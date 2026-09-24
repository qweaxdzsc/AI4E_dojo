"""末轴通道规则场的分块投影；空间身份和掩码显式交接。"""

from __future__ import annotations

import math
from collections.abc import Sequence

import torch
from torch import nn
from torch.nn import functional as F


def patch_centers(spatial_info: dict, *, device=None, dtype=torch.float32) -> torch.Tensor:
    """返回 [N,ndim] 归一化块格中心；它是索引位置而非物理坐标。"""
    grid = spatial_info["grid_shape"]
    axes = [(torch.arange(n, device=device, dtype=dtype) + 0.5) / n for n in grid]
    return torch.stack(torch.meshgrid(*axes, indexing="ij"), dim=-1).reshape(-1, len(grid))


def partition_patches(value: torch.Tensor, patch_shape: Sequence[int]) -> torch.Tensor:
    """将已整除的 [B,*spatial,C] 转为 [B,N,patch_volume*C]，末轴最快。"""
    ndim = len(patch_shape)
    grid = [value.shape[i + 1] // patch_shape[i] for i in range(ndim)]
    shape = [value.shape[0]]
    for count, patch in zip(grid, patch_shape, strict=True):
        shape.extend((count, patch))
    shape.append(value.shape[-1])
    axes = [0, *range(1, 2 * ndim + 1, 2), *range(2, 2 * ndim + 1, 2), 2 * ndim + 1]
    return value.reshape(shape).permute(axes).reshape(value.shape[0], math.prod(grid), -1)


class PatchEmbedding(nn.Module):
    """把二维或三维规则格分块后线性投影；仅在高索引侧补零。"""

    def __init__(self, in_channels: int, dim: int, patch_shape: Sequence[int]) -> None:
        super().__init__()
        self.patch_shape = tuple(patch_shape)
        if len(self.patch_shape) not in (2, 3) or any(
            type(p) is not int or p < 1 for p in self.patch_shape
        ):
            raise ValueError("patch_shape 必须是二或三个正整数")
        if in_channels < 1 or dim < 1:
            raise ValueError("通道数与投影宽度必须为正")
        self.in_channels = in_channels
        self.projection = nn.Linear(math.prod(self.patch_shape) * in_channels, dim)

    def forward(
        self,
        value: torch.Tensor,
        valid_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, dict]:
        """返回 tokens、真为忽略的键掩码，以及可搬移的纯形状字典。"""
        ndim = len(self.patch_shape)
        if value.ndim != ndim + 2 or value.shape[-1] != self.in_channels:
            raise ValueError("分块输入必须为 [B,*spatial,in_channels]")
        spatial = tuple(value.shape[1:-1])
        if value.shape[0] < 1 or any(n < 1 for n in spatial):
            raise ValueError("批次和空间维度不能为空")
        if valid_mask is None:
            valid_mask = torch.ones(value.shape[:-1], dtype=torch.bool, device=value.device)
        if valid_mask.dtype != torch.bool or valid_mask.shape != value.shape[:-1]:
            raise ValueError("valid_mask 必须是 [B,*spatial] 布尔张量")
        padded = tuple(
            ((n + p - 1) // p) * p for n, p in zip(spatial, self.patch_shape, strict=True)
        )
        pads = [0, 0]
        for n, size in reversed(list(zip(spatial, padded, strict=True))):
            pads.extend((0, size - n))
        masked = value.masked_fill(~valid_mask.unsqueeze(-1), 0)
        blocks = partition_patches(F.pad(masked, pads), self.patch_shape)
        validity = partition_patches(
            F.pad(valid_mask.unsqueeze(-1), pads, value=False), self.patch_shape
        )
        ignored = ~validity.any(dim=-1)
        if ignored.all(dim=-1).any():
            raise ValueError("分块样本必须至少包含一个有效格点")
        info = {
            "spatial_shape": spatial,
            "padded_shape": padded,
            "patch_shape": self.patch_shape,
            "grid_shape": tuple(n // p for n, p in zip(padded, self.patch_shape, strict=True)),
        }
        return self.projection(blocks), ignored, info
