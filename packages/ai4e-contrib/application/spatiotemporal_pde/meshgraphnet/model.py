"""MeshGraphNet 模型与 CylinderFlow 图字段的局部连接。"""

from __future__ import annotations

import torch
from torch import nn

from ai4e_contrib.ability.model.meshgraphnet import MeshGraphNet
from ai4e_contrib.application.datasets.cylinder_flow.adapter import graph_sample
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer


class CylinderFlowModel(nn.Module):
    """绑定 DeepMind CylinderFlow 输入/输出归一化的模型连接。"""

    structure_version = 2

    def __init__(self, network: MeshGraphNet) -> None:
        super().__init__()
        self.network = network
        self.node_normalizer = RunningNormalizer(11)
        self.edge_normalizer = RunningNormalizer(3)
        self.output_normalizer = RunningNormalizer(2)

    def forward(
        self,
        node_features: torch.Tensor,
        edge_features: torch.Tensor,
        edge_index: torch.Tensor,
        *,
        accumulate: bool = False,
    ) -> torch.Tensor:
        """归一化节点与边，再调用 MeshGraphNet 预测归一化增量。"""
        nodes = self.node_normalizer(node_features, accumulate=accumulate)
        edges = self.edge_normalizer(edge_features, accumulate=accumulate)
        return self.network(nodes, edges, edge_index)

    def normalize_target(self, target: torch.Tensor, *, accumulate: bool = False) -> torch.Tensor:
        """按输出统计归一化监督增量。"""
        return self.output_normalizer(target, accumulate=accumulate)

    def inverse_output(self, value: torch.Tensor) -> torch.Tensor:
        """把模型输出还原为物理速度增量。"""
        return self.output_normalizer.inverse(value)


def build_model(config: dict) -> CylinderFlowModel:
    """按配置构造 CylinderFlow 模型连接。"""
    model = config.get("model", config)
    return CylinderFlowModel(
        MeshGraphNet(
            node_input_dim=11,
            edge_input_dim=3,
            output_dim=2,
            hidden_dim=int(model.get("hidden_dim", 128)),
            processor_layers=int(model.get("processor_layers", 15)),
        )
    )


def build_graph(sample: dict) -> dict[str, torch.Tensor]:
    """把 CylinderFlow 物理帧映射为中立图字段。"""
    return graph_sample(sample)
