"""由公开分块、标准编码阶段和重建模块组成的中立规则场模型。"""

from __future__ import annotations

from collections.abc import Sequence

import torch
from torch import nn

from ..modules.patch_embedding import PatchEmbedding, patch_centers
from ..modules.patch_reconstruction import PatchReconstruction
from ..modules.position_encoding import ContinuousSincosEmbed
from ..modules.transformer import EncoderBlock
from ..stages.transformer import TransformerEncoder


class PatchTransformer(nn.Module):
    """标准非因果后规范化编码器；三个主要子结构均可注入普通模块。"""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        *,
        patch_shape: Sequence[int] = (5, 5),
        dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        feed_forward_dim: int = 256,
        dropout: float = 0.0,
        embedding: nn.Module | None = None,
        encoder: nn.Module | None = None,
        reconstruction: nn.Module | None = None,
        position_encoding: nn.Module | None = None,
    ) -> None:
        super().__init__()
        self.embedding = (
            embedding if embedding is not None else PatchEmbedding(in_channels, dim, patch_shape)
        )
        self.encoder = (
            encoder
            if encoder is not None
            else TransformerEncoder(
                EncoderBlock(dim, num_heads, feed_forward_dim=feed_forward_dim, dropout=dropout)
                for _ in range(num_layers)
            )
        )
        self.reconstruction = (
            reconstruction
            if reconstruction is not None
            else PatchReconstruction(dim, out_channels, patch_shape)
        )
        self.position_encoding = (
            position_encoding
            if position_encoding is not None
            else ContinuousSincosEmbed(dim, len(patch_shape))
        )

    def forward(self, value: torch.Tensor, valid_mask: torch.Tensor | None = None) -> torch.Tensor:
        """返回末轴通道规则场，无效格点置零；有效掩码仍由调用者持有。"""
        tokens, padding, info = self.embedding(value, valid_mask)
        centers = patch_centers(info, device=tokens.device, dtype=tokens.dtype)
        tokens = tokens + self.position_encoding(centers).to(tokens.dtype)
        tokens = self.encoder(tokens, key_padding_mask=padding)
        output = self.reconstruction(tokens, info)
        return output if valid_mask is None else output.masked_fill(~valid_mask.unsqueeze(-1), 0)
