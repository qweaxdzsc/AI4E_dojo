"""解析时空域、梯形映射及外法向；不依赖物理场或模型。"""

import torch


def physical_coordinates(points, mapping):
    """输入列为 t,x 或 t,eta,xi；返回 t,X 或 t,Y,X。"""
    if mapping == "identity":
        return points
    if mapping != "trapezoid" or points.shape[-1] != 3:
        raise ValueError("未知坐标映射或维度")
    t, eta, xi = points.unbind(-1)
    return torch.stack((t, eta, -1 + 0.5 * eta + xi * (2 - eta)), -1)


def boundary_axis(name, dimensions):
    """命名边界到参考轴与方向；不猜测未知边界。"""
    options = {"left": (dimensions - 1, -1), "right": (dimensions - 1, 1)}
    if dimensions == 3:
        options.update(bottom=(1, -1), top=(1, 1))
    if name not in options:
        raise ValueError(f"未知边界: {name}")
    return options[name]


def outward_normals(points, boundary, mapping):
    """返回物理空间法向，列顺序为 x 或 x,y。"""
    dimension = points.shape[-1] - 1
    result = points.new_zeros((len(points), dimension))
    axis, sign = boundary_axis(boundary, dimension + 1)
    if dimension == 1:
        result[:, 0] = sign
    elif axis == 1:
        result[:, 1] = sign
    else:
        result[:, 0] = sign
        if mapping == "trapezoid":
            result[:, 1] = 0.5
        result = result / result.norm(dim=-1, keepdim=True)
    return result


def validate_points(points, bounds, names):
    """校验参考域点，物理映射独立进行。"""
    if points.ndim != 2 or points.shape[1] != len(names) or not len(points):
        raise ValueError("采样点维度错误或为空")
    if not torch.isfinite(points).all():
        raise ValueError("采样点非有限")
    for i, name in enumerate(names):
        lo, hi = bounds[name]
        if not bool(((points[:, i] >= lo) & (points[:, i] <= hi)).all()):
            raise ValueError(f"{name}: 采样点超出定义域")
