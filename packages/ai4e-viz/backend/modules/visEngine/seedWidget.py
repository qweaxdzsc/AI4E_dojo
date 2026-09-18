"""流线种子手柄几何（本期不绑定拖动；函数保留，工作台不再挂手柄）。"""

import math

from .planeWidget import (
    HANDLE_NAMES,
    AXIS_VECTORS,
    move_plane,
    plane_widget_geometry,
    pick_plane_handle,
)


def _finite(values):
    point = [float(x) for x in values]
    if len(point) != 3 or not all(math.isfinite(x) for x in point):
        raise ValueError("invalid_seed_vector")
    return point


def _sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _add(a, b):
    return [a[i] + b[i] for i in range(3)]


def _scale(vector, factor):
    return [x * factor for x in vector]


def _length(vector):
    return math.sqrt(sum(x * x for x in vector))


def seed_widget_geometry(kind, params, bounds):
    """球体只给三平移轴；线段和平面给六轴。"""
    if kind == "sphere":
        origin = _finite(params.get("seed_center", [0, 0, 0]))
        handles = plane_widget_geometry(origin, [0, 0, 1], bounds)
        return {name: handles[name] for name in ("axis_x", "axis_y", "axis_z")}
    if kind == "plane":
        return plane_widget_geometry(
            params.get("seed_origin", [0, 0, 0]),
            params.get("seed_normal", [0, 0, 1]),
            bounds,
        )
    if kind != "line":
        raise ValueError("invalid_seed_widget")
    start = _finite(params.get("seed_start", [0, 0, 0]))
    end = _finite(params.get("seed_end", [0, 1, 0]))
    origin = [(start[i] + end[i]) / 2 for i in range(3)]
    direction = _sub(end, start)
    if _length(direction) == 0:
        direction = [0, 1, 0]
    return plane_widget_geometry(origin, direction, bounds)


def move_seed(kind, params, handle, start_ray, end_ray):
    """把平面手柄算术映射回种子参数。"""
    if handle not in HANDLE_NAMES:
        raise ValueError("invalid_plane_handle")
    if kind == "sphere":
        if handle not in AXIS_VECTORS:
            raise ValueError("invalid_sphere_handle")
        origin, _ = move_plane(
            params.get("seed_center", [0, 0, 0]), [0, 0, 1], handle, start_ray, end_ray
        )
        return {"seed_center": origin}
    if kind == "plane":
        origin, normal = move_plane(
            params.get("seed_origin", [0, 0, 0]),
            params.get("seed_normal", [0, 0, 1]),
            handle,
            start_ray,
            end_ray,
        )
        return {"seed_origin": origin, "seed_normal": normal}
    start = _finite(params.get("seed_start", [0, 0, 0]))
    end = _finite(params.get("seed_end", [0, 1, 0]))
    origin = [(start[i] + end[i]) / 2 for i in range(3)]
    direction = _sub(end, start)
    half = _length(direction) / 2 or 0.5
    if _length(direction) == 0:
        direction = [0, 1, 0]
    origin, normal = move_plane(origin, direction, handle, start_ray, end_ray)
    offset = _scale(normal, half)
    return {"seed_start": _sub(origin, offset), "seed_end": _add(origin, offset)}


__all__ = ["seed_widget_geometry", "move_seed", "pick_plane_handle"]
