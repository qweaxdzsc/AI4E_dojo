"""选定梯形实验的参数空间样条矩阵；保留源代码的递推与 FP32 端点行为。

来源 PI-BSNet 40ffb623，diffusion_trapezoid.ipynb 的数值函数。
这里的导数未作物理尺度换算，不可当作通用物理样条导数库使用。
"""

from functools import lru_cache

import numpy as np
import torch


def BsFun(i, d, t, knots):
    """原一基索引的 Cox 递推，末端为半开区间。"""
    if d == 0:
        return 1.0 if knots[i - 1] <= t < knots[i] else 0.0
    denomA = knots[d + i - 1] - knots[i - 1]
    denomB = knots[d + i] - knots[i]
    a_val = 0 if denomA == 0 else (t - knots[i - 1]) / denomA
    b_val = 0 if denomB == 0 else (knots[d + i] - t) / denomB
    return a_val * BsFun(i, d - 1, t, knots) + b_val * BsFun(i + 1, d - 1, t, knots)


def build_bspline_basis(n_cp, d, Nparam):
    """保留 FP32 累加参数坐标和末值基的单项覆盖。"""
    if not 2 <= d < n_cp or Nparam < 2:
        raise ValueError("样条次数、控制网格或查询点数无效")
    n_knots = n_cp + d + 1
    knots = np.zeros(n_knots)
    for i in range(d + 1, n_knots - d - 1):
        knots[i] = i - d
    knots[n_knots - d - 1 :] = n_cp - d
    param_vals = np.zeros(Nparam, dtype=np.float32)
    total_len = knots[-1] - knots[d]
    step = total_len / (Nparam - 1)
    for i in range(1, Nparam):
        param_vals[i] = param_vals[i - 1] + step

    basis = np.zeros((Nparam, n_cp), dtype=np.float32)
    for j in range(n_cp):
        for i in range(Nparam):
            basis[i, j] = BsFun(j + 1, d, param_vals[i], knots)
    basis[-1, -1] = 1.0
    return torch.tensor(basis, dtype=torch.float32), knots, param_vals


def build_bspline_derivatives(n_cp, d, Nparam, knots, param_vals):
    """原参数空间一二阶递推；未作物理尺度与端点修正。"""

    def BsFun_derivative(i, d, t):
        if d == 0:
            return 0.0
        denomA = knots[d + i - 1] - knots[i - 1]
        denomB = knots[d + i] - knots[i]
        A = 0 if denomA == 0 else d / denomA
        B = 0 if denomB == 0 else d / denomB
        return A * BsFun(i, d - 1, t, knots) - B * BsFun(i + 1, d - 1, t, knots)

    def BsFun_second(i, d, t):
        if d < 2:
            return 0.0
        a_val = (
            0
            if (knots[d + i - 2] - knots[i - 2]) == 0
            else d * (d - 1) / ((knots[d + i - 2] - knots[i - 2]) ** 2)
        )
        b_val = (
            0
            if (knots[d + i - 1] - knots[i - 1]) == 0
            else 2 * d * (d - 1) / ((knots[d + i - 1] - knots[i - 1]) ** 2)
        )
        c_val = (
            0 if (knots[d + i] - knots[i]) == 0 else d * (d - 1) / ((knots[d + i] - knots[i]) ** 2)
        )
        return (
            a_val * BsFun(i, d - 2, t, knots)
            - b_val * BsFun(i + 1, d - 2, t, knots)
            + c_val * BsFun(i + 2, d - 2, t, knots)
        )

    deriv = np.zeros((Nparam, n_cp), dtype=np.float32)
    second = np.zeros((Nparam, n_cp), dtype=np.float32)
    for j in range(n_cp):
        for i in range(Nparam):
            t_val = param_vals[i]
            deriv[i, j] = BsFun_derivative(j + 1, d, t_val)
            second[i, j] = BsFun_second(j + 1, d, t_val)
    return torch.tensor(deriv, dtype=torch.float32), torch.tensor(second, dtype=torch.float32)


@lru_cache(maxsize=32)
def grid_basis(n_cp, degree, count):
    """缓存不参与训练的轴矩阵；调用方不得原位修改返回值。"""
    b, knots, coordinates = build_bspline_basis(n_cp, degree, count)
    d, dd = build_bspline_derivatives(n_cp, degree, count, knots, coordinates)
    return b, d, dd
