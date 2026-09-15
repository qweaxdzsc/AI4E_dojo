"""标准物理条件的比较与分项聚合，不负责模型、采样或训练循环。"""

import math

import torch


def residual_loss(residual, *, loss="mse", reduction="mean"):
    """逐点残差归约；l2 为原 Burgers 使用的非平方全局范数。"""
    if not residual.numel() or not torch.isfinite(residual).all():
        raise ValueError("约束残差为空或非有限")
    if reduction not in {"mean", "sum"}:
        raise ValueError("未知损失归约方式")
    if loss == "l2":
        return torch.linalg.vector_norm(residual)
    if loss not in {"mse", "mae"}:
        raise ValueError(f"未知物理损失: {loss}")
    values = residual.square() if loss == "mse" else residual.abs()
    return values.mean() if reduction == "mean" else values.sum()


def boundary_residual(*, value, gradient, normals, condition, target=None):
    """Dirichlet 或物理外法向 Neumann 残差；零梯度不等同于任意零通量。"""
    kind = condition["type"]
    if kind == "fixed_value":
        expected = condition.get("value") if target is None else target
        predicted = value
    elif kind in {"fixed_gradient", "zero_gradient"}:
        if kind == "zero_gradient" and ("value" in condition or "gradient" in condition):
            raise ValueError("zero_gradient 不接受 value/gradient")
        if gradient is None or gradient.shape != normals.shape:
            raise ValueError("边界梯度和物理法向不对齐")
        predicted = (gradient * normals).sum(-1)
        expected = (
            0.0
            if kind == "zero_gradient"
            else (condition.get("gradient") if target is None else target)
        )
    else:
        raise ValueError(f"未知边界条件: {kind}")
    if isinstance(expected, torch.Tensor):
        if expected.shape not in (torch.Size([]), predicted.shape):
            raise ValueError("边界目标形状不对齐")
    elif (
        isinstance(expected, bool)
        or not isinstance(expected, (int, float))
        or not math.isfinite(expected)
    ):
        raise ValueError("边界目标必须为有限标量或匹配张量")
    return predicted - expected
