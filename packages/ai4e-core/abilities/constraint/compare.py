"""同形张量的比较方法；供监督项选用，不解释场名。"""

import math

import torch
import torch.nn.functional as F

METHODS = frozenset({"mse", "mae", "huber", "relative_l2"})


def compare(prediction, target, method: str = "mse", *, delta: float = 1.0):
    """按声明方法比较两个同形张量，得到可反向的标量。

    相对 L2 用整场向量范数比；目标范数不大于 ``1e-8`` 时失败，
    避免训练项变成无梯度的空值。评估指标允许跳过，口径不同。
    """
    if prediction.shape != target.shape or prediction.numel() == 0:
        raise ValueError("预测与目标形状必须完全一致且非空")
    if method not in METHODS:
        raise ValueError("未知比较方法")
    if method == "mse":
        return F.mse_loss(target, prediction, reduction="mean")
    if method == "mae":
        return torch.mean((prediction - target).abs())
    if method == "huber":
        width = float(delta)
        if not math.isfinite(width) or width <= 0:
            raise ValueError("Huber宽度必须有限且为正")
        return F.huber_loss(prediction, target, reduction="mean", delta=width)
    norm = torch.linalg.vector_norm(target)
    if float(norm) <= 1e-8:
        raise ValueError("相对L2的目标范数过小")
    return torch.linalg.vector_norm(prediction - target) / norm
