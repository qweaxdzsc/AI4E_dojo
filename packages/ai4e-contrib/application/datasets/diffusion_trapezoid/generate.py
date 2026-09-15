"""选定梯形实验的数据：原逐行间距差分与 Euler，不代表完整物理映射算子。"""

import numpy as np

from ai4e_contrib.application.datasets.parametric import generate_dataset, tensor_sample

PROTOCOL = "trapezoid-euler-row-spacing-v1"


def parameter_streams(config):
    """重现原连续 MT19937 流；保留单例演示消耗，随后生成正式测试名单。"""
    rng = np.random.RandomState(config["seed"])
    yield "train", rng
    rng.uniform(0, 1.5)  # 原 notebook 先做一次单例展示；该实例不进入十例均值。
    yield "test", rng


def solve(*, nx, ny, nt, a):
    """原近似空间模板的 Euler 解，返回 xi、eta、FP32 时间和场。

    每一步存回 FP32，差分中间量用 FP64，保留原 NumPy 1.x 标量提升。
    数组运算替代相互独立的空间循环；不引入子步、混合导数或隐式积分。
    超出显式稳定界时拒绝生成，不能自动改步长冒充同一个实验。
    """
    if min(nx, ny) < 3 or nt < 2 or not np.isfinite(a) or a < 0:
        raise ValueError("梯形网格至少 3×3，nt 至少 2，a 必须有限非负")
    xi, eta = np.linspace(0, 1, nx), np.linspace(0, 1, ny)
    dt, dy = 1.0 / (nt - 1), 1.0 / (ny - 1)
    dx = (2.0 - eta[1:-1]) / (nx - 1)
    if dt * (1 / dx.min() ** 2 + a / dy**2) > 1 + 1e-12:
        raise ValueError("Euler 稳定条件不满足：增加 nt，不会静默更换求解器")
    t = np.linspace(0, 1, nt, dtype=np.float32)
    values = np.ones((nt, ny, nx), dtype=np.float32)
    values[0, 1:-1, 1:-1] = 0
    for k in range(1, nt):
        old = values[k - 1].astype(np.float64)
        xx = (old[1:-1, 2:] - 2 * old[1:-1, 1:-1] + old[1:-1, :-2]) / dx[:, None] ** 2
        yy = (old[2:, 1:-1] - 2 * old[1:-1, 1:-1] + old[:-2, 1:-1]) / dy**2
        values[k, 1:-1, 1:-1] = old[1:-1, 1:-1] + dt * (0.5 * (xx + a * yy))
    return xi, eta, t, values


def make_sample(rng, config, *, index, split):
    """生成独立实例，显式记录数值协议；场布局始终为 t、eta、xi。"""
    p = {"a": float(rng.uniform(0, 1.5)), **config.get("parameters", {})}
    xi, eta, t, u = solve(nx=config["nx"], ny=config.get("ny", 21), nt=config["nt"], **p)
    sample = tensor_sample(
        {"t": t, "eta": eta, "xi": xi},
        u,
        p,
        {"t": [0.0, 1.0], "eta": [0.0, 1.0], "xi": [0.0, 1.0]},
        mapping="trapezoid",
    )
    sample["numerical_protocol"] = PROTOCOL
    return sample


def generate(config):
    """独立生产选定的主文十实例梯形数据，不启动训练。"""
    return generate_dataset("diffusion_trapezoid", config)
