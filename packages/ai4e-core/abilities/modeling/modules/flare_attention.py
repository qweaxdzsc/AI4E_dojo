# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""可选 FLARE++ 动态路由注意力；来源和本地改动见 Notice/physicsnemo/flare_plus_plus.json。

只处理普通特征张量，不绑定几何、模型、训练器或 recipe。固定路由数时，
三次注意力的 token 维计算量随输入长度线性增长，不代表已验证实际加速。
"""

from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F


class FLAREPlusPlus(nn.Module):
    """根据当前输入合成路由的注意力层，可由用户放入自己的网络。

    参数:
        dim: 输入和输出的特征数，正整数。
        heads: 注意力头数，正整数。
        dim_head: 每头内部特征数，正整数；无需 heads * dim_head 等于 dim。
        dropout: 输出投影之后的丢弃概率，范围 [0, 1]；eval 时关闭。
        n_global_queries: 学习 seed 和动态路由的数量，正整数。
        use_te: 只接受 False；本组件不依赖 Transformer Engine。
        attn_scale: 三次注意力共同使用的正有限缩放；None 为 dim_head**-0.5。

    输入/输出为浮点张量 (batch, tokens, dim)。同批样本长度相同，tokens
    必须非零；跨调用可改变长度。不提供 padding mask、因果注意力、几何
    上下文或 token 分片。需要这些语义时应另写明确的局部连接，不能把补零
    当作被屏蔽的 token。普通 state_dict 可保存和恢复学习参数。

    非法构造参数或张量形状抛 ValueError，非浮点输入抛 TypeError；TE 与
    token 分片不支持。此层不包含残差、归一化或 MLP，不自动替换已有模型。
    """

    def __init__(
        self,
        dim: int,
        heads: int = 8,
        dim_head: int = 64,
        dropout: float = 0.0,
        n_global_queries: int = 64,
        use_te: bool = False,
        attn_scale: float | None = None,
    ) -> None:
        super().__init__()
        if use_te:
            raise ValueError("FLAREPlusPlus 不支持 Transformer Engine，请设置 use_te=False")
        for name, value in (
            ("dim", dim),
            ("heads", heads),
            ("dim_head", dim_head),
            ("n_global_queries", n_global_queries),
        ):
            if type(value) is not int or value <= 0:
                raise ValueError(f"{name} 必须为正整数")
        if not math.isfinite(dropout) or not 0.0 <= dropout <= 1.0:
            raise ValueError("dropout 必须在 [0, 1] 内")
        scale = dim_head**-0.5 if attn_scale is None else attn_scale
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("attn_scale 必须为正有限数")

        self.dim = dim
        self.heads = heads
        self.dim_head = dim_head
        self.n_global_queries = n_global_queries
        self.scale = float(scale)
        # 保留上游参数命名和布局，可严格读取同版本 standalone 注意力权重。
        self.q_seed = nn.Parameter(torch.randn(1, heads, n_global_queries, dim_head))
        self.in_projection = nn.Linear(dim, 4 * heads * dim_head)
        self.out_linear = nn.Linear(heads * dim_head, dim)
        self.out_dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """将 (B, N, dim) 特征映射为同形特征，保留 autograd 与调用设备。

        学习 seed 先汇聚当前输入以生成路由，再汇聚物理特征并回传到输入
        token；仅输出投影后使用 dropout。非法形状、空 token 和整数输入
        在计算前拒绝；DTensor/token 分片会因缺少全局归一化而明确拒绝。
        """
        if hasattr(x, "redistribute"):
            raise NotImplementedError("FLAREPlusPlus 不支持 token 分片，请使用普通复制张量")
        if x.ndim != 3 or x.shape[-1] != self.dim or x.shape[1] == 0:
            raise ValueError(f"输入必须为 (B, N, {self.dim}) 且 N > 0，实际为 {tuple(x.shape)}")
        if not x.is_floating_point():
            raise TypeError("FLAREPlusPlus 输入必须为浮点张量")

        projections = self.in_projection(x).chunk(4, dim=-1)
        query_k, query_v, physical_k, physical_v = (
            value.reshape(x.shape[0], x.shape[1], self.heads, self.dim_head).transpose(1, 2)
            for value in projections
        )
        seeds = self.q_seed.to(dtype=x.dtype).expand(x.shape[0], -1, -1, -1)
        queries = F.scaled_dot_product_attention(seeds, query_k, query_v, scale=self.scale)
        routed_values = F.scaled_dot_product_attention(
            queries, physical_k, physical_v, scale=self.scale
        )
        output = F.scaled_dot_product_attention(
            physical_k, queries, routed_values, scale=self.scale
        )
        output = output.transpose(1, 2).reshape(x.shape[0], x.shape[1], self.heads * self.dim_head)
        return self.out_dropout(self.out_linear(output))
