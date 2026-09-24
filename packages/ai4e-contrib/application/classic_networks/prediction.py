"""固定预测、有效域反变换与只读评价，训练代码不进入后处理。"""

from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.inference.prediction import predict_named_batches


def predict_fields(model, arrays, record, get_batch, output, *, derived=None, originals=None):
    """真实逐样本预测保留原输出布局，掩码独立于网络输出保存。"""
    case = record["metadata"]["case"]
    names = ("input", "valid") if case == "double_cylinder" else ("input", "valid", "coordinates")
    result = predict_named_batches(
        model,
        len(arrays["target"]),
        get_batch,
        input_names=names,
        decode=lambda raw, _: raw,
        batch_size=1,
    )
    result = result.numpy().reshape(arrays["target"].shape)
    stats = record["metadata"]["statistics"]["target"]
    result = result * np.asarray(stats["scale"]) + np.asarray(stats["mean"])
    valid = np.asarray(arrays["valid"], bool)
    result[~valid] = 0
    payload = {
        "prediction": result.astype(np.float32),
        "target": arrays["physical_target"],
        "valid": valid,
        "entity_ids": arrays["entity_ids"],
        "physical_input": arrays["physical_input"],
    }
    metadata = {**record["metadata"], "derived": {}}
    if originals is not None:
        from .shapenet_volume import back_project

        if len(originals) != len(result):
            raise ValueError("原网格与规则格样本数量不一致")
        projected = [
            back_project(coordinates[..., :3], prediction, mask, physical)
            for coordinates, prediction, mask, physical in zip(
                arrays["physical_input"], result, valid, originals, strict=True
            )
        ]
        payload.update(
            {
                "original_" + key: np.concatenate([item[key] for item in projected])
                for key in projected[0]
            }
        )
        payload["original_offsets"] = np.cumsum([0] + [len(item["valid"]) for item in projected])
        metadata["original_projection"] = "all-eight-grid-vertices-valid; original point order"
    if "times" in arrays:
        payload["times"] = arrays["times"]
    if derived is not None:
        additions, declarations = derived(payload, metadata)
        if set(additions) & set(payload) or set(additions) != set(declarations):
            raise ValueError("派生字段不能覆盖原字段且须声明单位与身份")
        payload.update(additions)
        metadata["derived"] = declarations
    return save_arrays(output, payload, kind="classic-results-v1", metadata=metadata)


def evaluate(results, output, *, consume=None):
    """独立读取固定结果，在有效域内按样本/分量分别评价。"""
    record, arrays = read_arrays(results, kind="classic-results-v1")
    rows = []
    for identity, prediction, target, mask in zip(
        record["metadata"]["ids"],
        arrays["prediction"],
        arrays["target"],
        arrays["valid"],
        strict=True,
    ):
        active = np.asarray(mask, bool)
        if not active.any():
            raise ValueError("固定结果没有有效评价点")
        p, t = prediction[active].astype(np.float64), target[active].astype(np.float64)
        difference = p - t
        norm = np.linalg.norm(t)
        rows.append(
            {
                "id": identity,
                "mse": float(np.mean(difference**2)),
                "mae": float(np.mean(np.abs(difference))),
                "relative_l2": float(np.linalg.norm(difference) / norm) if norm else None,
                "component_mse": np.mean(difference**2, axis=0).tolist(),
                "valid_count": int(active.sum()),
                "coverage": float(active.mean()),
            }
        )
    ratios = [r["relative_l2"] for r in rows if r["relative_l2"] is not None]
    report = {
        "case": record["metadata"]["case"],
        "rows": rows,
        "mse": float(np.mean([r["mse"] for r in rows])),
        "mean_relative_l2": float(np.mean(ratios)) if ratios else None,
        "fields": record["metadata"]["fields"],
        "units": record["metadata"]["units"],
        "scope": "small-data structural integration; no accuracy threshold",
    }
    if consume is not None:
        report["derived"] = consume(arrays, record["metadata"]["derived"])
    report["field_metrics"] = [
        {
            "field": field,
            "unit": "(" + unit + ")^2",
            "mse": float(np.mean([row["component_mse"][i] for row in rows])),
        }
        for i, (field, unit) in enumerate(zip(report["fields"], report["units"], strict=True))
    ]
    if "original_offsets" in arrays:
        original_rows = []
        offsets = arrays["original_offsets"]
        for index, identity in enumerate(record["metadata"]["ids"]):
            selection = slice(int(offsets[index]), int(offsets[index + 1]))
            mask = arrays["original_valid"][selection].astype(bool)
            if not mask.any():
                raise ValueError("回贴原网格没有有效评价点")
            prediction = arrays["original_prediction"][selection][mask].astype(np.float64)
            target = arrays["original_target"][selection][mask].astype(np.float64)
            error = prediction - target
            norm = np.linalg.norm(target)
            original_rows.append(
                {
                    "id": identity,
                    "total_count": len(mask),
                    "valid_count": int(mask.sum()),
                    "coverage": float(mask.mean()),
                    "component_mse": np.mean(error**2, axis=0).tolist(),
                    "relative_l2": float(np.linalg.norm(error) / norm) if norm else None,
                }
            )
        report["original_mesh"] = {
            "rows": original_rows,
            "scope": "valid interpolation support only",
        }
    save_json(Path(output) / "metrics.json", report)
    return report
