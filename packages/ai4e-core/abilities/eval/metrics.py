"""逐样本物理场指标；零目标范数显式计为相对误差不可用。"""

import torch

METRIC_NAMES = ("mse", "mae", "relative_l2")


def selected_metrics(names=None) -> tuple[str, ...]:
    """缺省保留原三项，显式空列表不计算附加指标；未知或重复名称拒绝。"""
    if names is None:
        return METRIC_NAMES
    if not isinstance(names, (list, tuple)) or any(
        not isinstance(name, str) or name not in METRIC_NAMES for name in names
    ):
        raise ValueError("评估指标只支持 mse、mae、relative_l2")
    if len(set(names)) != len(names):
        raise ValueError("评估指标不能重复")
    return tuple(names)


def field_metrics(prediction, target, *, metrics=None) -> dict:
    """按 metrics 计算误差字典；None 保留三项、空序列返回空字典。

    非法名称、重复名称、广播、空场或非有限数据抛 ValueError。
    相对 L2 的目标范数不大于 1e-8 时返回 None。
    """
    names = selected_metrics(metrics)
    if prediction.shape != target.shape or not target.numel():
        raise ValueError("评估场必须同形且非空")
    delta = prediction - target
    if not torch.isfinite(delta).all() or not torch.isfinite(target).all():
        raise ValueError("评估包含非有限值")
    result = {}
    if "mse" in names:
        result["mse"] = delta.square().mean().item()
    if "mae" in names:
        result["mae"] = delta.abs().mean().item()
    if "relative_l2" in names:
        norm = torch.linalg.vector_norm(target)
        result["relative_l2"] = (
            (torch.linalg.vector_norm(delta) / norm).item() if norm > 1e-8 else None
        )
    return result
