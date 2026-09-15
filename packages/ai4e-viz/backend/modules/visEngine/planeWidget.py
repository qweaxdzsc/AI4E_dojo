"""切面可视平面的几何与拖动算术；不执行切开，不接触会话。"""

import math

import vtk

from .sampling import pick_ray


HANDLE_NAMES = ("plane", "axis_x", "axis_y", "axis_z", "rotate")
HANDLE_COLORS = {
    "plane": (0.35, 0.62, 0.95),
    "axis_x": (0.90, 0.22, 0.22),
    "axis_y": (0.20, 0.78, 0.32),
    "axis_z": (0.28, 0.48, 0.95),
    "rotate": (0.95, 0.84, 0.22),
}
AXIS_VECTORS = {
    "axis_x": (1.0, 0.0, 0.0),
    "axis_y": (0.0, 1.0, 0.0),
    "axis_z": (0.0, 0.0, 1.0),
}


def _finite(values):
    point = [float(x) for x in values]
    if len(point) != 3 or not all(math.isfinite(x) for x in point):
        raise ValueError("invalid_plane_vector")
    return point


def _normalize(vector):
    length = math.sqrt(sum(x * x for x in vector))
    if length == 0:
        raise ValueError("zero_plane_normal")
    return [x / length for x in vector]


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def _add(a, b):
    return [a[i] + b[i] for i in range(3)]


def _scale(vector, factor):
    return [x * factor for x in vector]


def _extent(bounds):
    return max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4], 1e-6)


def _tangents(normal):
    helper = [1.0, 0.0, 0.0] if abs(normal[0]) < 0.9 else [0.0, 1.0, 0.0]
    tangent = _normalize(_cross(normal, helper))
    return tangent, _normalize(_cross(normal, tangent))


def align_plane_normal(origin, axis: str):
    """属性 X/Y/Z 只改法向，原点保持不动。"""
    mapping = {"x": [1.0, 0.0, 0.0], "y": [0.0, 1.0, 0.0], "z": [0.0, 0.0, 1.0]}
    if axis not in mapping:
        raise ValueError("invalid_plane_axis")
    return _finite(origin), mapping[axis]


def plane_widget_geometry(origin, normal, bounds):
    """按数据包围盒生成平面片、三轴手柄和旋转环。"""
    origin = _finite(origin)
    normal = _normalize(_finite(normal))
    size = _extent(bounds) * 0.55
    tangent, bitangent = _tangents(normal)
    start = _add(origin, _add(_scale(tangent, -0.5 * size), _scale(bitangent, -0.5 * size)))
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(start)
    plane.SetPoint1(_add(start, _scale(tangent, size)))
    plane.SetPoint2(_add(start, _scale(bitangent, size)))
    plane.SetXResolution(1)
    plane.SetYResolution(1)
    plane.Update()
    handles = {"plane": plane.GetOutput()}
    axis_length = size * 0.45
    for name, direction in AXIS_VECTORS.items():
        line = vtk.vtkLineSource()
        line.SetPoint1(origin)
        line.SetPoint2(_add(origin, _scale(direction, axis_length)))
        line.SetResolution(1)
        line.Update()
        handles[name] = line.GetOutput()
    ring = vtk.vtkRegularPolygonSource()
    ring.SetCenter(origin)
    ring.SetNormal(normal)
    ring.SetRadius(size * 0.32)
    ring.SetNumberOfSides(48)
    ring.SetGeneratePolygon(False)
    ring.Update()
    handles["rotate"] = ring.GetOutput()
    return handles


def _ray_direction(ray):
    direction = _sub(ray[1], ray[0])
    length = math.sqrt(sum(x * x for x in direction))
    if length == 0:
        raise ValueError("invalid_pick_ray")
    return _scale(direction, 1 / length)


def _closest_on_axis(ray, origin, axis):
    """射线到轴的最近点，用于沿 X/Y/Z 或法向拖动。"""
    axis = _normalize(axis)
    direction = _ray_direction(ray)
    start = _sub(ray[0], origin)
    denom = 1 - _dot(direction, axis) ** 2
    if abs(denom) < 1e-10:
        return _dot(start, axis)
    return (_dot(start, axis) - _dot(start, direction) * _dot(direction, axis)) / denom


def _ray_plane(ray, origin, normal):
    direction = _sub(ray[1], ray[0])
    denom = _dot(normal, direction)
    if abs(denom) < 1e-12:
        return None
    factor = _dot(normal, _sub(origin, ray[0])) / denom
    return _add(ray[0], _scale(direction, factor))


def _rotate_vector(vector, axis, angle):
    axis = _normalize(axis)
    cosine, sine = math.cos(angle), math.sin(angle)
    return _add(
        _add(_scale(vector, cosine), _scale(_cross(axis, vector), sine)),
        _scale(axis, _dot(axis, vector) * (1 - cosine)),
    )


def move_plane(origin, normal, handle, start_ray, end_ray):
    """根据手柄和两条射线计算新的原点和法向，不切开网格。"""
    origin = _finite(origin)
    normal = _normalize(_finite(normal))
    if handle not in HANDLE_NAMES:
        raise ValueError("invalid_plane_handle")
    if handle in AXIS_VECTORS:
        axis = AXIS_VECTORS[handle]
        delta = _closest_on_axis(end_ray, origin, axis) - _closest_on_axis(
            start_ray, origin, axis
        )
        return _add(origin, _scale(axis, delta)), normal
    if handle == "plane":
        delta = _closest_on_axis(end_ray, origin, normal) - _closest_on_axis(
            start_ray, origin, normal
        )
        return _add(origin, _scale(normal, delta)), normal
    start = _ray_plane(start_ray, origin, normal)
    end = _ray_plane(end_ray, origin, normal)
    if start is None or end is None:
        return origin, normal
    first, second = _sub(start, origin), _sub(end, origin)
    axis = _cross(first, second)
    if sum(x * x for x in axis) < 1e-16:
        return origin, normal
    angle = math.atan2(math.sqrt(sum(x * x for x in axis)), _dot(first, second))
    return origin, _normalize(_rotate_vector(normal, axis, angle))


def pick_plane_handle(handles: dict, ray):
    """在手柄网格上选最近命中，未命中返回空。"""
    best, distance = None, None
    for name, mesh in handles.items():
        hit = pick_ray(mesh, ray, "cell")
        if not hit.get("valid"):
            continue
        current = sum((hit["position"][i] - ray[0][i]) ** 2 for i in range(3))
        if distance is None or current < distance:
            best, distance = name, current
    return best
