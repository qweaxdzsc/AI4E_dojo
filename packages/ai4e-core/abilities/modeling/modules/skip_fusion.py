"""跳连的尺寸对齐、拼接与特征融合，保留两分支梯度。"""

from collections.abc import Sequence

import torch
from torch import Tensor, nn

from .spatial_resampling import SpatialUpsample


class SkipFusion(nn.Module):
    """插值主支，与跳连按通道拼接后执行注入的融合网络。"""

    def __init__(self, fusion: nn.Module, *, upsample: nn.Module | None = None) -> None:
        super().__init__()
        self.upsample = upsample if upsample is not None else SpatialUpsample()
        self.fusion = fusion

    def forward(self, value: Tensor, skip: Tensor, size: Sequence[int]) -> Tensor:
        """显式尺寸必须与跳连完全一致，不能以裁切掩盖交接错误。"""
        if value.ndim not in (4, 5) or value.ndim != skip.ndim or value.shape[0] != skip.shape[0]:
            raise ValueError("跳连批次或空间维度不相容")
        if tuple(skip.shape[2:]) != tuple(size):
            raise ValueError("跳连尺寸与声明不一致")
        aligned = self.upsample(value, size)
        if aligned.shape[0] != skip.shape[0] or aligned.shape[2:] != skip.shape[2:]:
            raise ValueError("上采样输出与跳连不相容")
        return self.fusion(torch.cat((skip, aligned), dim=1))
