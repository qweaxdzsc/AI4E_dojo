"""中立节点、边编码与节点读出；多层计算共用公开前馈组件。"""

import torch
from torch import nn

from .feed_forward import FeedForward


class GraphEncoder(nn.Module):
    """把节点和边独立映射到相同隐藏宽度，末端使用层归一化。"""

    def __init__(self, node_input_dim: int, edge_input_dim: int, hidden_dim: int = 64) -> None:
        super().__init__()
        self.nodes = nn.Sequential(
            FeedForward(
                node_input_dim,
                hidden_dim,
                hidden_features=(hidden_dim, hidden_dim),
                activation="relu",
            ),
            nn.LayerNorm(hidden_dim),
        )
        self.edges = nn.Sequential(
            FeedForward(
                edge_input_dim,
                hidden_dim,
                hidden_features=(hidden_dim, hidden_dim),
                activation="relu",
            ),
            nn.LayerNorm(hidden_dim),
        )

    def forward(
        self, nodes: torch.Tensor, edges: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """返回相同节点、边行序的隐藏特征。"""
        return self.nodes(nodes), self.edges(edges)


class GraphReadout(nn.Module):
    """按节点独立读出，无输出激活，不解释节点物理含义。"""

    def __init__(self, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.network = FeedForward(
            hidden_dim, output_dim, hidden_features=(hidden_dim, hidden_dim), activation="relu"
        )

    def forward(self, nodes: torch.Tensor) -> torch.Tensor:
        """返回每个节点的输出特征。"""
        return self.network(nodes)
