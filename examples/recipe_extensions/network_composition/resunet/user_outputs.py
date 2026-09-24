"""用户派生输出：计算普通数组，持久化与运行记录由研究步骤承担。"""

from collections.abc import Mapping

import numpy as np


def derive(arrays: Mapping[str, np.ndarray], metadata: dict) -> tuple[dict, dict]:
    """末轴通道预测的向量范数，返回新增数组及单位/实体/mask声明。

    metadata可显式提供unit、entity、mask引用；单位未声明则保留unknown。
    不改变原预测、身份或有效性，不将无效区转成真实标签。
    """
    if "prediction" not in arrays:
        raise ValueError("缺少prediction数组")
    prediction = np.asarray(arrays["prediction"])
    if prediction.ndim < 2 or prediction.dtype.kind != "f":
        raise ValueError("派生输出需要末轴通道的浮点预测")
    value = np.linalg.norm(prediction, axis=-1, keepdims=True)
    return {"prediction_norm": value}, {
        "prediction_norm": {
            "unit": metadata.get("unit", "unknown"),
            "entity": metadata.get("entity", "prediction"),
            "mask": metadata.get("mask", "valid"),
        }
    }


def consume(arrays: Mapping[str, np.ndarray], declarations: dict) -> dict:
    """读回派生数组，检查声明和有效域有限性，返回JSON形状摘要。"""
    if "prediction_norm" not in arrays or "prediction_norm" not in declarations:
        raise ValueError("缺少派生数组或声明prediction_norm")
    value = np.asarray(arrays["prediction_norm"])
    declaration = declarations["prediction_norm"]
    if not {"unit", "entity", "mask"} <= set(declaration) or not value.size:
        raise ValueError("派生声明不完整或数组为空")
    valid = arrays.get(declaration["mask"]) if isinstance(declaration["mask"], str) else None
    checked = value
    if valid is not None:
        mask = np.asarray(valid, dtype=bool)
        if mask.shape == value.shape[:-1]:
            mask = mask[..., None]
        if mask.shape != value.shape:
            raise ValueError("派生数组与有效域形状不一致")
        checked = value[mask]
    if not checked.size or not np.isfinite(checked).all():
        raise ValueError("派生有效域为空或含非有限值")
    return {
        "prediction_norm": {"shape": list(value.shape), "finite": True, "unit": declaration["unit"]}
    }
