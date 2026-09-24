"""可拆分为公开编码、处理和读出的基础消息传递图网络。"""

import torch
from torch import nn

from ..modules.graph_encoding import GraphEncoder, GraphReadout
from ..modules.graph_message_passing import GraphInteraction
from ..stages.graph import GraphProcessor


class GraphNetwork(nn.Module):
    """中立图网络；节点、边维度由调用方显式提供。"""

    def __init__(
        self,
        node_input_dim: int,
        edge_input_dim: int,
        output_dim: int,
        *,
        hidden_dim: int = 64,
        processor_layers: int = 3,
        aggregation: str = "sum",
        encoder: nn.Module | None = None,
        processor: nn.Module | None = None,
        readout: nn.Module | None = None,
    ) -> None:
        super().__init__()
        self.encoder = (
            encoder
            if encoder is not None
            else GraphEncoder(node_input_dim, edge_input_dim, hidden_dim)
        )
        self.processor = (
            processor
            if processor is not None
            else GraphProcessor(
                GraphInteraction(hidden_dim, hidden_dim, hidden_dim, aggregation=aggregation)
                for _ in range(processor_layers)
            )
        )
        self.readout = readout if readout is not None else GraphReadout(hidden_dim, output_dim)

    def forward(
        self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor
    ) -> torch.Tensor:
        """返回 [N,output_dim] 节点输出，不内置采样、损失或物理归一化。"""
        nodes, edges = self.encoder(node_features, edge_features)
        nodes, _ = self.processor(nodes, edges, edge_index)
        return self.readout(nodes)
