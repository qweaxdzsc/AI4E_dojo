"""分块序列的可训练空间重建；显式裁去编码阶段的补齐区域。"""

from __future__ import annotations

import math
from collections.abc import Sequence

import torch
from torch import nn


class PatchReconstruction(nn.Module):
    """线性读出每块格点再拼接；不是投影矩阵的数值逆运算。"""

    def __init__(self, dim: int, out_channels: int, patch_shape: Sequence[int]) -> None:
        super().__init__()
        self.patch_shape = tuple(patch_shape)
        if len(self.patch_shape) not in (2, 3) or any(
            type(p) is not int or p < 1 for p in self.patch_shape
        ):
            raise ValueError("patch_shape 必须是二或三个正整数")
        if min(dim, out_channels) < 1:
            raise ValueError("投影宽度与输出通道必须为正")
        self.out_channels = out_channels
        self.projection = nn.Linear(dim, math.prod(self.patch_shape) * out_channels)

    def forward(self, tokens: torch.Tensor, spatial_info: dict) -> torch.Tensor:
        """根据编码阶段元数据重建 [B,*original_spatial,C]。"""
        patch = self.patch_shape
        ndim = len(patch)
        spatial = tuple(spatial_info["spatial_shape"])
        padded = tuple(spatial_info["padded_shape"])
        grid = tuple(spatial_info["grid_shape"])
        if (
            tuple(spatial_info["patch_shape"]) != patch
            or len(spatial) != ndim
            or len(padded) != ndim
            or len(grid) != ndim
        ):
            raise ValueError("分块重建元数据维度不一致")
        if any(
            g < 1 or n < 1 or not 0 <= size - n < p or size != g * p
            for n, size, g, p in zip(spatial, padded, grid, patch, strict=True)
        ):
            raise ValueError("原空间、补齐空间与块格不一致")
        if tokens.ndim != 3 or tokens.shape[1] != math.prod(grid):
            raise ValueError("token 数量与空间块格不一致")
        blocks = self.projection(tokens).reshape(tokens.shape[0], *grid, *patch, self.out_channels)
        axes = [0]
        for i in range(ndim):
            axes.extend((1 + i, 1 + ndim + i))
        axes.append(2 * ndim + 1)
        value = blocks.permute(axes).reshape(tokens.shape[0], *padded, self.out_channels)
        return value[(slice(None), *(slice(n) for n in spatial), slice(None))]
