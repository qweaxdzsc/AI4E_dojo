"""固定物理场的逐元素误差；调用者决定时间窗口和样本归约。"""

import torch


def errors(prediction, truth, *, epsilon=1e-8):
    """返回 MAE、RMSE、MARE，分母为 abs(truth)+epsilon。"""
    if prediction.shape != truth.shape or truth.numel() == 0:
        raise ValueError("评价形状不匹配或为空")
    if not torch.isfinite(prediction).all() or not torch.isfinite(truth).all():
        raise ValueError("评价数组含非有限值")
    difference = prediction.double() - truth.double()
    return {
        "mae": float(difference.abs().mean()),
        "rmse": float(difference.square().mean().sqrt()),
        "mare": float((difference.abs() / (truth.double().abs() + epsilon)).mean()),
    }
