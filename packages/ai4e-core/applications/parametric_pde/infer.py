"""独立后处理：检查点核验、全网格预测与逐实例指标。"""

from pathlib import Path

import torch

from ai4e_core.abilities.data.save.bundle import file_digest, save_bundle, save_json

from .contracts import open_preparation, read_prepared
from .model import build_model
from .train import training_contract


def infer(cfg, *, dataset_component, model_component, session):
    """独立恢复权重，输出所有 test 预测；失败保留部分交付状态。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])
    path, prepared = open_preparation(cfg, dataset, model_component)
    if not cfg["post"]["checkpoint"]:
        raise ValueError("infer 需要明确 checkpoint 输入")
    checkpoint = Path(cfg["post"]["checkpoint"])
    root = Path(cfg["post"]["output"])
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"预测输出必须为新目录: {root}")
    if session.dry_run:
        session.report({"status": "checked", "checkpoint": str(checkpoint)}, stage="infer")
        return None
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if state["contract"] != training_contract(cfg, prepared, model_component):
        raise ValueError("检查点与物理数据、模型或训练协议不一致")
    model = build_model(cfg, model_component)
    model.load_state_dict(state["model"], strict=True)
    model.eval()
    report = {
        "status": "running",
        "checkpoint": str(checkpoint),
        "epoch": state["epoch"],
        "checkpoint_sha256": file_digest(checkpoint),
        "dataset_identity": dataset.manifest["content_id"],
        "samples": [],
    }
    try:
        with torch.no_grad():
            for record in prepared["samples"]:
                if record["split"] != "test":
                    continue
                batch = read_prepared(path, record)
                prediction = model_component.predictions(model, batch, cfg)["u"].cpu()
                truth = batch["sample"]["u"].to(prediction)
                error = prediction - truth
                norm = float(truth.norm())
                metrics = {
                    "mae": float(error.abs().mean()),
                    "l2": float(error.norm()),
                    "relative_l2": float(error.norm()) / norm if norm else None,
                    "max_error": float(error.abs().max()),
                }
                # 数据契约首轴为时间；与整体时空相对 L2 分开报告，不能互换。
                time_error = error.double().flatten(1).norm(dim=1)
                time_norm = truth.double().flatten(1).norm(dim=1)
                metrics["mean_time_relative_l2"] = float((time_error / (time_norm + 1e-12)).mean())
                save_bundle(
                    root / f"{record['id']}.pt",
                    {
                        "sample_id": record["id"],
                        "axes": batch["sample"]["axes"],
                        "mapping": batch["sample"]["mapping"],
                        "prediction": prediction,
                        "target": truth,
                        "metrics": metrics,
                    },
                )
                report["samples"].append(
                    {
                        "id": record["id"],
                        **metrics,
                        "sha256": file_digest(root / f"{record['id']}.pt"),
                    }
                )
                session.artifact("inference-progress.json", report)
    except Exception as exc:
        report.update(status="partial_failure", error=str(exc))
        session.artifact("inference-progress.json", report)
        session.report(report, stage="infer")
        raise
    if not report["samples"]:
        report.update(status="failed", error="没有测试实例")
        session.artifact("inference-progress.json", report)
        raise ValueError(report["error"])
    report["status"] = "complete"
    relative = [r["relative_l2"] for r in report["samples"] if r["relative_l2"] is not None]
    report["relative_l2_valid_samples"] = len(relative)
    report["mean_relative_l2"] = sum(relative) / len(relative) if relative else None
    report["mean_time_relative_l2"] = sum(
        r["mean_time_relative_l2"] for r in report["samples"]
    ) / len(report["samples"])
    report["time_relative_l2_definition"] = (
        "mean_samples(mean_time(norm_spatial(pred-target)/(norm_spatial(target)+1e-12)))"
    )
    save_json(root / "predictions.json", report)
    session.artifact("inference-progress.json", report)
    session.report(report, stage="infer")
    session.record_asset(
        "results", root / "predictions.json", kind="other", stage="infer", dependencies=[root]
    )
    return {**report, "results": str(root / "predictions.json")}


def predict_fields(
    model,
    preparation,
    output,
    *,
    split,
    batch,
    input_names,
    decode,
    batch_size,
    fields,
    units,
    times,
    provenance,
    derived=None,
):
    """交付固定物理预测、真值、拓扑和派生数组；后处理无需模型或原数据。"""
    from pathlib import Path

    import numpy as np
    import pyvista as pv

    from ai4e_core.abilities.data.save.array_manifest import digest, save_arrays
    from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf
    from ai4e_core.abilities.inference.prediction import predict_named_batches
    from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs

    record, arrays = read_field_inputs(preparation, split)
    prediction = predict_named_batches(
        model,
        len(arrays["target"]),
        batch,
        input_names=input_names,
        decode=decode,
        batch_size=batch_size,
    ).numpy()
    result = {
        "prediction": prediction,
        "target": arrays["physical_target"],
        "coordinates": arrays["coordinates"],
        "entity_ids": arrays["entity_ids"],
        "faces": arrays["faces"],
    }
    descriptions = {}
    if derived:
        extra, descriptions = derived(result)
        if set(extra) & set(result) or set(extra) != set(descriptions):
            raise ValueError("派生数组声明缺失或覆盖固定结果")
        for name, value in extra.items():
            if value.shape[0] != prediction.shape[0] or set(descriptions[name]) != {
                "units",
                "axes",
            }:
                raise ValueError("派生数组身份或语义缺失")
        result.update(extra)
    root = Path(output)
    # save_arrays 拒绝已存在目录，所以先在完整新结果目录写数组再追加网格。
    manifest = save_arrays(
        root,
        result,
        kind="named-field-result-v1",
        metadata={
            "ids": record["metadata"]["ids"],
            "split": split,
            "fields": fields,
            "units": units,
            "times": times,
            "provenance": provenance,
            "derived": descriptions,
        },
    )
    # 网格也成功后才发布完整清单；失败时仅留下未完成数据，不可被 post 消费。
    pending = Path(manifest).with_name("manifest.pending.json")
    Path(manifest).replace(pending)
    meshes = []
    for i, identity in enumerate(record["metadata"]["ids"]):
        coords = arrays["coordinates"][i]
        if coords.shape[-1] == 2:
            coords = np.pad(coords, ((0, 0), (0, 1)))
        mesh = pv.PolyData(coords, arrays["faces"][i])
        mesh.point_data["source_point_id"] = arrays["entity_ids"][i]
        for j, time in enumerate(times):
            for k, name in enumerate(fields):
                mesh.point_data[f"{name}_prediction_frame{j:03d}"] = prediction[i, j, :, k]
                mesh.point_data[f"{name}_truth_frame{j:03d}"] = arrays["physical_target"][
                    i, j, :, k
                ]
        path = write_vtkhdf(root / "meshes" / f"{identity}.vtkhdf", mesh)
        meshes.append({"path": str(path.relative_to(root)), "sha256": digest(path)})
    import json

    from ai4e_core.abilities.data.save.arrays import save_json

    final = json.loads(pending.read_text())
    final["metadata"]["meshes"] = meshes
    save_json(manifest, final)
    pending.unlink()
    return manifest
