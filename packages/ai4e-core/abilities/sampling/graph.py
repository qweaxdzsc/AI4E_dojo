"""通用图核心分区与 halo 扩展，不解释模型或物理字段。"""

from __future__ import annotations

from collections import deque

import torch


def core_partitions(
    edge_index: torch.Tensor, node_count: int, max_nodes: int
) -> list[torch.Tensor]:
    """按稳定 BFS 顺序划分互斥核心块，并完整覆盖全部节点。"""
    if node_count < 1 or max_nodes < 1:
        raise ValueError("节点数和核心块上限必须为正")
    adjacency = _adjacency(edge_index, node_count)
    return _core_partitions(adjacency, max_nodes, edge_index.device)


def _core_partitions(
    adjacency: list[list[int]], max_nodes: int, device: torch.device
) -> list[torch.Tensor]:
    """复用已校验邻接表生成核心块，避免大图重复展开边。"""
    node_count = len(adjacency)
    unseen = set(range(node_count))
    result = []
    while unseen:
        queue = deque([min(unseen)])
        chosen = []
        queued = set(queue)
        while queue and len(chosen) < max_nodes:
            node = queue.popleft()
            if node not in unseen:
                continue
            unseen.remove(node)
            chosen.append(node)
            for neighbor in adjacency[node]:
                if neighbor in unseen and neighbor not in queued:
                    queue.append(neighbor)
                    queued.add(neighbor)
        # 非连通孤点或本连通分量已耗尽时，从最小剩余节点续填。
        while unseen and len(chosen) < max_nodes:
            node = min(unseen)
            unseen.remove(node)
            chosen.append(node)
        result.append(torch.tensor(chosen, dtype=torch.long, device=device))
    return result


def expand_halo(
    edge_index: torch.Tensor, core: torch.Tensor, node_count: int, hops: int
) -> tuple[torch.Tensor, torch.Tensor]:
    """扩展指定跳数的 halo，返回子图节点和其中核心节点的布尔 mask。"""
    if hops < 0:
        raise ValueError("halo 跳数不能为负")
    core = torch.as_tensor(core, dtype=torch.long, device=edge_index.device)
    if core.ndim != 1 or not len(core) or len(core.unique()) != len(core):
        raise ValueError("核心节点必须是一维非空不重复索引")
    adjacency = _adjacency(edge_index, node_count)
    return _expand_halo(adjacency, core, hops)


def _expand_halo(
    adjacency: list[list[int]], core: torch.Tensor, hops: int
) -> tuple[torch.Tensor, torch.Tensor]:
    """在已校验邻接表上扩展 halo。"""
    selected = set(map(int, core.tolist()))
    frontier = set(selected)
    for _ in range(hops):
        frontier = {n for node in frontier for n in adjacency[node]} - selected
        selected.update(frontier)
    nodes = torch.tensor(sorted(selected), dtype=torch.long, device=core.device)
    core_set = set(map(int, core.tolist()))
    mask = torch.tensor([int(node) in core_set for node in nodes], device=core.device)
    return nodes, mask


def partition_with_halo(
    edge_index: torch.Tensor, node_count: int, max_nodes: int, hops: int
) -> list[dict[str, torch.Tensor]]:
    """生成核心互斥、halo 可重叠的完整图分区声明；邻接表只构造一次。"""
    if node_count < 1 or max_nodes < 1:
        raise ValueError("节点数和核心块上限必须为正")
    if hops < 0:
        raise ValueError("halo 跳数不能为负")
    adjacency = _adjacency(edge_index, node_count)
    return [
        {"core_ids": core, "node_ids": nodes, "core_mask": mask}
        for core in _core_partitions(adjacency, max_nodes, edge_index.device)
        for nodes, mask in [_expand_halo(adjacency, core, hops)]
    ]


def _adjacency(edge_index: torch.Tensor, node_count: int) -> list[list[int]]:
    if edge_index.ndim != 2 or edge_index.shape[0] != 2:
        raise ValueError("edge_index 必须是 (2, e)")
    if edge_index.numel() and (edge_index.min() < 0 or edge_index.max() >= node_count):
        raise ValueError("edge_index 超出节点范围")
    adjacency = [set() for _ in range(node_count)]
    for source, target in edge_index.t().tolist():
        if source != target:
            adjacency[source].add(target)
            adjacency[target].add(source)
    return [sorted(values) for values in adjacency]
