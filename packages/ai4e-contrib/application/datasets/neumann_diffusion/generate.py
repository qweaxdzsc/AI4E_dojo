"""齐次 Neumann 扩散的解析数据生成。"""

import numpy as np

from ai4e_contrib.application.datasets.parametric import generate_dataset, tensor_sample


def truth(x, t, *, nu):
    """cos(pi*x)*exp(-nu*pi²*t)，两端物理法向导数均为零。"""
    return np.cos(np.pi * x) * np.exp(-nu * np.pi**2 * t)


def parameter_streams(config):
    """按原代码连续MT19937流先训练后测试。"""
    rng = np.random.RandomState(config["seed"])
    yield "train", rng
    yield "test", rng


def make_sample(rng, config, *, index, split):
    """生成单个扩散系数实例。"""
    p = {"nu": float(rng.uniform(0.1, 1.5)), **config.get("parameters", {})}
    if p["nu"] <= 0:
        raise ValueError("nu 必须为正")
    x, t = (
        np.linspace(0, 1, config["nx"]).astype(np.float32),
        np.linspace(0, 1, config["nt"]).astype(np.float32),
    )
    sample = tensor_sample(
        {"t": t, "x": x}, truth(x[None], t[:, None], **p), p, {"t": [0.0, 1.0], "x": [0.0, 1.0]}
    )

    sample["axes"] = {k: v.float() for k, v in sample["axes"].items()}
    sample["u"] = sample["u"].float()
    sample["parameters"] = {k: float(np.float32(v)) for k, v in p.items()}
    sample["numerical_protocol"] = "neumann-source-fp32-mt19937-v1"
    return sample


def generate(config):
    """独立生产 Neumann 扩散数据集。"""
    return generate_dataset("neumann_diffusion", config)
