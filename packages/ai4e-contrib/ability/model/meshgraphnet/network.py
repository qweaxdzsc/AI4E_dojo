"""MeshGraphNet 的二维图网络实现。

网络只接受已经装配好的图特征；CylinderFlow 的节点类别、mask 和物理字段由
``application/spatiotemporal_pde/meshgraphnet`` 连接。
"""

from __future__ import annotations

import torch
from torch import nn

from .blocks import GraphDecoder, GraphEncoder, GraphProcessor


class MeshGraphNet(nn.Module):
    """编码节点/边、执行图处理并输出节点增量。"""

    structure_version = 2

    def __init__(
        self,
        node_input_dim: int = 11,
        edge_input_dim: int = 3,
        output_dim: int = 2,
        hidden_dim: int = 128,
        processor_layers: int = 15,
    ) -> None:
        super().__init__()
        self.encoder = GraphEncoder(node_input_dim, edge_input_dim, hidden_dim)
        self.processor = GraphProcessor(hidden_dim, processor_layers)
        self.decoder = GraphDecoder(hidden_dim, output_dim)

    def forward(
        self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor
    ) -> torch.Tensor:
        """编码图特征，经 Processor 更新后解码节点增量。"""
        nodes, edges = self.encoder(node_features, edge_features)
        nodes, _ = self.processor(nodes, edges, edge_index)
        return self.decoder(nodes)


def predict(model: MeshGraphNet, graph: dict[str, torch.Tensor]) -> torch.Tensor:
    """对已装配图执行无梯度节点预测。"""
    required = {"node_features", "edge_features", "edge_index"}
    if set(graph) != required:
        raise ValueError("MeshGraphNet 输入必须恰好包含 node_features、edge_features、edge_index")
    with torch.no_grad():
        return model(graph["node_features"], graph["edge_features"], graph["edge_index"])
