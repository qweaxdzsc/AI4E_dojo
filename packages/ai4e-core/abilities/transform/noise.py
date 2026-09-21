"""与模型无关的加性噪声变换。"""

from __future__ import annotations

import torch


def add_gaussian_noise(
    value: torch.Tensor, std: float | torch.Tensor, *, generator=None
) -> torch.Tensor:
    """按给定标准差添加高斯噪声，不改变输入张量。"""
    scale = torch.as_tensor(std, dtype=value.dtype, device=value.device)
    if scale.ndim > 0 and scale.numel() not in (1, value.shape[-1]):
        raise ValueError("噪声标准差必须是标量或与最后一维对齐")
    if not torch.isfinite(scale).all() or (scale < 0).any():
        raise ValueError("噪声标准差必须是有限非负数")
    noise = torch.randn(value.shape, dtype=value.dtype, device=value.device, generator=generator)
    return value + noise * scale
