"""MeshGraphNet 训练目标连接。"""

from __future__ import annotations

import torch

from ai4e_core.abilities.constraint.masked import masked_mse
from ai4e_core.abilities.transform.noise import add_gaussian_noise


def velocity_increment_target(previous: torch.Tensor, current: torch.Tensor) -> torch.Tensor:
    """计算相邻物理帧的速度增量。"""
    if previous.shape != current.shape:
        raise ValueError("相邻速度帧形状必须一致")
    return current - previous


def objective(
    model,
    graph: dict[str, torch.Tensor],
    target: torch.Tensor,
    mask: torch.Tensor,
    *,
    noise_std=0.0,
    noise_mask: torch.Tensor | None = None,
    accumulate_normalizers: bool = False,
) -> torch.Tensor:
    """调用模型并在显式可训练节点 mask 上计算 MSE。"""
    inputs = graph["node_features"]
    if noise_std:
        inputs = inputs.clone()
        physical_velocity = inputs[:, :2]
        noisy_velocity = add_gaussian_noise(physical_velocity, noise_std)
        if noise_mask is not None:
            if noise_mask.shape != physical_velocity.shape[:-1]:
                raise ValueError("noise_mask 必须匹配节点轴")
            noisy_velocity = torch.where(
                noise_mask.to(device=inputs.device).unsqueeze(-1),
                noisy_velocity,
                physical_velocity,
            )
        inputs[:, :2] = noisy_velocity
        target = target - (noisy_velocity - physical_velocity)
    prediction = model(
        inputs,
        graph["edge_features"],
        graph["edge_index"],
        accumulate=accumulate_normalizers,
    )
    normalized_target = model.normalize_target(target, accumulate=accumulate_normalizers)
    return masked_mse(prediction, normalized_target, mask, feature_reduction="sum")
