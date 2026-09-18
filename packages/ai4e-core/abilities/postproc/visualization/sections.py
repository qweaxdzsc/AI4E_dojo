"""切片、剖切与等值提取；共同变换网格中的全部物理数组。"""

from __future__ import annotations

from typing import Any

import numpy as np

from .fields import derived_mesh, pyvista, scalar_mesh


def plane(origin: Any, normal: Any) -> tuple[np.ndarray, np.ndarray]:
    """校验物理平面并返回单位法向。"""
    origin, normal = np.asarray(origin, dtype=float), np.asarray(normal, dtype=float)
    if (
        origin.shape != (3,)
        or normal.shape != (3,)
        or not np.isfinite([origin, normal]).all()
        or not np.linalg.norm(normal)
    ):
        raise ValueError("平面需要有限三维原点与非零法向")
    return origin, normal / np.linalg.norm(normal)


def slice_mesh(mesh: Any, *, origin: Any, normal: Any) -> Any:
    """切开真实单元并插值全部字段；没有交点则失败。"""
    origin, normal = plane(origin, normal)
    result = pyvista().wrap(mesh).slice(origin=origin, normal=normal)
    if not result.n_cells:
        raise ValueError("切片与有效拓扑没有交点")
    return derived_mesh(
        result,
        operation="slice",
        parameters={
            "origin": origin.tolist(),
            "normal": normal.tolist(),
            "interpolation": "VTK cell interpolation",
        },
    )


def clip_mesh(mesh: Any, *, origin: Any, normal: Any, keep: str = "positive") -> Any:
    """保留平面正侧或负侧；返回独立网格。"""
    origin, normal = plane(origin, normal)
    if keep not in {"positive", "negative"}:
        raise ValueError("keep 必须为 positive 或 negative")
    result = pyvista().wrap(mesh).clip(origin=origin, normal=normal, invert=keep == "negative")
    if not result.n_cells:
        raise ValueError("剖切后无有效单元")
    return derived_mesh(
        result,
        operation="clip",
        parameters={
            "origin": origin.tolist(),
            "normal": normal.tolist(),
            "keep": keep,
            "interpolation": "VTK cell interpolation",
        },
    )


def contour_mesh(
    mesh: Any,
    *,
    field: str,
    values: Any,
    association: str = "point",
    component: str | int = "scalar",
    kind: str = "isosurface",
    cell_to_point: bool = False,
) -> Any:
    """体网格提取等值面、面网格提取等高线；单元插值须明确授权。"""
    mesh = pyvista().wrap(mesh)
    dimensions = {mesh.GetCell(i).GetCellDimension() for i in range(mesh.n_cells)}
    if (
        kind not in {"isosurface", "contour"}
        or not dimensions
        or (kind == "isosurface" and dimensions != {3})
        or (kind == "contour" and max(dimensions) > 2)
    ):
        raise ValueError("等值操作与网格维度不匹配")
    levels = np.asarray(values, dtype=float)
    if levels.ndim != 1 or not 1 <= len(levels) <= 256 or not np.isfinite(levels).all():
        raise ValueError("等值列表必须有限且含 1 到 256 项")
    source = scalar_mesh(mesh, field, association=association, component=component)
    if association == "cell":
        if not cell_to_point:
            raise ValueError("单元场等值提取须显式 cell_to_point=True")
        source = source.cell_data_to_point_data(pass_cell_data=True)
    result = source.contour(isosurfaces=levels, scalars="__post_scalar", preference="point")
    if not result.n_cells:
        raise ValueError("等值结果为空")
    return derived_mesh(
        result,
        operation=kind,
        parameters={
            "field": field,
            "values": levels.tolist(),
            "cell_to_point": cell_to_point,
            "interpolation": "VTK cell interpolation",
        },
    )
