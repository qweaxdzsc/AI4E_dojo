"""独立 FP64 完整场指标；不导入 Dojo 或信任候选提供的真值。"""

from pathlib import Path

import numpy as np

from .io import digest, inside, read_json, write_json


def evaluate_arrays(predictions, targets):
    """按实例 ID 比对二维时空场，返回固定口径指标；坏样本整批拒绝。"""
    if not targets or set(predictions) != set(targets):
        raise ValueError("预测实例必须与评价名单完全一致")
    rows = []
    for sample_id in sorted(targets):
        prediction = np.asarray(predictions[sample_id], dtype=np.float64)
        target = np.asarray(targets[sample_id], dtype=np.float64)
        if prediction.shape != target.shape or target.ndim != 2 or not target.size:
            raise ValueError(f"{sample_id}: 时空场形状不匹配")
        if not np.isfinite(prediction).all() or not np.isfinite(target).all():
            raise ValueError(f"{sample_id}: 非有限值")
        norm = np.linalg.norm(target)
        if norm == 0 or np.linalg.norm(target[0]) == 0:
            raise ValueError(f"{sample_id}: 零真值范数不可评价")
        error = prediction - target
        rows.append(
            {
                "sample_id": sample_id,
                "relative_l2": float(np.linalg.norm(error) / norm),
                "mae": float(np.abs(error).mean()),
                "l2": float(np.linalg.norm(error)),
                "max_error": float(np.abs(error).max()),
                "initial_relative_l2": float(np.linalg.norm(error[0]) / np.linalg.norm(target[0])),
                "predicted_to_true_norm": float(np.linalg.norm(prediction) / norm),
                "time_relative_l2": float(
                    np.mean(
                        np.linalg.norm(error, axis=1) / (np.linalg.norm(target, axis=1) + 1e-12)
                    )
                ),
            }
        )
    errors = [r["relative_l2"] for r in rows]
    result = {
        "status": "complete",
        "sample_count": len(rows),
        "precision": "float64",
        "final_mean_relative_l2": float(np.mean(errors)),
        "per_sample_relative_l2": {r["sample_id"]: r["relative_l2"] for r in rows},
        "std_relative_l2": float(np.std(errors, ddof=0)),
        "median_relative_l2": float(np.median(errors)),
        "p90_relative_l2": float(np.quantile(errors, 0.9, method="linear")),
        "max_relative_l2": float(max(errors)),
        "samples": rows,
    }
    for key in (
        "mae",
        "l2",
        "max_error",
        "initial_relative_l2",
        "predicted_to_true_norm",
        "time_relative_l2",
    ):
        result[f"mean_{key}"] = float(np.mean([r[key] for r in rows]))
    return result


def evaluate(prediction_manifest, truth_manifest, output):
    """消费 NPY 清单并验证内容摘要；真值清单必须来自主会话冻结材料。"""
    manifests = [Path(prediction_manifest), Path(truth_manifest)]
    groups = []
    for manifest in manifests:
        content = read_json(manifest)
        records = content["samples"]
        if len(records) != 10 or len({r["id"] for r in records}) != 10:
            raise ValueError("正式评价必须恰好有 10 个不同实例")
        arrays = {}
        for record in records:
            path = inside(manifest.parent, record["path"])
            if digest(path) != record["sha256"]:
                raise ValueError(f"产物摘要不匹配: {record['id']}")
            value = np.load(path, allow_pickle=False)
            if value.shape != (128, 128):
                raise ValueError("正式评价要求原始 128×128 时空网格")
            arrays[record["id"]] = value
        groups.append(arrays)
    result = evaluate_arrays(*groups)
    result["prediction_manifest_sha256"] = digest(manifests[0])
    result["truth_manifest_sha256"] = digest(manifests[1])
    result["evaluator_sha256"] = digest(Path(__file__))
    write_json(output, result)
    return result
