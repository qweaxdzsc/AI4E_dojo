"""标准后规范化 Transformer 编码块；显式保留残差和前馈顺序。"""

from __future__ import annotations

import torch
from torch import nn

from .attention import SelfAttention
from .feed_forward import FeedForward


class EncoderBlock(nn.Module):
    """注意力残差后规范化，再进行前馈残差后规范化；组件可独立替换。"""

    def __init__(
        self,
        dim: int,
        num_heads: int = 4,
        *,
        feed_forward_dim: int = 256,
        dropout: float = 0.0,
        attention: nn.Module | None = None,
        feed_forward: nn.Module | None = None,
    ) -> None:
        super().__init__()
        self.attention = (
            attention if attention is not None else SelfAttention(dim, num_heads, dropout=dropout)
        )
        self.feed_forward = (
            feed_forward
            if feed_forward is not None
            else FeedForward(
                dim,
                dim,
                hidden_features=(feed_forward_dim,),
                activation="relu",
                dropout=dropout,
            )
        )
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(
        self,
        value: torch.Tensor,
        *,
        key_padding_mask: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """执行标准后规范化算术，掩码只作用于注意力的键。"""
        value = self.norm1(
            value
            + self.dropout1(
                self.attention(
                    value,
                    key_padding_mask=key_padding_mask,
                    attn_mask=attn_mask,
                )
            )
        )
        return self.norm2(value + self.dropout2(self.feed_forward(value)))
