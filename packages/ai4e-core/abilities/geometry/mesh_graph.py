"""中立的二维/多维网格图原语。

本模块只处理坐标、单元和图边，不解释数据集名称、物理字段或节点类别。
单元边会先生成无向唯一边，再展开成双向有向边，便于消息传递网络使用。
"""

from __future__ import annotations

import torch


def triangles_to_edges(triangles: torch.Tensor, *, bidirectional: bool = True) -> torch.Tensor:
    """把 ``(n, 3)`` 三角形连接转换为 ``(2, e)`` 的边索引。

    返回的边按字典序稳定排序，并删除同一无向边的重复项。输入只接受整型
    三角形索引，不会根据点坐标猜测拓扑。
    """
    if triangles.ndim != 2 or triangles.shape[1] != 3:
        raise ValueError("triangles 必须是 (n, 3) 索引数组")
    if triangles.dtype not in (torch.int32, torch.int64):
        raise ValueError("triangles 必须使用整型索引")
    if triangles.numel() == 0:
        return torch.empty((2, 0), dtype=torch.long, device=triangles.device)
    if (triangles < 0).any():
        raise ValueError("三角形索引不能为负")

    edges = torch.cat([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]], dim=0).to(
        torch.long
    )
    edges = torch.sort(edges, dim=1).values
    edges = torch.unique(edges, dim=0, sorted=True)
    if bidirectional:
        edges = torch.cat([edges, edges[:, [1, 0]]], dim=0)
    return edges.t().contiguous()


def cells_to_edges(
    cells: torch.Tensor | list[torch.Tensor], *, bidirectional: bool = True
) -> torch.Tensor:
    """从等宽或混合 VTK 单元提取单元真实边。

    三角形、四边形按闭合边界取边；四面体、六面体、楔体和金字塔按
    VTK 标准局部边表取边。这里不会把一个单元的所有节点两两相连，因此
    六面体不会被错误变成完全图。
    """
    groups = [cells] if isinstance(cells, torch.Tensor) else list(cells)
    tables = {
        2: ((0, 1),),
        3: ((0, 1), (1, 2), (2, 0)),
        4: ((0, 1), (1, 2), (2, 3), (3, 0)),
        5: ((0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)),
        6: ((0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)),
        8: (
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ),
    }
    pieces = []
    device = groups[0].device if groups else torch.device("cpu")
    for group in groups:
        if group.ndim != 2 or group.dtype not in (torch.int32, torch.int64):
            raise ValueError("cells 必须是二维整型索引数组")
        if group.numel() and (group < 0).any():
            raise ValueError("单元索引不能为负")
        table = tables.get(group.shape[1])
        if table is None:
            raise ValueError(f"不支持 {group.shape[1]} 节点单元")
        pieces.extend(group[:, pair] for pair in table)
    if not pieces:
        return torch.empty((2, 0), dtype=torch.long, device=device)
    edges = torch.cat(pieces, dim=0).long()
    edges = torch.sort(edges, dim=1).values
    edges = torch.unique(edges, dim=0, sorted=True)
    if bidirectional:
        edges = torch.cat((edges, edges[:, [1, 0]]), dim=0)
    return edges.t().contiguous()


def induced_subgraph(
    edge_index: torch.Tensor, node_ids: torch.Tensor, *, node_count: int | None = None
) -> tuple[torch.Tensor, torch.Tensor]:
    """按保留节点构造诱导子图，返回局部边和局部到原节点的映射。"""
    if edge_index.ndim != 2 or edge_index.shape[0] != 2:
        raise ValueError("edge_index 必须是 (2, e)")
    ids = torch.as_tensor(node_ids, dtype=torch.long, device=edge_index.device)
    if ids.ndim != 1 or len(ids.unique()) != len(ids) or (ids < 0).any():
        raise ValueError("node_ids 必须是一维、不重复的非负整数")
    inferred = int(edge_index.max().item()) + 1 if edge_index.numel() else 0
    count = inferred if node_count is None else int(node_count)
    if len(ids) and ids.max().item() >= count:
        raise ValueError("node_ids 超出节点范围")
    remap = torch.full((count,), -1, dtype=torch.long, device=edge_index.device)
    remap[ids] = torch.arange(len(ids), device=edge_index.device)
    selected = (remap[edge_index[0]] >= 0) & (remap[edge_index[1]] >= 0)
    return remap[edge_index[:, selected]], ids


def edge_features(positions: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
    """根据节点坐标计算有向边的相对位置和欧氏距离。"""
    if positions.ndim != 2 or edge_index.ndim != 2 or edge_index.shape[0] != 2:
        raise ValueError("positions 必须是 (n, d)，edge_index 必须是 (2, e)")
    if edge_index.numel() and (edge_index.min() < 0 or edge_index.max() >= positions.shape[0]):
        raise ValueError("edge_index 超出节点范围")
    source, target = edge_index
    # 有向边特征使用 sender - receiver，和消息传递的 source/target 语义一致。
    delta = positions[source] - positions[target]
    distance = torch.linalg.vector_norm(delta, dim=-1, keepdim=True)
    return torch.cat([delta, distance], dim=-1)


def vtk_cell_edges(mesh) -> torch.Tensor:
    """从 VTK 数据对象的真实单元边生成稳定双向边索引。

    体单元优先使用 VTK 自身的局部边定义；没有显式边的线和二维多边形按点序闭合。
    本函数不解释物理域、数据集或模型名称。
    """
    edges: set[tuple[int, int]] = set()
    for cell_index in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(cell_index)
        count = cell.GetNumberOfEdges()
        if count:
            for edge_index in range(count):
                edge = cell.GetEdge(edge_index)
                if edge.GetNumberOfPoints() != 2:
                    raise ValueError("VTK 单元边必须包含两个端点")
                left, right = int(edge.GetPointId(0)), int(edge.GetPointId(1))
                if left != right:
                    edges.add((min(left, right), max(left, right)))
            continue
        points = [int(cell.GetPointId(i)) for i in range(cell.GetNumberOfPoints())]
        if len(points) == 2:
            edges.add((min(points), max(points)))
        elif len(points) > 2:
            for left, right in zip(points, points[1:] + points[:1], strict=True):
                if left != right:
                    edges.add((min(left, right), max(left, right)))
    ordered = sorted(edges)
    if not ordered:
        return torch.empty((2, 0), dtype=torch.long)
    values = torch.tensor(ordered, dtype=torch.long)
    return torch.cat((values, values[:, [1, 0]]), dim=0).t().contiguous()
