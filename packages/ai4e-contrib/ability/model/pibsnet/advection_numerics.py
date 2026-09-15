"""锁定40ffb623来源的advection数值定义；仅本案例使用，不是通用物理导数。"""

import numpy as np
import torch
from torch import nn


def BsFun(i, d, t, Ln):
    """保留锁定原仓库的BsFun数值行为；导数为参数坐标，非物理坐标。"""
    if d == 0:
        return 1.0 if Ln[i - 1] <= t < Ln[i] else 0.0
    else:
        a = 0 if Ln[d + i - 1] - Ln[i - 1] == 0 else (t - Ln[i - 1]) / (Ln[d + i - 1] - Ln[i - 1])
        b = 0 if Ln[d + i] - Ln[i] == 0 else (Ln[d + i] - t) / (Ln[d + i] - Ln[i])
        return a * BsFun(i, d - 1, t, Ln) + b * BsFun(i + 1, d - 1, t, Ln)


def BsFun_derivative(i, d, t, Ln):
    """保留锁定原仓库的BsFun_derivative数值行为；导数为参数坐标，非物理坐标。"""
    if d == 0:
        return 0.0
    else:
        a = 0 if Ln[d + i - 1] - Ln[i - 1] == 0 else d / (Ln[d + i - 1] - Ln[i - 1])
        b = 0 if Ln[d + i] - Ln[i] == 0 else d / (Ln[d + i] - Ln[i])
        return a * BsFun(i, d - 1, t, Ln) - b * BsFun(i + 1, d - 1, t, Ln)


def BsFun_second_derivative(i, d, t, Ln):
    """保留锁定原仓库的BsFun_second_derivative数值行为；导数为参数坐标，非物理坐标。"""
    if d < 2:
        return 0.0
    else:
        a = 0 if Ln[d + i - 2] - Ln[i - 2] == 0 else d * (d - 1) / (Ln[d + i - 2] - Ln[i - 2]) ** 2
        b = (
            0
            if Ln[d + i - 1] - Ln[i - 1] == 0
            else 2 * d * (d - 1) / (Ln[d + i - 1] - Ln[i - 1]) ** 2
        )
        c = 0 if Ln[d + i] - Ln[i] == 0 else d * (d - 1) / (Ln[d + i] - Ln[i]) ** 2
        return (
            a * BsFun(i, d - 2, t, Ln)
            - b * BsFun(i + 1, d - 2, t, Ln)
            + c * BsFun(i + 2, d - 2, t, Ln)
        )


def BsKnots(n_cp, d, Ns):
    """保留锁定原仓库的BsKnots数值行为；导数为参数坐标，非物理坐标。"""
    n_knots = n_cp + d + 1
    Ln = np.zeros(n_knots)
    for i in range(d + 1, n_knots - d - 1):
        Ln[i] = i - d
    Ln[n_knots - d - 1 :] = n_cp - d
    tk = np.zeros(Ns)
    for i in range(1, Ns):
        tk[i] = tk[i - 1] + Ln[-1] / (Ns - 1)
    Bit = np.zeros((Ns, n_cp))
    for j in range(n_cp):
        for i in range(Ns):
            Bit[i, j] = BsFun(j + 1, d, tk[i], Ln)
    Bit[Ns - 1, n_cp - 1] = 1
    return (tk, Ln, Bit)


def BsKnots_derivatives(n_cp, d, Ns, Ln, tk):
    """保留锁定原仓库的BsKnots_derivatives数值行为；导数为参数坐标，非物理坐标。"""
    Bit_derivative = np.zeros((Ns, n_cp))
    for j in range(n_cp):
        for i in range(Ns):
            Bit_derivative[i, j] = BsFun_derivative(j + 1, d, tk[i], Ln)
    Bit_second_derivative = np.zeros((Ns, n_cp))
    for j in range(n_cp):
        for i in range(Ns):
            Bit_second_derivative[i, j] = BsFun_second_derivative(j + 1, d, tk[i], Ln)
    return (Bit_derivative, Bit_second_derivative)


class BetaPhaseControlPointNet(nn.Module):
    """保留锁定原仓库的BetaPhaseControlPointNet数值行为；导数为参数坐标，非物理坐标。"""

    def __init__(self, n_cp_x, n_cp_t, hidden_dim=64):
        super().__init__()
        self.fc1 = nn.Linear(2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, n_cp_x * n_cp_t)
        self.n_cp_t = n_cp_t
        self.n_cp_x = n_cp_x

    def forward(self, beta, phase):
        """原控制系数网络前向计算。"""
        "\n        beta:  shape (batch_size, 1)\n        phase: shape (batch_size, 1)\n        We concat => shape (batch_size, 2)\n        return shape => (n_cp_t, n_cp_x) if batch_size=1\n        "
        x = torch.cat((beta, phase), dim=1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        out = self.fc3(x)
        return out.view(-1, self.n_cp_t, self.n_cp_x)


def compute_bspline_derivatives(U_full, Bit_t, Bit_x, Bit_t_derivative, Bit_x_derivative):
    """保留锁定原仓库的compute_bspline_derivatives数值行为；导数为参数坐标，非物理坐标。"""
    "\n    Approx. partial derivatives of the B-spline surface:\n      B_surface_t ~ d/dt (B_surface)\n      B_surface_x ~ d/dx (B_surface)\n    "
    B_surface_t = torch.matmul(torch.matmul(Bit_t_derivative, U_full), Bit_x.T)
    B_surface_x = torch.matmul(torch.matmul(Bit_t, U_full), Bit_x_derivative.T)
    return (B_surface_t, B_surface_x)


def assign_first_row_direct(U_pred, u0_values):
    """保留锁定原仓库的assign_first_row_direct数值行为；导数为参数坐标，非物理坐标。"""
    "\n    Overwrite row 0 in U_pred with the actual initial condition.\n    If n_cp_x != len(u0_values), we interpolate.\n\n    U_pred: shape (n_cp_t, n_cp_x) or (1, n_cp_t, n_cp_x)\n    u0_values: shape (Nx,)\n    "
    if U_pred.ndim == 3:
        row0 = U_pred[0, 0, :]
        n_cp_x = U_pred.shape[2]
    else:
        row0 = U_pred[0, :]
        n_cp_x = U_pred.shape[1]
    Nx = len(u0_values)
    if n_cp_x == Nx:
        row0[:] = torch.from_numpy(u0_values)
    else:
        x_data = np.arange(Nx)
        x_cp = np.linspace(0, Nx - 1, n_cp_x)
        row0_cp = np.interp(x_cp, x_data, u0_values)
        row0[:] = torch.from_numpy(row0_cp)
