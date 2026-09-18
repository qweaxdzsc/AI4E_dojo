"""线段提取草稿两端手柄；只回填点位，不采样。"""

import math

from .planeWidget import AXIS_VECTORS, move_plane, plane_widget_geometry
from .sampling import pick_ray


def _finite(values):
    point = [float(x) for x in values]
    if len(point) != 3 or not all(math.isfinite(x) for x in point):
        raise ValueError("invalid_line_point")
    return point


def _sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _add(a, b):
    return [a[i] + b[i] for i in range(3)]


def _scale(vector, factor):
    return [x * factor for x in vector]


def _length(vector):
    return math.sqrt(sum(x * x for x in vector))


def line_frame(point1, point2):
    """用中点和方向描述线段，复用平面手柄算术。"""
    start, end = _finite(point1), _finite(point2)
    origin = [(start[i] + end[i]) / 2 for i in range(3)]
    direction = _sub(end, start)
    half = _length(direction) / 2 or 0.5
    if _length(direction) == 0:
        direction = [1, 0, 0]
    return origin, direction, half


def line_widget_geometry(point1, point2, bounds):
    """线段两端共用六轴，拖动后仍是一条线段。"""
    origin, direction, _ = line_frame(point1, point2)
    return plane_widget_geometry(origin, direction, bounds)


def move_line(point1, point2, handle, start_ray, end_ray):
    """平移或旋转整条线段，保持长度。"""
    origin, direction, half = line_frame(point1, point2)
    origin, normal = move_plane(origin, direction, handle, start_ray, end_ray)
    offset = _scale(normal, half)
    return _sub(origin, offset), _add(origin, offset)


def pick_line_handle(handles, ray):
    """命中平移或旋转手柄。"""
    best, distance = None, None
    for name, mesh in handles.items():
        if name not in AXIS_VECTORS and not name.startswith("rotate_"):
            continue
        hit = pick_ray(mesh, ray, "cell")
        if not hit.get("valid"):
            continue
        current = sum((hit["position"][i] - ray[0][i]) ** 2 for i in range(3))
        if distance is None or current < distance:
            best, distance = name, current
    return best
