"""圆柱字段和损失调度绑定；残差计算由core实现。"""

import torch

from ai4e_core.abilities.constraint.field_supervision import field_losses, interior_mask


def ramp(update, total, warmup=0.2, duration=0.2):
    """以已完成更新后的下一次更新序号决定连续爬升。"""
    return min(1.0, max(0.0, (update - total * warmup) / (total * duration)))


def objective(prepared, cfg, branch, arm):
    """返回共享训练可调用目标；未来几何只参与损失有效域。"""
    selection = slice(0, 3) if branch == "fluid" else slice(3, 4)
    mean = torch.tensor(prepared["statistics"]["mean"])[selection]
    scale = torch.tensor(prepared["statistics"]["scale"])[selection]

    def loss(model, item):
        prediction = model(item["input"])
        target = item["target"][..., selection]
        mask = (
            interior_mask(item["physical"][..., 3] > 0.02)
            if branch == "fluid"
            else torch.ones_like(target[..., 0], dtype=torch.bool)
        )
        parts = field_losses(
            prediction,
            target,
            mask,
            mean=mean.to(prediction),
            scale=scale.to(prediction),
            gradient_scale=prepared["gradient_scale"],
            velocity=branch == "fluid",
        )
        factor = ramp(
            item["update"],
            cfg["train"]["updates"],
            cfg["loss"]["warmup_fraction"],
            cfg["loss"]["ramp_fraction"],
        )
        loss.last = {k: float(v.detach()) for k, v in parts.items()}
        return parts["data"] + factor * (
            cfg["loss"]["gradient_weight"] * parts["gradient"]
            + (cfg["loss"]["divergence_weight"] * parts["divergence"] if arm == "physics" else 0)
        )

    loss.last = {}
    return loss
