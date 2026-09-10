"""体积点到网格表面的有符号距离；先校验全部单元为支持的二维面。"""

from __future__ import annotations

import numpy as np
from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersCore import vtkImplicitPolyDataDistance

from ai4e_core.abilities.geometry.nearest import EPSILON, _as_points_3d
from ai4e_core.abilities.geometry.surface import prepare_surface, require_surface_mesh
from ai4e_core.base.events import traced

# 保留原模块的公开门禁入口，内部实现统一归入 surface。
__all__ = ["mesh_signed_distance", "require_surface_mesh"]


@traced("点到面距离")
def mesh_signed_distance(
    query_points: np.ndarray,
    surface: vtkDataObject,
    *,
    epsilon: float = EPSILON,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """计算查询点到网格表面的有符号距离、面上最近点和方向。

    必须先通过表面门禁。符号遵循输入绕序；只有朝外定向的闭合表面才可
    解释为外正内负，开放表面或反向绕序不保证物理内外。
    方向为 ``(查询点 - 面上最近点) / (|距离| + epsilon)``。不改写输入网格，
    也不把失败降级为点到点。

    Args:
        query_points: 查询点，形状 ``(N, 3)``。
        surface: 带二维面单元的表面 VTK 对象。
        epsilon: 距离为零时避免除零的偏置。

    Returns:
        ``(有符号距离, 面上最近点, 方向)``，首维均为 ``N``。
    """
    prepared = prepare_surface(surface)
    query = _as_points_3d(query_points, "查询点")
    if query.shape[0] == 0:
        empty = np.zeros((0, 3), dtype=np.float64)
        return np.zeros(0, dtype=np.float64), empty, empty

    poly = prepared.poly

    implicit = vtkImplicitPolyDataDistance()
    implicit.SetInput(poly)

    signed = np.empty(query.shape[0], dtype=np.float64)
    closest = np.empty((query.shape[0], 3), dtype=np.float64)
    closest_point = [0.0, 0.0, 0.0]
    for index, point in enumerate(query):
        signed[index] = implicit.EvaluateFunctionAndGetClosestPoint(point.tolist(), closest_point)
        closest[index] = closest_point

    offset = query - closest
    directions = offset / (np.abs(signed)[:, np.newaxis] + epsilon)
    return signed, closest, directions
