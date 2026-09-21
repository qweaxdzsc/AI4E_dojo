"""中立图消息传递模块；不绑定具体模型或数据集。"""

from __future__ import annotations

import torch
from torch import nn


class GraphMessagePassingBlock(nn.Module):
    """使用边、源节点和目标节点特征更新节点与边状态。"""

    def __init__(
        self, node_dim: int, edge_dim: int, hidden_dim: int, *, aggregation: str = "sum"
    ) -> None:
        super().__init__()
        if min(node_dim, edge_dim, hidden_dim) <= 0:
            raise ValueError("图模块维度必须为正")
        if aggregation not in {"sum", "mean"}:
            raise ValueError("aggregation 必须是 sum 或 mean")
        self.aggregation = aggregation
        self.edge_update = nn.Sequential(
            nn.Linear(node_dim * 2 + edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, edge_dim),
            nn.LayerNorm(edge_dim),
        )
        self.node_update = nn.Sequential(
            nn.Linear(node_dim + edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_dim),
            nn.LayerNorm(node_dim),
        )

    def forward(
        self,
        node_features: torch.Tensor,
        edge_features: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """先更新边，再按目标节点聚合新边并更新节点。"""
        if node_features.ndim != 2 or edge_features.ndim != 2:
            raise ValueError("节点和边特征必须是二维张量")
        if (
            edge_index.ndim != 2
            or edge_index.shape[0] != 2
            or edge_index.shape[1] != edge_features.shape[0]
        ):
            raise ValueError("edge_index 与边特征数量不一致")
        source, target = edge_index
        if edge_index.numel() and (
            edge_index.min() < 0 or edge_index.max() >= node_features.shape[0]
        ):
            raise ValueError("edge_index 越界")
        updated_edges = edge_features + self.edge_update(
            torch.cat([node_features[source], node_features[target], edge_features], dim=-1)
        )
        messages = torch.zeros(
            node_features.shape[0],
            updated_edges.shape[1],
            dtype=updated_edges.dtype,
            device=updated_edges.device,
        )
        messages.index_add_(0, target, updated_edges)
        counts = torch.zeros(
            node_features.shape[0], 1, dtype=node_features.dtype, device=node_features.device
        )
        counts.index_add_(
            0,
            target,
            torch.ones(target.shape[0], 1, dtype=node_features.dtype, device=node_features.device),
        )
        if self.aggregation == "mean":
            messages = messages / counts.clamp_min(1)
        updated_nodes = node_features + self.node_update(
            torch.cat([node_features, messages], dim=-1)
        )
        return updated_nodes, updated_edges
