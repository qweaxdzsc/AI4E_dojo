"""用精确坐标标出不与表面重合的体积点，不删点。"""

from __future__ import annotations

import numpy as np

from ai4e_core.base.events import traced


@traced("重合点标记")
def exterior_mask(volume_points: np.ndarray, surface_points: np.ndarray) -> np.ndarray:
    """标出体积点中不与任一表面点坐标精确重合的位置。

    ``True`` 表示不重合（后续可保留），``False`` 表示与表面坐标精确相同。
    极性与有效点 mask 一致。用坐标元组判断，不按距离阈值合并，不删点。

    Args:
        volume_points: 体积点，形状 ``(N, 3)``。
        surface_points: 表面点，形状 ``(M, 3)``。

    Returns:
        与体积点数等长的布尔 mask。

    Raises:
        ValueError: 数组不是三维点。
    """
    volume = _as_points_3d(volume_points, "体积点")
    surface = _as_points_3d(surface_points, "表面点")
    surface_set = {tuple(point) for point in surface}
    return np.fromiter(
        (tuple(point) not in surface_set for point in volume),
        dtype=bool,
        count=volume.shape[0],
    )


def _as_points_3d(array: np.ndarray, label: str) -> np.ndarray:
    """要求输入是 ``(N, 3)`` 点坐标。"""
    points = np.asarray(array, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"{label}形状不是 (N, 3): {getattr(array, 'shape', None)}")
    return points
