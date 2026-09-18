"""速度目标逐样本损失；不混入领域条件和通道选择。"""

import torch


def velocity_mse(prediction, target):
    """先每样本展平求平均，再样本平均；拒绝广播。"""
    if prediction.shape != target.shape or not prediction.numel():
        raise ValueError("速度目标和预测形状不一致")
    difference = prediction.reshape(prediction.shape[0], -1) - target.reshape(target.shape[0], -1)
    if not torch.isfinite(difference).all():
        raise ValueError("非有限速度目标")
    return difference.square().mean(dim=1).mean()
