"""锁定40ffb623来源的neumann数值定义；仅本案例使用，不是通用物理导数。"""

import numpy as np
from torch import nn


def BsFun(i, d, t, Ln):
    """保留锁定原仓库的BsFun数值行为；导数为参数坐标，非物理坐标。"""
    if d == 0:
        return 1.0 if Ln[i - 1] <= t < Ln[i] else 0.0
    a = 0.0 if Ln[d + i - 1] - Ln[i - 1] == 0 else (t - Ln[i - 1]) / (Ln[d + i - 1] - Ln[i - 1])
    b = 0.0 if Ln[d + i] - Ln[i] == 0 else (Ln[d + i] - t) / (Ln[d + i] - Ln[i])
    return a * BsFun(i, d - 1, t, Ln) + b * BsFun(i + 1, d - 1, t, Ln)


def BsFun_derivative(i, d, t, Ln):
    """保留锁定原仓库的BsFun_derivative数值行为；导数为参数坐标，非物理坐标。"""
    if d == 0:
        return 0.0
    a = 0.0 if Ln[d + i - 1] - Ln[i - 1] == 0 else d / (Ln[d + i - 1] - Ln[i - 1])
    b = 0.0 if Ln[d + i] - Ln[i] == 0 else d / (Ln[d + i] - Ln[i])
    return a * BsFun(i, d - 1, t, Ln) - b * BsFun(i + 1, d - 1, t, Ln)


def BsFun_second_derivative(i, d, t, Ln):
    """保留锁定原仓库的BsFun_second_derivative数值行为；导数为参数坐标，非物理坐标。"""
    if d < 2:
        return 0.0
    a = 0.0 if Ln[d + i - 2] - Ln[i - 2] == 0 else d * (d - 1) / (Ln[d + i - 2] - Ln[i - 2]) ** 2
    b = (
        0.0
        if Ln[d + i - 1] - Ln[i - 1] == 0
        else 2 * d * (d - 1) / (Ln[d + i - 1] - Ln[i - 1]) ** 2
    )
    c = 0.0 if Ln[d + i] - Ln[i] == 0 else d * (d - 1) / (Ln[d + i] - Ln[i]) ** 2
    return (
        a * BsFun(i, d - 2, t, Ln) - b * BsFun(i + 1, d - 2, t, Ln) + c * BsFun(i + 2, d - 2, t, Ln)
    )


def BsKnots(n_cp, d, Ns):
    """保留锁定原仓库的BsKnots数值行为；导数为参数坐标，非物理坐标。"""
    n_knots = n_cp + d + 1
    Ln = np.zeros(n_knots, dtype=np.float32)
    for i in range(d + 1, n_knots - d - 1):
        Ln[i] = i - d
    Ln[n_knots - d - 1 :] = n_cp - d
    tk = np.linspace(0, Ln[-1], Ns).astype(np.float32)
    B = np.zeros((Ns, n_cp), dtype=np.float32)
    for j in range(n_cp):
        for i in range(Ns):
            B[i, j] = BsFun(j + 1, d, tk[i], Ln)
    B[-1, -1] = 1.0
    return (tk, Ln, B)


def BsKnots_derivatives(n_cp, d, Ns, Ln, tk):
    """保留锁定原仓库的BsKnots_derivatives数值行为；导数为参数坐标，非物理坐标。"""
    Bd1 = np.zeros((Ns, n_cp), dtype=np.float32)
    Bd2 = np.zeros((Ns, n_cp), dtype=np.float32)
    for j in range(n_cp):
        for i in range(Ns):
            Bd1[i, j] = BsFun_derivative(j + 1, d, tk[i], Ln)
            Bd2[i, j] = BsFun_second_derivative(j + 1, d, tk[i], Ln)
    return (Bd1, Bd2)


def bspline_eval(U, Bt, Bx):
    """保留锁定原仓库的bspline_eval数值行为；导数为参数坐标，非物理坐标。"""
    return Bt @ U @ Bx.T


def bspline_derivs(U, Bt, Bx, Bt_d1, Bx_d1, Bt_d2, Bx_d2):
    """保留锁定原仓库的bspline_derivs数值行为；导数为参数坐标，非物理坐标。"""
    S_t = Bt_d1 @ U @ Bx.T
    S_x = Bt @ U @ Bx_d1.T
    S_xx = Bt @ U @ Bx_d2.T
    return (S_t, S_x, S_xx)


class ControlPointNet(nn.Module):
    """保留锁定原仓库的ControlPointNet数值行为；导数为参数坐标，非物理坐标。"""

    def __init__(self, n_cp_t, n_cp_x, hidden=128):
        super().__init__()
        self.n_cp_t, self.n_cp_x = (n_cp_t, n_cp_x)
        self.net = nn.Sequential(
            nn.Linear(1, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_cp_t * n_cp_x),
        )

    def forward(self, nu):
        """原控制系数网络前向计算。"""
        return self.net(nu)


class BSNetLoss(nn.Module):
    """保留锁定原仓库的BSNetLoss数值行为；导数为参数坐标，非物理坐标。"""

    def __init__(self, n_cp_t, n_cp_x, hidden=128):
        super().__init__()
        self.n_cp_t, self.n_cp_x = (n_cp_t, n_cp_x)
        self.ctrl = ControlPointNet(n_cp_t, n_cp_x, hidden)

    def forward_U(self, nu):
        """原控制系数网络前向计算。"""
        vec = self.ctrl(nu)
        return vec.view(-1, self.n_cp_t, self.n_cp_x)
