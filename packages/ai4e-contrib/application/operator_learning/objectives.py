"""Darcy监督与最大值原理约束的局部连接；不将采样外圈冒充精确壁面。"""

import math

import torch

from ai4e_core.abilities.constraint.physical import residual_loss


def physical_terms(prediction, target, valid, *, mean, scale):
    """分别返回监督MSE和非负解违约；用于正系数、非负源、零Dirichlet的Darcy。

    样本的最外圈可能是离散内部点，不强加边界零值。非负解由椭圆方程
    最大值原理给出，不依赖采样点是否恰落在边界。scale统一比较量纲；
    这里不宣称评价了完整PDE残差。调用方负责来源方程的准入。
    """
    if (
        prediction.shape != target.shape
        or valid.shape != prediction.shape[:-1]
        or valid.dtype != torch.bool
        or not valid.any()
    ):
        raise ValueError("场、监督和有效域不对齐")
    mean = torch.as_tensor(mean, dtype=prediction.dtype, device=prediction.device)
    scale = torch.as_tensor(scale, dtype=prediction.dtype, device=prediction.device)
    if (
        mean.shape not in (torch.Size([]), torch.Size([prediction.shape[-1]]))
        or scale.shape not in (torch.Size([]), torch.Size([prediction.shape[-1]]))
        or not torch.isfinite(mean).all()
        or not torch.isfinite(scale).all()
        or (scale <= 0).any()
    ):
        raise ValueError("物理尺度必须正且有限")
    physical = prediction * scale + mean
    data = residual_loss(prediction[valid] - target[valid])
    violation = torch.relu(-physical[valid]) / scale
    return {"data": data, "nonnegative": residual_loss(violation)}


class FieldObjective:
    """普通训练目标对象，调用已有约束并保持梯度，不持有训练会话。"""

    def __init__(self, statistics, *, physical_weight=0.0):
        if not math.isfinite(physical_weight) or physical_weight < 0:
            raise ValueError("物理约束权重须非负有限")
        self.statistics = statistics
        self.physical_weight = physical_weight

    def __call__(self, model, item):
        prediction = model(item["input"], item["valid"], item.get("coordinates"))
        if (
            prediction.shape != item["target"].shape
            or item["valid"].shape != prediction.shape[:-1]
            or item["valid"].dtype != torch.bool
            or not item["valid"].any()
        ):
            raise ValueError("场、监督和有效域不对齐，禁止隐式广播")
        if self.physical_weight:
            terms = physical_terms(
                prediction,
                item["target"],
                item["valid"],
                **{key: self.statistics["target"][key] for key in ("mean", "scale")},
            )
            return terms["data"] + self.physical_weight * terms["nonnegative"]
        return residual_loss(prediction[item["valid"]] - item["target"][item["valid"]])
