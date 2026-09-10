"""逐样本物理场指标；零目标范数显式计为相对误差不可用。"""

import torch


def field_metrics(prediction, target) -> dict:
    """计算 MSE、MAE 与 relative L2，拒绝广播和非有限数据。"""
    if prediction.shape != target.shape or not target.numel():
        raise ValueError("评估场必须同形且非空")
    delta = prediction - target
    if not torch.isfinite(delta).all() or not torch.isfinite(target).all():
        raise ValueError("评估包含非有限值")
    norm = torch.linalg.vector_norm(target)
    return {
        "mse": delta.square().mean().item(),
        "mae": delta.abs().mean().item(),
        "relative_l2": (torch.linalg.vector_norm(delta) / norm).item() if norm > 1e-8 else None,
    }
