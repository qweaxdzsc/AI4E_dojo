"""周期 FFT 空间离散与 LSODA 积分的 Burgers 数据生成。"""

import numpy as np
from scipy.integrate import solve_ivp

from ai4e_contrib.application.datasets.parametric import generate_dataset, tensor_sample


def solve(*, nx, nt, mu, m, nu=0.01, rtol=1e-7, atol=1e-9):
    """周期网格不重复端点；求解 u_t=-mu*u*u_x+nu*u_xx。

    保留原 Gaussian 初值的离散周期延拓，不声称端点连续；这会影响空间
    收敛，必须通过细网格参考核验，不能只比较积分器容差。
    """
    x, t = np.linspace(0, 10, nx, endpoint=False), np.linspace(0, 8, nt)
    k = 2 * np.pi * np.fft.fftfreq(nx, d=10 / nx)

    def rhs(time, u):
        spectrum = np.fft.fft(u)
        ux = np.fft.ifft(1j * k * spectrum).real
        uxx = np.fft.ifft(-k * k * spectrum).real
        return -mu * u * ux + nu * uxx

    solution = solve_ivp(
        rhs, (0, 8), np.exp(-((x - m) ** 2) / 2), t_eval=t, method="LSODA", rtol=rtol, atol=atol
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return x, t, solution.y.T


def make_sample(rng, config, *, index, split):
    """生成黏性 Burgers 单实例参考场。"""
    p = {
        "mu": float(rng.uniform(0.5, 1.5)),
        "m": float(rng.uniform(2, 4)),
        "nu": 0.01,
        **config.get("parameters", {}),
    }
    if p["nu"] <= 0:
        raise ValueError("nu 必须为正")
    x, t, values = solve(
        nx=config["nx"],
        nt=config["nt"],
        **p,
        rtol=config.get("rtol", 1e-7),
        atol=config.get("atol", 1e-9),
    )
    return tensor_sample({"t": t, "x": x}, values, p, {"t": [0.0, 8.0], "x": [0.0, 10.0]})


def generate(config):
    """独立生产 Burgers 数据集。"""
    return generate_dataset("burgers", config)
