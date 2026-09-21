"""二维连续性离散：交错通量差分及三角形分片线性梯度。

速度须处于同一物理或一致无量纲空间；调用方提供来源相符的网格位置和有效域。
"""

import torch


def staggered_divergence(velocity, spacing=(1.0, 1.0)):
    """对 (..., X, Y, 2) 面速度求前向通量散度，输出 (..., X-1, Y-1)。"""
    if velocity.shape[-1] != 2 or min(velocity.shape[-3:-1]) < 2:
        raise ValueError("速度必须是至少2×2网格的二维分量")
    dx, dy = spacing
    if dx <= 0 or dy <= 0:
        raise ValueError("网格间距必须为正")
    return (velocity[..., 1:, :-1, 0] - velocity[..., :-1, :-1, 0]) / dx + (
        velocity[..., :-1, 1:, 1] - velocity[..., :-1, :-1, 1]
    ) / dy


def triangle_geometry(position, cells):
    """返回三角形梯度变换和面积；拒绝退化或非法连接关系。"""
    if position.ndim != 2 or position.shape[1] != 2 or cells.ndim != 2 or cells.shape[1] != 3:
        raise ValueError("需要二维节点与三角连接关系")
    if not torch.isfinite(position).all() or cells.numel() == 0:
        raise ValueError("坐标非法或网格为空")
    if cells.min() < 0 or cells.max() >= len(position):
        raise ValueError("三角形节点编号越界")
    points = position[cells]
    edges = points[:, 1:] - points[:, :1]
    determinant = torch.linalg.det(edges)
    if (determinant.abs() <= torch.finfo(position.dtype).eps * edges.square().sum((-2, -1))).any():
        raise ValueError("存在退化三角形")
    return torch.linalg.inv(edges), determinant.abs() / 2


def triangle_gradient(values, cells, inverse):
    """节点值 (..., N, C) 返回 (..., triangles, C, xy) 的可微梯度。"""
    sampled = values[..., cells, :]
    differences = sampled[..., 1:, :] - sampled[..., :1, :]
    return torch.einsum("kij,...kjc->...kci", inverse, differences)


def triangle_divergence(velocity, cells, inverse):
    """二维节点速度的单元散度，不声称等同于来源求解器离散。"""
    if velocity.shape[-1] != 2:
        raise ValueError("连续性需要两个速度分量")
    gradient = triangle_gradient(velocity, cells, inverse)
    return gradient[..., 0, 0] + gradient[..., 1, 1]


def weighted_mean_square(values, weights):
    """有效域加权均方；空域或非法权重明确失败。"""
    weights = torch.broadcast_to(weights, values.shape)
    if not torch.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("权重非法或有效域为空")
    if not torch.isfinite(values).all():
        raise ValueError("参与残差计算的值非有限")
    return (values.square() * weights).sum() / weights.sum()
