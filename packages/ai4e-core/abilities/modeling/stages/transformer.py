"""可独立调用的网络编码阶段；不执行训练或运行记录。"""

from collections.abc import Iterable

import torch
from torch import nn


class TransformerEncoder(nn.Module):
    """按显式顺序注册和执行编码块，不自动共享块权重。"""

    def __init__(self, blocks: Iterable[nn.Module]) -> None:
        super().__init__()
        self.blocks = nn.ModuleList(blocks)
        if not self.blocks:
            raise ValueError("编码器至少需要一个块")

    def forward(
        self,
        value: torch.Tensor,
        *,
        key_padding_mask: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """逐块传递特征和掩码，保持 [B,N,D] 布局。"""
        for block in self.blocks:
            value = block(value, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
        return value
