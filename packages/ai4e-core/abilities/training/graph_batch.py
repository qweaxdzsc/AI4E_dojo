"""变长图样本的拼接与局部索引交接。"""

from __future__ import annotations

import torch


def concatenate_graphs(samples: list[dict[str, torch.Tensor]]) -> dict[str, torch.Tensor]:
    """拼接变长图，自动偏移 ``edge_index`` 并返回节点/边 batch 标记。"""
    if not samples:
        raise ValueError("图批次不能为空")
    required = {"node_features", "edge_index", "edge_features"}
    if any(not required.issubset(sample) for sample in samples):
        raise ValueError("每个图样本必须包含 node_features、edge_index 和 edge_features")
    nodes: list[torch.Tensor] = []
    edges: list[torch.Tensor] = []
    edge_features: list[torch.Tensor] = []
    node_batches: list[torch.Tensor] = []
    edge_batches: list[torch.Tensor] = []
    offset = 0
    for batch_id, sample in enumerate(samples):
        node = sample["node_features"]
        edge = sample["edge_index"]
        feature = sample["edge_features"]
        if node.ndim != 2 or edge.ndim != 2 or edge.shape[0] != 2:
            raise ValueError("图节点或边索引形状错误")
        if feature.ndim != 2 or feature.shape[0] != edge.shape[1]:
            raise ValueError("边特征数量必须与边索引一致")
        if edge.numel() and (edge.min() < 0 or edge.max() >= node.shape[0]):
            raise ValueError("图边索引越界")
        nodes.append(node)
        edges.append(edge + offset)
        edge_features.append(feature)
        node_batches.append(
            torch.full((node.shape[0],), batch_id, dtype=torch.long, device=node.device)
        )
        edge_batches.append(
            torch.full((edge.shape[1],), batch_id, dtype=torch.long, device=edge.device)
        )
        offset += node.shape[0]
    return {
        "node_features": torch.cat(nodes, dim=0),
        "edge_index": torch.cat(edges, dim=1),
        "edge_features": torch.cat(edge_features, dim=0),
        "node_batch": torch.cat(node_batches, dim=0),
        "edge_batch": torch.cat(edge_batches, dim=0),
    }
