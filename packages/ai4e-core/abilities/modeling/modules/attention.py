"""标准多头注意力；掩码真值表示忽略，不绑定几何或物理字段。"""

from __future__ import annotations

import torch
from torch import nn


def _validate_masks(query, context, padding, attention, heads):
    """拒绝布局错误与无可用键的查询，避免全屏蔽行静默产生伪输出。"""
    if query.ndim != 3 or context.ndim != 3 or query.shape[0] != context.shape[0]:
        raise ValueError("注意力输入必须是批次一致的 [B,N,D]")
    batch, queries, _ = query.shape
    keys = context.shape[1]
    if queries == 0 or keys == 0:
        raise ValueError("注意力查询和键不能为空")
    blocked = torch.zeros(batch, heads, queries, keys, dtype=torch.bool, device=query.device)
    if padding is not None:
        if padding.dtype != torch.bool or padding.shape != (batch, keys):
            raise ValueError("key_padding_mask 必须是 [B,K] 布尔张量，真表示忽略")
        blocked |= padding[:, None, None, :]
    if attention is not None:
        if attention.dtype != torch.bool and not attention.is_floating_point():
            raise ValueError("attn_mask 必须是布尔或浮点张量")
        if attention.shape == (queries, keys):
            mask = attention[None, None]
        elif attention.shape == (batch * heads, queries, keys):
            mask = attention.reshape(batch, heads, queries, keys)
        else:
            raise ValueError("attn_mask 形状必须是 [Q,K] 或 [B*heads,Q,K]")
        if attention.is_floating_point():
            if torch.isnan(attention).any() or torch.isposinf(attention).any():
                raise ValueError("attn_mask 不能含 NaN 或正无穷")
            mask = torch.isneginf(mask)
        blocked |= mask
    if blocked.all(dim=-1).any():
        raise ValueError("注意力查询不能屏蔽全部键")


class CrossAttention(nn.Module):
    """标准交叉注意力；查询宽度为 dim，上下文宽度可单独配置。"""

    def __init__(
        self, dim: int, num_heads: int, *, context_dim: int | None = None, dropout: float = 0.0
    ) -> None:
        super().__init__()
        if dim < 1 or num_heads < 1 or dim % num_heads:
            raise ValueError("注意力宽度须为正且可被头数整除")
        self.attention = nn.MultiheadAttention(
            dim,
            num_heads,
            dropout=dropout,
            batch_first=True,
            kdim=context_dim,
            vdim=context_dim,
        )

    def forward(
        self,
        query: torch.Tensor,
        context: torch.Tensor,
        *,
        key_padding_mask: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """返回 [B,Q,D]；布尔掩码真表示忽略，浮点掩码按加性偏置解释。"""
        _validate_masks(query, context, key_padding_mask, attn_mask, self.attention.num_heads)
        padding = key_padding_mask
        # MHA 要求两种掩码类型一致；转换仍保持“真为忽略”的公开语义。
        if attn_mask is not None and attn_mask.is_floating_point() and padding is not None:
            padding = torch.zeros_like(padding, dtype=attn_mask.dtype).masked_fill(
                padding, -torch.inf
            )
        return self.attention(
            query,
            context,
            context,
            key_padding_mask=padding,
            attn_mask=attn_mask,
            need_weights=False,
        )[0]


class SelfAttention(CrossAttention):
    """标准非因果自注意力；因果或其他屏蔽只能通过显式掩码传入。"""

    def __init__(self, dim: int, num_heads: int, *, dropout: float = 0.0) -> None:
        super().__init__(dim, num_heads, dropout=dropout)

    def forward(
        self,
        value: torch.Tensor,
        *,
        key_padding_mask: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """查询、键和值共用输入，返回与输入相同的序列布局。"""
        return super().forward(value, value, key_padding_mask=key_padding_mask, attn_mask=attn_mask)
