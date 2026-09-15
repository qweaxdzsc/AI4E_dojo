"""首次通过概率的对流扩散数据；闭式 CDF 与原积分表达式等价。"""

import numpy as np
from scipy.special import log_ndtr, ndtr

from ai4e_contrib.application.datasets.parametric import generate_dataset, tensor_sample


def truth(x, t, *, a, lam):
    """u_t = lam*u_x + 0.5*u_xx，右端吸收边界优先于初值。"""
    x, t = np.broadcast_arrays(x, t)
    distance = np.maximum(a - x, 0)
    safe_t = np.maximum(t, np.finfo(float).tiny)
    root = np.sqrt(safe_t)
    with np.errstate(over="ignore", invalid="ignore"):
        result = ndtr((lam * safe_t - distance) / root) + np.exp(
            2 * lam * distance + log_ndtr((-lam * safe_t - distance) / root)
        )
    return np.where(x >= a, 1.0, np.where(t == 0, 0.0, result))


def make_sample(rng, config, *, index, split):
    """按原范围生成一个实例；默认独立测试使用原论文脚本指定参数。"""
    a, lam = float(rng.uniform(0, 4)), float(rng.uniform(0, 2))
    if split == "test" and index == 0:
        a, lam = 2.0, 1.5
    p = {"a": a, "lam": lam, **config.get("parameters", {})}
    x, t = np.linspace(-10, p["a"], config["nx"]), np.linspace(0, 10, config["nt"])
    return tensor_sample(
        {"t": t, "x": x},
        truth(x[None], t[:, None], **p),
        p,
        {"t": [0.0, 10.0], "x": [-10.0, p["a"]]},
    )


def generate(config):
    """独立生产对流扩散数据集，返回清单路径。"""
    return generate_dataset("convection_diffusion", config)
