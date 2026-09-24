"""可独立调用的顺序图处理段，不持有领域或运行状态。"""

from collections.abc import Iterable

import torch
from torch import nn


class GraphProcessor(nn.Module):
    """注册显式给定的图交互层；层之间传递节点和边状态。"""

    def __init__(self, blocks: Iterable[nn.Module]) -> None:
        super().__init__()
        self.blocks = nn.ModuleList(blocks)
        if not self.blocks:
            raise ValueError("图处理段至少需要一个交互块")

    def forward(
        self, nodes: torch.Tensor, edges: torch.Tensor, edge_index: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """按顺序执行交互层并保留节点、边身份。"""
        for block in self.blocks:
            nodes, edges = block(nodes, edges, edge_index)
        return nodes, edges
