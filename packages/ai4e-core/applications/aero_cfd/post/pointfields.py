"""全表面点场后处理装配：推理、数值结果、网格与指标分别提交。"""

import csv
import hashlib
import json
import random
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json, save_npy
from ai4e_core.abilities.data.validate.fingerprint import (
    file_fingerprint,
    fingerprint,
    source_fingerprint,
)
from ai4e_core.abilities.eval.field_totals import FieldTotals
from ai4e_core.abilities.inference.stream import predict_stream
from ai4e_core.abilities.postproc.export.field_surface import write_h5, write_vtp
from ai4e_core.abilities.postproc.surface_geometry import surface_area_ratio
from ai4e_core.abilities.sampling.stride import reconstruct
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.post.stage import resolve_checkpoint
from ai4e_core.applications.aero_cfd.trainprep.pointfields import features, open_preparation
from ai4e_core.base.events import sample_context


def select(available, samples=None, *, all_samples=False):
    """显式全量与指定名单互斥；默认只选择一个随机样本。"""
    if not available or (samples is not None and all_samples):
        raise ValueError("样本为空或选择方式冲突")
    selected = (
        list(available)
        if all_samples
        else list(samples)
        if samples is not None
        else [random.SystemRandom().choice(available)]
    )
    if not selected or len(selected) != len(set(selected)) or set(selected) - set(available):
        raise ValueError("选择为空、重复或不属于目标分片")
    return selected


def complete(directory, identity, count, parts, width=4):
    """验证实际预测内容；同形状但旧权重的文件不可复用。"""
    try:
        marker = json.loads((directory / ".commit.json").read_text())
        if marker["identity"] != identity:
            return False
        expected = {f"prediction_part{i}.npy" for i in range(parts)} | {"metadata.json"}
        if set(marker["files"]) != expected:
            return False
        for name, digest in marker["files"].items():
            if file_fingerprint(directory / name) != digest:
                return False
        for i in range(parts):
            array = np.load(directory / f"prediction_part{i}.npy", allow_pickle=False)
            if array.shape != (len(range(i, count, parts)), width) or not np.isfinite(array).all():
                return False
        return True
    except (OSError, ValueError, KeyError):
        return False


def _full(view, split, item):
    """从数据组件恢复几何、真值与原始顺序，不识别其存储文件名。"""
    blocks = [view.read(split, item, selection=i) for i in range(view.describe()["chunk_count"])]
    result = {
        field: reconstruct([b[field] for b in blocks], view.describe()["point_count"])
        for field in ("points", "normals", "area", "labels")
    }
    result["conditions"], result["metadata"] = blocks[0]["conditions"], blocks[0]["metadata"]
    return result


def metrics_stem(selected, all_samples):
    """按原选择顺序生成指标文件名，避免不同样本子集相互覆盖。"""
    if all_samples:
        return "metrics"
    if len(selected) == 1:
        return f"metrics_{selected[0]}"
    return "metrics_selected_" + hashlib.sha256("\n".join(selected).encode()).hexdigest()[:10]


def preflight(root, output, inferred, selected, settings):
    """干跑与提交共用已有目标检查；恢复模式只授权重新计算合法来源。"""
    if settings.get("overwrite") or settings.get("resume"):
        return
    if settings.get("infer", True):
        for name in inferred:
            directory = root / name
            if directory.exists() and any(directory.iterdir()):
                raise FileExistsError(f"预测目录非空: {directory}")
    for name in selected:
        for enabled, suffix in (
            (settings.get("export_hdf5", True), ".h5"),
            (settings.get("export_vtk", True), ".vtp"),
        ):
            if enabled and (output / (name + suffix)).exists():
                raise FileExistsError(output / (name + suffix))
    if settings.get("evaluate", True) and selected:
        stem = metrics_stem(selected, settings.get("all_samples", False))
        for suffix in (".json", ".csv"):
            if (output / (stem + suffix)).exists():
                raise FileExistsError(output / (stem + suffix))


