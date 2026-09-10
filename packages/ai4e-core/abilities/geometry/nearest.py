"""体积点到最近表面顶点的非负距离与方向。"""

from __future__ import annotations

import numpy as np
from sklearn.neighbors import NearestNeighbors

from ai4e_core.base.events import traced

EPSILON = 1e-8


@traced("点到最近顶点")
def nearest_vertex_distance_and_direction(
    query_points: np.ndarray,
    boundary_points: np.ndarray,
    *,
    epsilon: float = EPSILON,
) -> tuple[np.ndarray, np.ndarray]:
    """按最近表面顶点计算非负欧氏距离和方向。

    这是点云 1-NN，不看单元，也不是点到面的有符号距离。方向为
    ``(查询点 - 最近顶点) / (距离 + epsilon)``，与功能表第 15 项一致。

    Args:
        query_points: 查询点，形状 ``(N, 3)``。
        boundary_points: 表面顶点，形状 ``(M, 3)``。
        epsilon: 距离为零时避免除零的偏置，默认 ``1e-8``。

    Returns:
        ``(距离, 方向)``。距离形状 ``(N,)`` 且非负；方向形状 ``(N, 3)``。

    Raises:
        ValueError: 数组不是三维点，或边界点为空。
    """
    query = _as_points_3d(query_points, "查询点")
    boundary = _as_points_3d(boundary_points, "边界点")
    if boundary.shape[0] == 0:
        raise ValueError("边界点为空")
    if query.shape[0] == 0:
        return np.zeros(0, dtype=np.float64), np.zeros((0, 3), dtype=np.float64)

    # 等距点的选择会改变方向；锁定官方所用近邻实现及版本，不能只对比距离。
    distances, indices = NearestNeighbors(n_neighbors=1).fit(boundary).kneighbors(query)
    distances = distances.reshape(-1)
    offset = query - boundary[indices[:, 0]]
    directions = offset / (distances[:, np.newaxis] + epsilon)
    return distances, directions


def _as_points_3d(array: np.ndarray, label: str) -> np.ndarray:
    """要求输入是 ``(N, 3)`` 点坐标。"""
    points = np.asarray(array, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"{label}形状不是 (N, 3): {getattr(array, 'shape', None)}")
    return points
