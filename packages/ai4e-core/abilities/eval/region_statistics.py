"""有效区域的实体等权统计，不推断面积或体积权重。"""

from __future__ import annotations

from typing import Any

import numpy as np


def region_statistics(
    values: Any, *, mask: Any = None, region: Any = "whole", interpolation: str | None = None
) -> dict:
    """统计标量数组；空有效域拒绝，标准差使用总体口径。"""
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 1:
        raise ValueError("区域统计需要已选择分量的一维数组")
    total = len(values)
    if mask is not None:
        valid = np.asarray(mask)
        if valid.dtype != np.bool_ or valid.shape != values.shape:
            raise ValueError("统计 mask 必须逐实体布尔声明")
        values = values[valid]
    if not len(values) or not np.isfinite(values).all():
        raise ValueError("统计区域为空或含非有限值")
    return {
        "count": len(values),
        "excluded": total - len(values),
        "min": float(values.min()),
        "max": float(values.max()),
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "median": float(np.median(values)),
        "p90": float(np.quantile(values, 0.9)),
        "region": region,
        "interpolation": interpolation,
        "weighting": "equal_entity",
    }
