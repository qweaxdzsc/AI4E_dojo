"""物理坐标上的开放均匀 B 样条及张量积求值。"""

import numpy as np
import torch
from scipy.interpolate import BSpline

from ai4e_core.abilities.transform.trapezoid import physical_derivatives


def basis(coordinates, *, bounds, control_points, degree):
    """生成零、一、二阶物理导数；端点使用样条定义域内的单侧值。

    节点直接位于声明坐标区间，不再遗漏原仓库参数坐标到物理坐标缩放。
    SciPy 仅用于准备常量矩阵，训练对控制系数的梯度由 PyTorch 保留。
    """
    low, high = bounds
    if not 1 <= degree < control_points or not low < high:
        raise ValueError("样条次数、控制点数或定义域不合法")
    values = coordinates.detach().cpu().double().numpy()
    if not np.isfinite(values).all() or np.any(values < low) or np.any(values > high):
        raise ValueError("样条查询坐标超出定义域")
    knots = np.r_[
        np.repeat(low, degree),
        np.linspace(low, high, control_points - degree + 1),
        np.repeat(high, degree),
    ]
    spline = BSpline(knots, np.eye(control_points), degree, extrapolate=False)
    return tuple(
        torch.from_numpy(np.asarray(spline(values, nu=order)))
        if order <= degree
        else torch.zeros(len(values), control_points, dtype=torch.float64)
        for order in range(3)
    )


def prepare_points(sample, points, config):
    """任意配点的各轴矩阵，用于按点查询。"""
    return [
        basis(
            points[:, i], bounds=sample["bounds"][name], control_points=n, degree=config["degree"]
        )
        for i, (name, n) in enumerate(
            zip(sample["axis_names"], config["control_points"], strict=True)
        )
    ]


def prepare_grid(sample, config):
    """完整网格按轴准备，避免存储逐点 Kronecker 矩阵。"""
    return [
        basis(
            sample["axes"][name],
            bounds=sample["bounds"][name],
            control_points=n,
            degree=config["degree"],
        )
        for name, n in zip(sample["axis_names"], config["control_points"], strict=True)
    ]


def evaluate(coefficients, bases, *, points=None, mapping="identity", grid=False):
    """计算场和一二阶导数；grid 使用可分离轴收缩，不展开乘积矩阵。"""
    ndim = coefficients.ndim
    matrices = [[v.to(coefficients) for v in group] for group in bases]

    def contract(orders):
        b = [matrices[i][order] for i, order in enumerate(orders)]
        if ndim == 2:
            return b[0] @ coefficients @ b[1].T if grid else ((b[0] @ coefficients) * b[1]).sum(-1)
        if ndim != 3:
            raise ValueError("仅支持一维或二维空间样条场")
        if grid:
            value = torch.einsum("ai,ijk->ajk", b[0], coefficients)
            value = torch.einsum("bj,ajk->abk", b[1], value)
            return torch.einsum("ck,abk->abc", b[2], value)
        return torch.einsum("ni,ijk,nj,nk->n", b[0], coefficients, b[1], b[2])

    zero = [0] * ndim
    values = {"u": contract(zero)}
    for i, name in enumerate(("t", "x") if ndim == 2 else ("t", "eta", "xi")):
        order = zero.copy()
        order[i] = 1
        values[f"u_{name}"] = contract(order)
        if i:
            order[i] = 2
            values[f"u_{name}{name}"] = contract(order)
    if ndim == 3:
        values["u_xieta"] = contract([0, 1, 1])
        if mapping != "trapezoid" or points is None:
            raise ValueError("二维样条场必须提供梯形参考坐标")
        eta, xi = points[..., 1].to(coefficients), points[..., 2].to(coefficients)
        values.update(
            physical_derivatives(
                xi=xi,
                eta=eta,
                u_xi=values["u_xi"],
                u_eta=values["u_eta"],
                u_xixi=values["u_xixi"],
                u_xieta=values["u_xieta"],
                u_etaeta=values["u_etaeta"],
            )
        )
    return values
