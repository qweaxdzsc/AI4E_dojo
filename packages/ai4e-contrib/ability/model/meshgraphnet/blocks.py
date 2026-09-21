"""MeshGraphNet 的模型专属编码、处理和读出块。"""

from __future__ import annotations

import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.graph_message_passing import GraphMessagePassingBlock


class GraphEncoder(nn.Module):
    """把原始节点和边特征分别编码到公共隐空间。"""

    def __init__(self, node_input_dim: int, edge_input_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.nodes = _mlp(node_input_dim, hidden_dim, hidden_dim, normalize=True)
        self.edges = _mlp(edge_input_dim, hidden_dim, hidden_dim, normalize=True)

    def forward(
        self, nodes: torch.Tensor, edges: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """返回编码后的节点与边。"""
        return self.nodes(nodes), self.edges(edges)


class GraphProcessor(nn.Module):
    """顺序应用固定数量的残差消息传递块。"""

    def __init__(self, hidden_dim: int, layers: int) -> None:
        super().__init__()
        if layers < 1:
            raise ValueError("processor_layers 必须为正")
        self.layers = nn.ModuleList(
            [
                GraphMessagePassingBlock(hidden_dim, hidden_dim, hidden_dim, aggregation="sum")
                for _ in range(layers)
            ]
        )

    def forward(
        self, nodes: torch.Tensor, edges: torch.Tensor, edge_index: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """执行全部消息传递层并返回最终图状态。"""
        for layer in self.layers:
            nodes, edges = layer(nodes, edges, edge_index)
        return nodes, edges


class GraphDecoder(nn.Module):
    """从最终节点隐状态读出物理状态增量。"""

    def __init__(self, hidden_dim: int, output_dim: int) -> None:
        super().__init__()
        self.readout = _mlp(hidden_dim, output_dim, hidden_dim, normalize=False)

    def forward(self, nodes: torch.Tensor) -> torch.Tensor:
        """把节点隐状态解码为节点输出。"""
        return self.readout(nodes)


def _mlp(input_dim: int, output_dim: int, hidden_dim: int, *, normalize: bool) -> nn.Sequential:
    layers: list[nn.Module] = [
        nn.Linear(input_dim, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, output_dim),
    ]
    if normalize:
        layers.append(nn.LayerNorm(output_dim))
    return nn.Sequential(*layers)
