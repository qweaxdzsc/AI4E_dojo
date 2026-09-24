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


# 新公共组合独立于上方历史块：保留历史构造签名、参数键及默认算术。
from .feed_forward import FeedForward


def aggregate_messages(
    messages: torch.Tensor, target: torch.Tensor, node_count: int, *, reduction: str = "sum"
) -> torch.Tensor:
    """按目标节点聚合消息；均值只除实际入度，孤点输出零。"""
    if reduction not in {"sum", "mean"}:
        raise ValueError("reduction 必须是 sum 或 mean")
    if messages.ndim != 2 or target.ndim != 1 or len(target) != len(messages):
        raise ValueError("消息必须是 [E,D]，目标索引必须是 [E]")
    if target.dtype != torch.long or node_count < 0:
        raise ValueError("目标索引须为 int64，节点数不能为负")
    if target.numel() and (target.min() < 0 or target.max() >= node_count):
        raise ValueError("目标索引越界")
    result = messages.new_zeros(node_count, messages.shape[1]).index_add(0, target, messages)
    if reduction == "mean":
        count = messages.new_zeros(node_count, 1).index_add(
            0, target, messages.new_ones(len(target), 1)
        )
        result = result / count.clamp_min(1)
    return result


class EdgeUpdate(nn.Module):
    """连接源节点、目标节点与原边，进行多层变换及边残差更新。"""

    def __init__(self, node_dim: int, edge_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            FeedForward(
                node_dim * 2 + edge_dim,
                edge_dim,
                hidden_features=(hidden_dim, hidden_dim),
                activation="relu",
            ),
            nn.LayerNorm(edge_dim),
        )

    def forward(
        self, nodes: torch.Tensor, edges: torch.Tensor, edge_index: torch.Tensor
    ) -> torch.Tensor:
        """返回更新后的边状态；消息方向固定为 source 到 target。"""
        source, target = edge_index
        return edges + self.network(torch.cat((nodes[source], nodes[target], edges), dim=-1))


class NodeUpdate(nn.Module):
    """连接原节点和聚合后的新边消息，进行多层变换及节点残差更新。"""

    def __init__(self, node_dim: int, edge_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            FeedForward(
                node_dim + edge_dim,
                node_dim,
                hidden_features=(hidden_dim, hidden_dim),
                activation="relu",
            ),
            nn.LayerNorm(node_dim),
        )

    def forward(self, nodes: torch.Tensor, messages: torch.Tensor) -> torch.Tensor:
        """返回残差后的节点状态。"""
        return nodes + self.network(torch.cat((nodes, messages), dim=-1))


class GraphInteraction(nn.Module):
    """可注入消息、聚合与节点更新的图交互，不要求统一组件基类。"""

    def __init__(
        self,
        node_dim: int,
        edge_dim: int,
        hidden_dim: int,
        *,
        aggregation: str = "sum",
        edge_update=None,
        node_update=None,
        aggregate=None,
    ) -> None:
        super().__init__()
        if min(node_dim, edge_dim, hidden_dim) <= 0 or aggregation not in {"sum", "mean"}:
            raise ValueError("图维度须为正，aggregation 必须为 sum 或 mean")
        self.aggregation = aggregation
        self.edge_update = (
            edge_update if edge_update is not None else EdgeUpdate(node_dim, edge_dim, hidden_dim)
        )
        self.node_update = (
            node_update if node_update is not None else NodeUpdate(node_dim, edge_dim, hidden_dim)
        )
        self.aggregate = aggregate if aggregate is not None else aggregate_messages

    def forward(
        self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """先计算新边，再聚合新边并更新节点；返回节点和边。"""
        if node_features.ndim != 2 or edge_features.ndim != 2:
            raise ValueError("节点和边特征必须是二维张量")
        if edge_index.shape != (2, len(edge_features)) or edge_index.dtype != torch.long:
            raise ValueError("edge_index 必须是 [2,E] int64 索引")
        if edge_index.numel() and (edge_index.min() < 0 or edge_index.max() >= len(node_features)):
            raise ValueError("edge_index 越界")
        edges = self.edge_update(node_features, edge_features, edge_index)
        messages = self.aggregate(
            edges, edge_index[1], len(node_features), reduction=self.aggregation
        )
        return self.node_update(node_features, messages), edges
