"""箭头与流线计算；显式矢量归属、种子和积分口径。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from .fields import derived_mesh, field_values, pyvista
from .sections import plane


def seed_points(
    *,
    kind: str = "line",
    count: int = 20,
    start: Any = None,
    end: Any = None,
    center: Any = None,
    radius: float = 1.0,
    normal: Any = (1, 0, 0),
    width: float = 1.0,
    height: float = 1.0,
    points: Any = None,
) -> Any:
    """生成确定性点、线、平面或球体种子，不消耗调用者随机流。"""
    pv = pyvista()
    if isinstance(count, bool) or int(count) != count or count < 1:
        raise ValueError("种子数量必须为正整数")
    if kind == "points":
        values = np.asarray(points, dtype=float)
    elif kind == "line":
        a, _ = plane(start, (1, 0, 0))
        b, _ = plane(end, (1, 0, 0))
        values = np.linspace(a, b, count)
    elif kind == "sphere":
        center, _ = plane(center, normal)
        if not np.isfinite(radius) or radius <= 0:
            raise ValueError("种子半径必须为正数")
        rng = np.random.default_rng(0)
        directions = rng.normal(size=(count, 3))
        directions /= np.linalg.norm(directions, axis=1)[:, None]
        values = center + radius * rng.random(count)[:, None] ** (1 / 3) * directions
    elif kind == "plane":
        center, n = plane(center, normal)
        if not np.isfinite([width, height]).all() or min(width, height) <= 0:
            raise ValueError("种子平面尺寸须为正数")
        axis = np.eye(3)[np.argmin(np.abs(n))]
        u = np.cross(n, axis)
        u /= np.linalg.norm(u)
        v = np.cross(n, u)
        side = int(np.ceil(np.sqrt(count)))
        xy = (
            np.array(np.meshgrid(np.linspace(-0.5, 0.5, side), np.linspace(-0.5, 0.5, side)))
            .reshape(2, -1)
            .T[:count]
        )
        values = center + xy[:, :1] * width * u + xy[:, 1:] * height * v
    else:
        raise ValueError("未知种子类型")
    if values.ndim != 2 or values.shape[1] != 3 or not len(values) or not np.isfinite(values).all():
        raise ValueError("种子必须是非空有限三维点")
    return pv.PolyData(values)


def _vector_mesh(mesh, field, association, cell_to_point):
    mesh = pyvista().wrap(mesh).copy(deep=True)
    field_values(mesh, field, association=association, component="vector")
    if association == "cell":
        if not cell_to_point:
            raise ValueError("矢量单元场须显式转换到点")
        mesh = mesh.cell_data_to_point_data(pass_cell_data=True)
    return mesh


def glyph_mesh(
    mesh: Any,
    *,
    field: str,
    association: str = "point",
    stride: int = 1,
    scale: float = 0.1,
    cell_to_point: bool = False,
) -> Any:
    """按固定间隔绘制箭头，保留完整矢量和独立着色数组。"""
    mesh = _vector_mesh(mesh, field, association, cell_to_point)
    if (
        isinstance(stride, bool)
        or int(stride) != stride
        or stride < 1
        or not np.isfinite(scale)
        or scale <= 0
    ):
        raise ValueError("箭头间隔与比例必须为正数")
    points = pyvista().PolyData(mesh.points[::stride].copy())
    for name, values in mesh.field_data.items():
        points.field_data[name] = values.copy()
    for name, values in mesh.point_data.items():
        points.point_data[name] = values[::stride].copy()
    result = points.glyph(orient=field, scale=field, factor=scale)
    # vtkGlyph3D 把方向数组改名为 GlyphVector，恢复显式字段名供独立着色。
    result.point_data[field] = result.point_data["GlyphVector"].copy()
    return derived_mesh(
        result,
        operation="glyph",
        parameters={
            "field": field,
            "stride": stride,
            "scale": scale,
            "cell_to_point": cell_to_point,
        },
    )


def streamline_mesh(
    mesh: Any,
    *,
    field: str,
    seeds: Any,
    association: str = "point",
    direction: str = "both",
    length: float = 1.0,
    step: float = 0.01,
    max_steps: int = 4000,
    surface: bool = False,
    cell_to_point: bool = False,
) -> Any:
    """积分真实拓扑上的矢量场；表面模式显式投影到切平面。"""
    mesh = _vector_mesh(mesh, field, association, cell_to_point)
    dimensions = {mesh.GetCell(i).GetCellDimension() for i in range(mesh.n_cells)}
    if not dimensions or (not surface and dimensions != {3}) or (surface and dimensions != {2}):
        raise ValueError("流线模式与体/面拓扑不匹配")
    if (
        direction not in {"both", "forward", "backward"}
        or not np.isfinite([length, step]).all()
        or min(length, step) <= 0
        or max_steps < 1
    ):
        raise ValueError("非法流线积分参数")
    if surface:
        mesh = mesh.extract_surface().compute_normals(
            point_normals=True, cell_normals=False, split_vertices=False
        )
        vector = np.array(mesh.point_data[field], copy=True)
        normals = mesh.point_data["Normals"]
        mesh.point_data[field] = vector - np.sum(vector * normals, axis=1)[:, None] * normals
    source = seed_points(**seeds) if isinstance(seeds, Mapping) else pyvista().wrap(seeds)
    if not source.n_points:
        raise ValueError("流线种子为空")
    result = mesh.streamlines_from_source(
        source,
        vectors=field,
        integration_direction=direction,
        surface_streamlines=surface,
        max_length=length,
        initial_step_length=step,
        min_step_length=step / 100,
        max_step_length=step * 10,
        step_unit="l",
        max_steps=max_steps,
        compute_vorticity=False,
        interpolator_type="cell",
    )
    if not result.n_cells:
        raise ValueError("流线为空，请检查种子是否位于有效场中")
    for name, values in mesh.field_data.items():
        result.field_data[name] = values.copy()
    return derived_mesh(
        result,
        operation="streamline",
        parameters={
            "field": field,
            "direction": direction,
            "length": length,
            "step": step,
            "surface_projection": surface,
            "cell_to_point": cell_to_point,
            "seeds": np.asarray(source.points).tolist(),
        },
    )
