"""静态单域或多域 MeshGraphNet 外壳；各域网络参数彼此独立。"""

from __future__ import annotations

import torch
from torch import nn

from .network import MeshGraphNet


class StaticMeshGraphNet(nn.Module):
    """按中立域声明构造多个独立 MeshGraphNet 子网络。"""

    structure_version = "static-multidomain-v1"

    def __init__(
        self,
        *,
        domains: dict[str, dict],
        hidden_dim: int = 128,
        processor_layers: int = 15,
    ) -> None:
        super().__init__()
        if not domains:
            raise ValueError("静态 MeshGraphNet 至少需要一个域")
        self.layouts = {name: dict(value) for name, value in domains.items()}
        self.processor_layers = int(processor_layers)
        self.networks = nn.ModuleDict(
            {
                name: MeshGraphNet(
                    node_input_dim=int(spec["node_input_dim"]),
                    edge_input_dim=int(spec["edge_input_dim"]),
                    output_dim=int(spec["output_dim"]),
                    hidden_dim=int(hidden_dim),
                    processor_layers=self.processor_layers,
                )
                for name, spec in self.layouts.items()
            }
        )

    def forward(self, graphs: dict[str, dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
        """分别执行各域图网络，返回包含 halo 节点的域输出。"""
        if not graphs or set(graphs) - set(self.networks):
            raise ValueError("图输入包含未知域或为空")
        return {
            name: self.networks[name](
                graph["node_features"], graph["edge_features"], graph["edge_index"]
            )
            for name, graph in graphs.items()
        }
