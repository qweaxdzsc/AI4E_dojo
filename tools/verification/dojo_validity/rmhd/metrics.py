"""纯 NumPy FP64 可信评分；不导入候选代码，不混合六场量纲。"""

import numpy as np

from .protocol import FIELDS


def field_errors(prediction, target, history_last=None):
    """一个窗口 [40,6,R,Z] 的逐场全场误差；坏样本不允许删去。"""
    p, y = np.asarray(prediction, dtype=np.float64), np.asarray(target, dtype=np.float64)
    if p.shape != y.shape or p.ndim != 4 or p.shape[:2] != (40, 6):
        raise ValueError("预测必须与真值同形状 [40,6,R,Z]")
    if not np.isfinite(p).all() or not np.isfinite(y).all():
        raise ValueError("非有限预测或真值")
    axes = (0, 2, 3)
    norm = np.sqrt(np.sum(y * y, axis=axes))
    if np.any(norm == 0):
        raise ValueError("完整场真值零范数，不可评价")
    error = p - y
    absolute = np.sqrt(np.sum(error * error, axis=axes))
    result = {
        "relative_l2": (absolute / norm).tolist(),
        "l2": absolute.tolist(),
        "mae": np.mean(np.abs(error), axis=axes).tolist(),
        "max_error": np.max(np.abs(error), axis=axes).tolist(),
        "per_frame_relative_l2": (
            np.sqrt(np.sum(error * error, axis=(2, 3)))
            / (np.sqrt(np.sum(y * y, axis=(2, 3))) + 1e-12)
        ).tolist(),
    }
    if history_last is not None:
        change = y - np.asarray(history_last, dtype=np.float64)[None]
        change_norm = np.sqrt(np.sum(change * change, axis=axes))
        result["change_relative_l2"] = [
            float(a / b) if b > 0 else None for a, b in zip(absolute, change_norm, strict=True)
        ]
    return result


def aggregate(rows, expected_ids, starts=(0, 80, 161)):
    """按轨迹/窗口/字段等权复算，并强制检查完整身份集合。"""
    expected = {(i, s) for i in expected_ids for s in starts}
    actual = [(r["id"], r["start"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("窗口缺失、重复或包含非预期样本")
    values = np.array([r["relative_l2"] for r in rows], dtype=np.float64)
    if values.shape != (len(expected), 6) or not np.isfinite(values).all():
        raise ValueError("非法逐场指标")
    windows = values.mean(axis=1)
    return {
        "mean_field_relative_l2": float(values.mean()),
        "per_field_relative_l2": dict(zip(FIELDS, values.mean(axis=0).tolist(), strict=True)),
        "std_relative_l2": float(windows.std()),
        "median_relative_l2": float(np.median(windows)),
        "p90_relative_l2": float(np.quantile(windows, 0.90, method="linear")),
        "max_relative_l2": float(windows.max()),
        "mean_mae": np.mean([r["mae"] for r in rows], axis=0).tolist(),
        "mean_l2": np.mean([r["l2"] for r in rows], axis=0).tolist(),
        "mean_max_error": np.mean([r["max_error"] for r in rows], axis=0).tolist(),
        "rows": rows,
    }
