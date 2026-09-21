"""地热固定结果读回及误差统计；不加载网络或重新预测。"""

import json
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.eval.relative_field import errors


def read_results(path):
    """核对清单和每个结果内容；扩展数组也按声明读回。"""
    path = Path(path)
    record = json.loads(path.read_text())
    if record.get("version") != 1 or record.get("kind") != "results" or not record["samples"]:
        raise ValueError("结果清单不完整")
    arrays = []
    for sample in record["samples"]:
        file = path.parent / sample["file"]
        if Path(sample["file"]).name != sample["file"] or digest(file) != sample["sha256"]:
            raise ValueError("结果文件变化或越界")
        arrays.append(torch.load(file, map_location="cpu", weights_only=False))
    record = dict(record)
    record["derived_values"] = {}
    for name, item in record.get("derived", {}).items():
        file = path.parent / item["file"]
        if Path(item["file"]).name != item["file"] or digest(file) != item["sha256"]:
            raise ValueError("派生数组变化或越界")
        value = np.load(file, allow_pickle=False)
        if item["sample_ids"] != [s["id"] for s in record["samples"]] or value.shape[0] != len(
            arrays
        ):
            raise ValueError("派生数组样本身份不匹配")
        if not item.get("unit") or not np.isfinite(value).all():
            raise ValueError("派生数组单位缺失或含非有限值")
        record["derived_values"][name] = value
    return record, arrays


def evaluate_results(record, arrays):
    """第1—20年逐例评价后按例等权；无独立真值不输出精度。"""
    per_case = []
    if record["truth_available"]:
        for item in arrays:
            truth = item["truth"]
            metrics = {
                field: errors(item[key][..., 1:], truth[field][..., 1:])
                for key, field in [("Pres", "pres"), ("Temp", "temp")]
            }
            metrics.update(
                {
                    field: errors(item[key][0], truth[field][0])
                    for key, field in [("Twh", "Temp_wh"), ("Hwh", "Heat_wh"), ("Pinj", "P_inj")]
                }
            )
            per_case.append(metrics)
    mean = (
        {
            field: {
                metric: sum(row[field][metric] for row in per_case) / len(per_case)
                for metric in ["mae", "rmse", "mare"]
            }
            for field in per_case[0]
        }
        if per_case
        else None
    )
    derived = {}
    for name, values in record.get("derived_values", {}).items():
        value = np.asarray(values, dtype=float)
        if not np.isfinite(value).all():
            raise ValueError("派生统计含非有限值")
        derived[name] = {"mean": float(value.mean()), "count": int(value.size)}
    return {
        "scope": record["scope"],
        "samples": len(arrays),
        "per_case": per_case,
        "mean": mean,
        "derived": derived,
        "years": [1, 20],
        "well_counts": [
            {"production": len(a["Twh"][0]), "injection": len(a["Pinj"][0])} for a in arrays
        ],
        "aggregation": "equal cases; equal wells and years within each case",
    }
