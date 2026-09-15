"""固定物理数组评价；不调用模型，不改变训练阶段的历史指标算术。"""

import numpy as np

from .catalog import METRICS


def evaluate_arrays(prediction, truth, *, component="scalar", mask=None, metrics=None):
    """在物理空间按有效实体计算；零分母返回不可定义而非伪造有限数。"""
    selected = ["mse", "rmse", "mae", "relative_l2", "r2"] if metrics is None else list(metrics)
    if not selected or set(selected) - METRICS.keys():
        raise ValueError("未知或空指标选择")
    p, t = np.asarray(prediction, dtype=np.float64), np.asarray(truth, dtype=np.float64)
    if p.shape != t.shape or p.ndim != 2 or not p.shape[1]:
        raise ValueError("预测和真值形状或分量不一致")
    total = len(p)
    if mask is not None:
        valid = np.asarray(mask)
        if valid.shape != (total,) or valid.dtype != np.bool_:
            raise ValueError("有效性声明必须逐实体提供布尔值")
        p, t = p[valid], t[valid]
    if not len(p):
        raise ValueError("无有效实体")
    if not np.isfinite(p).all() or not np.isfinite(t).all():
        raise ValueError("预测或真值存在未声明的非有限值")
    if component == "magnitude":
        p, t = np.linalg.norm(p, axis=1), np.linalg.norm(t, axis=1)
    else:
        index = 0 if component == "scalar" and p.shape[1] == 1 else int(component)
        if index < 0 or index >= p.shape[1]:
            raise ValueError("分量选择不合法")
        p, t = p[:, index], t[:, index]
    difference = p - t
    squared = float(np.square(difference).sum())
    norm = float(np.square(t).sum())
    variance = float(np.square(t - t.mean()).sum())
    absolute = float(np.abs(difference).sum())
    truth_absolute = float(np.abs(t).sum())
    threshold = 1e-12 * float(np.abs(t).max())
    nonzero = np.abs(t) > threshold
    relative = (
        float(np.mean(np.abs(difference[nonzero]) / np.abs(t[nonzero]))) if nonzero.any() else None
    )
    values = {
        "max_abs_error": float(np.abs(difference).max()),
        "relative_mae": absolute / truth_absolute if truth_absolute else None,
        "mean_relative_error": relative,
        "mape": relative * 100 if relative is not None else None,
        "mse": squared / len(p),
        "rmse": float(np.sqrt(squared / len(p))),
        "mae": float(np.abs(difference).mean()),
        "relative_l2": float(np.sqrt(squared / norm)) if norm else None,
        "r2": 1 - squared / variance if variance else None,
    }
    if any(v is not None and not np.isfinite(v) for v in values.values()):
        raise ValueError("指标累计溢出")
    reasons = {
        k: "真值恒定"
        if k == "r2"
        else "无非零真值"
        if k in {"mean_relative_error", "mape"}
        else "真值范数为零"
        for k in selected
        if values[k] is None
    }
    return {
        "values": {k: values[k] for k in selected},
        "undefined": reasons,
        "count": len(p),
        "excluded": total - len(p),
        "relative_excluded": int((~nonzero).sum()),
        "relative_threshold": threshold,
    }