def execute(config, data_component, model_component, run):
    """独立恢复权重并按声明执行操作，所有失败保留已提交记录。"""
    settings = config["post"]
    split = settings.get("split", "test")
    if split not in {"test", "validation"}:
        raise ValueError("后处理只支持独立验证或测试分片")
    infer = settings.get("infer", True)
    evaluate = settings.get("evaluate", True)
    export_h5 = settings.get("export_hdf5", True)
    export_vtk = settings.get("export_vtk", True)
    if not any((infer, evaluate, export_h5, export_vtk)):
        raise ValueError("后处理没有启用操作")
    view, normalization, prepared = open_preparation(
        config, data_component, config["train"].get("preparation"), validate=False
    )
    checkpoint = resolve_checkpoint(settings.get("checkpoint") or "best", run.run_dir)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if (
        state.get("version") != 2
        or state.get("contract", {}).get("preparation") != prepared["digest"]
    ):
        raise ValueError("检查点与数据、模型或准备契约冲突")
    available = view.partitions[split]
    inferred = select(
        available,
        settings.get("inference_samples"),
        all_samples=settings.get("inference_samples") is None,
    )
    selected = (
        select(available, settings.get("samples"), all_samples=settings.get("all_samples", False))
        if any((evaluate, export_h5, export_vtk))
        else []
    )
    root = Path(config["paths"]["datasets"]["predictions"]) / split
    output = Path(config["paths"]["datasets"]["post"]) / split
    weights = fingerprint(state["model"])
    identity = fingerprint({"preparation": prepared["digest"], "weights": weights, "split": split})
    identity = fingerprint(
        {
            "inputs": identity,
            "component": model_component.SOURCE,
            "source": source_fingerprint(Path(model_component.__file__).parent),
            "precision": config["train"]["precision"],
            "device": config["train"]["device"],
            "torch": torch.__version__,
        }
    )
    width = len(view.describe()["fields"]["labels"])
    if run.dry_run:
        preflight(root, output, inferred, selected, settings)
        return {
            "mode": "post_check",
            "checkpoint": str(checkpoint),
            "predictions": inferred,
            "outputs": selected,
        }
    progress = PostProgress(
        run,
        {"predictions": infer, "evaluation": evaluate, "results": export_h5, "mesh": export_vtk},
    )
    protocol = {
        "version": 1,
        "dataset": prepared["dataset"],
        "weights": weights,
        "normalization": normalization.record,
        "model": state["contract"]["component"],
        "split": split,
        "selected_samples": selected,
        "inputs": [],
    }
    progress.protocol = protocol
    for key, record in progress.report["operations"].items():
        record["expected"] = len(inferred) if key == "predictions" else len(selected)
    overwrite, resume = settings.get("overwrite", False), settings.get("resume", False)
    try:
        preflight(root, output, inferred, selected, settings)
        progress.publish()
        if infer:
            device = resolve_device(config["train"]["device"])
            model = model_component.construct(**config["model"]["parameters"]).to(device).float()
            model.load_state_dict(state["model"], strict=True)
            with progress.operation("predictions"):
                for name in inferred:
                    item = available.index(name)
                    directory = root / name
                    with progress.unit([{"sample_id": name, "index": item, "partition": split}]):
                        sample_identity = fingerprint({"run": identity, "sample": name})
                        if resume and complete(
                            directory,
                            sample_identity,
                            view.describe()["point_count"],
                            view.describe()["chunk_count"],
                            width,
                        ):
                            progress.committed(directory / "metadata.json")
                            continue
                        if (
                            directory.exists()
                            and any(directory.iterdir())
                            and not (overwrite or resume)
                        ):
                            raise FileExistsError(f"预测目录非空: {directory}")
                        (directory / ".commit.json").unlink(missing_ok=True)
                        (directory / "metadata.json").unlink(missing_ok=True)

                        def chunks(item=item, name=name):
                            for part in range(view.describe()["chunk_count"]):
                                raw = view.read(
                                    split, item, selection=part, fields=("points", "normals")
                                )
                                yield (
                                    {"sample": name, "part": part},
                                    {
                                        "features": torch.from_numpy(features(raw, normalization))[
                                            None
                                        ]
                                    },
                                )

                        paths = []
                        for meta, result in predict_stream(
                            model, chunks, factory=model_component.SurfaceInference
                        ):
                            array = normalization.inverse(result["fields"].squeeze(0).cpu().numpy())
                            expected = len(
                                range(
                                    meta["part"],
                                    view.describe()["point_count"],
                                    view.describe()["chunk_count"],
                                )
                            )
                            if array.shape != (expected, width) or not np.isfinite(array).all():
                                raise ValueError("预测块形状错误或非有限")
                            path = directory / f"prediction_part{meta['part']}.npy"
                            save_npy(path, array)
                            paths.append(path)
                            progress.committed(path)
                        metadata_path = directory / "metadata.json"
                        save_json(
                            metadata_path,
                            {
                                "sample_id": name,
                                "split": split,
                                "point_count": view.describe()["point_count"],
                                "chunk_count": view.describe()["chunk_count"],
                                "manifest_fingerprint": view.describe()["fingerprint"],
                                "checkpoint_epoch": state["epoch"] - 1,
                            },
                        )
                        paths.append(metadata_path)
                        save_json(
                            directory / ".commit.json",
                            {
                                "identity": sample_identity,
                                "files": {p.name: file_fingerprint(p) for p in paths},
                            },
                        )
                        progress.committed(metadata_path)
        topology = (
            data_component.reconstruct_surface_topology(Path(config["dataset"]["connectivity_h5"]))
            if export_vtk
            else None
        )
        if topology is not None and topology.point_count != view.describe()["point_count"]:
            raise ValueError("网格与样本点数不一致")
        labels = view.describe()["fields"]["labels"]
        condition_names = view.describe()["fields"]["conditions"]
        aggregate, metrics, rows = FieldTotals(labels), {}, []
        for name in selected:
            item = available.index(name)
            directory = root / name
            with sample_context(
                "后处理输入", [{"sample_id": name, "index": item, "partition": split}]
            ):
                if not complete(
                    directory,
                    fingerprint({"run": identity, "sample": name}),
                    view.describe()["point_count"],
                    view.describe()["chunk_count"],
                    width,
                ):
                    raise ValueError(f"预测缺失、权重或数据身份不一致: {name}")
                full = _full(view, split, item)
                prediction = reconstruct(
                    [
                        np.load(directory / f"prediction_part{i}.npy", allow_pickle=False)
                        for i in range(view.describe()["chunk_count"])
                    ],
                    view.describe()["point_count"],
                )
            truth = full["labels"]
            if evaluate:
                with (
                    progress.operation("evaluation"),
                    progress.unit([{"sample_id": name, "index": item, "partition": split}]),
                ):
                    acc = FieldTotals(labels)
                    acc.update(prediction, truth)
                    metric = acc.finalize()
                    aggregate.update(prediction, truth)
                    metrics[name] = metric
                    row = {"sample_id": name, "point_count": metric["point_count"]}
                    for key in ("mse", "mae", "relative_l2"):
                        row.update(
                            {f"{key}_{field}": value for field, value in metric[key].items()}
                        )
                        row[f"{key}_cf_magnitude"] = metric["cf_magnitude"][key]
                    rows.append(row)
            if export_h5:
                with (
                    progress.operation("results"),
                    progress.unit([{"sample_id": name, "index": item, "partition": split}]),
                ):
                    path = output / f"{name}.h5"
                    if path.exists() and not (overwrite or resume):
                        raise FileExistsError(path)
                    write_h5(
                        path,
                        arrays={
                            "coordinates": full["points"],
                            "normals": full["normals"],
                            "surface_area": full["area"],
                            "conditions": full["conditions"],
                            "truth": truth,
                            "prediction": prediction,
                            "error": prediction - truth,
                        },
                        attributes={
                            "sample_id": name,
                            "split": split,
                            **full["metadata"]["global_targets"],
                        },
                        field_names={
                            "conditions": condition_names,
                            "truth": labels,
                            "prediction": labels,
                        },
                    )
                    progress.committed(path)
            if export_vtk:
                with (
                    progress.operation("mesh"),
                    progress.unit([{"sample_id": name, "index": item, "partition": split}]),
                ):
                    path = output / f"{name}.vtp"
                    if path.exists() and not (overwrite or resume):
                        raise FileExistsError(path)
                    ratio = surface_area_ratio(topology, full["points"], full["area"])
                    if not 0.95 <= ratio <= 1.05:
                        raise ValueError(f"{name}: 网格面积比 {ratio} 不在 [0.95,1.05]")
                    write_vtp(
                        path,
                        topology=topology,
                        points=full["points"],
                        normals=full["normals"],
                        area=full["area"],
                        conditions=full["conditions"],
                        truth=truth,
                        prediction=prediction,
                        labels=labels,
                        condition_names=condition_names,
                    )
                    progress.committed(path)
        if evaluate:
            with progress.operation("evaluation"):
                stem = metrics_stem(selected, settings.get("all_samples", False))
                summary = {
                    "split": split,
                    "manifest_fingerprint": view.describe()["fingerprint"],
                    "sample_count": len(selected),
                    "selected_samples": selected,
                    "selection_mode": "all"
                    if settings.get("all_samples")
                    else "explicit"
                    if settings.get("samples") is not None
                    else "random_one",
                    "vtk_exported": export_vtk,
                    "topology": None
                    if topology is None
                    else {
                        "point_count": topology.point_count,
                        "triangle_count": len(topology.triangles),
                        "quad_count": len(topology.quads),
                        "face_count": topology.face_count,
                        "edge_count": topology.edge_count,
                        "euler_characteristic": topology.euler_characteristic,
                    },
                    "samples": metrics,
                    "aggregate": aggregate.finalize(),
                    "metrics_path": str(output / f"{stem}.json"),
                }
                save_json(output / f"{stem}.json", summary)
                progress.committed(output / f"{stem}.json")
                with (
                    atomic_path(output / f"{stem}.csv") as temporary,
                    temporary.open("w", newline="") as stream,
                ):
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                progress.committed(output / f"{stem}.csv")
                progress.report["evaluation"] = summary
        progress.finish()
        return progress.report
    except Exception as error:
        progress.finish(error)
        raise
