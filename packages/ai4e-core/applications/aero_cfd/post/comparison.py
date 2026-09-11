"""跨独立运行比较；严格对齐样本和原点，几何计算交给能力。"""

import json
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.eval.physical import PhysicalMetrics
from ai4e_core.abilities.postproc.comparison import (
    attach_valid_mesh,
    cut_plane,
    surface,
    write_polydata,
)


def align(left, right) -> np.ndarray:
    """稳定 ID 重排，不允许用不同点子集或不同物理真值比较。"""
    a, b = np.asarray(left), np.asarray(right)
    if a.ndim != 1 or b.ndim != 1 or len(np.unique(a)) != len(a) or len(np.unique(b)) != len(b):
        raise ValueError("比较点身份必须是一维唯一 ID")
    order = np.argsort(b)
    positions = np.searchsorted(b[order], a)
    if (
        len(a) != len(b)
        or (positions >= len(b)).any()
        or not np.array_equal(b[order[positions]], a)
    ):
        raise ValueError("两模型没有覆盖同一完整点集")
    return order[positions]


def compare(
    left_path,
    right_path,
    *,
    domain,
    output,
    dataset_component,
    config,
    cuts,
    labels=("left", "right"),
    visual_count=3,
):
    """逐样本生成指标和前三样本图形数据，来源不符即失败。"""
    if len(labels) != 2 or len(set(labels)) != 2 or "truth" in labels:
        raise ValueError("比较需要两个不同的模型显示名")
    left, right = [json.loads(Path(p).read_text()) for p in (left_path, right_path)]
    for report in (left, right):
        if report["status"] != "succeeded":
            raise ValueError("不能把部分预测报告标为完整比较")
    a, b = left["protocol"], right["protocol"]
    for protocol in (a, b):
        if not all(protocol.get(key) for key in ("weights", "preparation", "model", "digest")):
            raise ValueError("比较缺少权重、准备或模型来源")
        if fingerprint({k: v for k, v in protocol.items() if k != "digest"}) != protocol["digest"]:
            raise ValueError("比较来源协议摘要不一致")
    if any(a[k] != b[k] for k in ("dataset", "samples", "split", "execution")):
        raise ValueError("数据、样本或执行精度设备不同，不能进行本次模型比较")
    output = Path(output)
    progress = {
        "status": "running",
        "domain": domain,
        "samples": a["samples"],
        "completed": [],
        "sources": [str(left_path), str(right_path)],
        "visuals": [],
        "models": list(labels),
    }
    destination = output / "comparison.json"
    save_json(destination, progress)
    totals = [PhysicalMetrics(), PhysicalMetrics()]
    try:
        lookups = [
            {item["sample"]: item["manifest"] for item in report["results"]}
            for report in (left, right)
        ]
        if any(set(lookup) != set(a["samples"]) for lookup in lookups):
            raise ValueError("预测报告缺样本或存在重复样本")
        for index, name in enumerate(a["samples"]):
            paths = [Path(lookup[name]) for lookup in lookups]
            manifests = [json.loads(path.read_text()) for path in paths]
            if any(
                m["protocol"] != report["protocol"]["digest"]
                for m, report in zip(manifests, (left, right), strict=True)
            ):
                raise ValueError(f"{name}: 预测来源不匹配")
            desc = [m["domains"][domain] for m in manifests]
            if (
                desc[0]["targets"] != desc[1]["targets"]
                or desc[0]["identity_basis"] != desc[1]["identity_basis"]
            ):
                raise ValueError(f"{name}: 域字段或身份基础不一致")
            tensors = [
                {
                    k: torch.load(path.parent / v, weights_only=True).numpy()
                    for k, v in m["filemap"].items()
                }
                for path, m in zip(paths, manifests, strict=True)
            ]
            rows = align(tensors[0][desc[0]["ids"]], tensors[1][desc[1]["ids"]])
            points = tensors[0][desc[0]["position"]]
            if not np.array_equal(points, tensors[1][desc[1]["position"]][rows]):
                raise ValueError(f"{name}: 相同点 ID 的物理坐标变化")
            metrics, arrays = [PhysicalMetrics(), PhysicalMetrics()], {}
            for field, key in desc[0]["targets"].items():
                truth = tensors[0][key + ".truth"]
                if not np.array_equal(truth, tensors[1][key + ".truth"][rows]):
                    raise ValueError(f"{name}/{field}: 物理真值不一致")
                predictions = [
                    tensors[0][key + ".prediction"],
                    tensors[1][key + ".prediction"][rows],
                ]
                for i, pred in enumerate(predictions):
                    metrics[i].update(field, pred, truth)
                    totals[i].update(field, pred, truth)
                # 向量展示模长；误差为模长误差，组件指标仍独立保留。
                shown = [
                    np.linalg.norm(v, axis=1) if v.shape[1] > 1 else v[:, 0]
                    for v in [truth, *predictions]
                ]
                for label, value in zip(("truth", *labels), shown, strict=True):
                    arrays[field + "." + label] = value
                arrays[field + "." + labels[0] + "_error"] = np.abs(shown[1] - shown[0])
                arrays[field + "." + labels[1] + "_error"] = np.abs(shown[2] - shown[0])
            item = {
                "sample": name,
                "metrics": {labels[i]: metrics[i].finalize() for i in range(2)},
            }
            if index < visual_count:
                mesh = dataset_component.comparison_mesh(config, name, domain, points)
                mesh = attach_valid_mesh(
                    mesh,
                    points,
                    arrays,
                    source_ids=(
                        tensors[0][desc[0]["ids"]]
                        if desc[0]["identity_basis"] == "source"
                        else None
                    ),
                )
                folder = output / f"sample-{index}"
                if domain == "surface":
                    path = folder / "surface.vtp"
                    write_polydata(path, surface(mesh))
                    progress["visuals"].append(
                        {
                            "sample": name,
                            "kind": "surface",
                            "path": str(path),
                            "fields": list(desc[0]["targets"]),
                            "field_labels": {
                                field: field + " magnitude"
                                if tensors[0][key + ".truth"].shape[1] > 1
                                else field
                                for field, key in desc[0]["targets"].items()
                            },
                            "view_up": getattr(dataset_component, "VIEW_UP", [0, 0, 1]),
                        }
                    )
                for cut in cuts:
                    geometry, metadata = cut_plane(mesh, axis=cut["axis"], fraction=cut["fraction"])
                    path = folder / f"cut-{cut['axis']}-{cut['fraction']}.vtp"
                    write_polydata(path, geometry)
                    progress["visuals"].append(
                        {
                            "sample": name,
                            "kind": "curve" if domain == "surface" else "slice",
                            "path": str(path),
                            "fields": list(desc[0]["targets"]),
                            "field_labels": {
                                field: field + " magnitude"
                                if tensors[0][key + ".truth"].shape[1] > 1
                                else field
                                for field, key in desc[0]["targets"].items()
                            },
                            **metadata,
                            "span_fraction": cut.get("span_fraction"),
                        }
                    )
            progress["completed"].append(item)
            save_json(destination, progress)
        progress.update(
            status="succeeded",
            metrics={labels[i]: totals[i].finalize() for i in range(2)},
        )
        save_json(destination, progress)
        return progress
    except BaseException as exc:
        progress.update(status="failed", error={"type": type(exc).__name__, "message": str(exc)})
        save_json(destination, progress)
        raise
