"""原版重加权与控制安全代价；物理安全值和模型缩放分开。"""

import torch

from ai4e_contrib.ability.transform.safediffcon.preparation import physical


def safety(values: torch.Tensor, *, case: str, calibration: bool = False) -> torch.Tensor:
    """以原版统计量返回安全值：Burgers 平方最大值通道，Tokamak 最低q95。"""
    if case == "burgers":
        return (
            values[:, 2, :11].mean(dim=(-1, -2))
            if calibration
            else values[:, 2, :11].amax(dim=(-1, -2))
        )
    return values[:, 1, :122].amin(dim=-1)


def cost(
    values: torch.Tensor, target, *, case: str, q: float = 0.0, weight: float = 1.0
) -> torch.Tensor:
    """原 guidance/reweight 物理代价；目标使用显式提供的源码目标。"""
    if case == "burgers":
        s = safety(values, case=case, calibration=True)
        return torch.maximum(s + q - 0.8**2, torch.zeros_like(s)) * weight
    s = safety(values, case=case)
    # 发布案例 w_obj=0；目标轨迹通过条件通道提供，不能擅自加入目标损失。
    return torch.maximum(4.98 - s + q, torch.zeros_like(s)) * weight


def reweights(
    values: torch.Tensor, target, *, case: str, q: float = 0.0, weight: float = 1.0
) -> torch.Tensor:
    """原指数重加权及全局样本归一化，全部下溢时保持原均匀回退。"""
    w = torch.exp(-cost(physical(values, case=case), target, case=case, q=q, weight=weight))
    return torch.ones_like(w) if w.sum() == 0 else len(w) * w / w.sum()


def diffusion_loss(model: torch.nn.Module, values) -> torch.Tensor:
    """调用原噪声损失，普通训练批次不改变模型内部损失归约。"""
    if isinstance(values, tuple):
        sample, weight = values
        return (model(sample, mean=False) * weight).mean()
    return model(values)
