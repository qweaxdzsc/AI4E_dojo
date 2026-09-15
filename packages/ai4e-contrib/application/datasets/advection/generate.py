"""周期正弦传播的解析数据，不依赖样条或网络。"""

import numpy as np

from ai4e_contrib.application.datasets.parametric import generate_dataset, tensor_sample


def truth(x, t, *, beta, phase):
    """周期为一的解析传播真值。"""
    return np.sin(2 * np.pi * ((x - beta * t) % 1.0) + phase)


def parameter_streams(config):
    """按原代码连续MT19937流先训练后测试。"""
    rng = np.random.RandomState(config["seed"])
    yield "train", rng
    yield "test", rng


def make_sample(rng, config, *, index, split):
    """生成速度与相位实例。"""
    p = {
        "beta": float(rng.uniform(0.5, 1.5)),
        "phase": float(rng.uniform(0, 2 * np.pi)),
        **config.get("parameters", {}),
    }
    x, t = np.linspace(0, 1, config["nx"]), np.linspace(0, 2, config["nt"])
    sample = tensor_sample(
        {"t": t, "x": x}, truth(x[None], t[:, None], **p), p, {"t": [0.0, 2.0], "x": [0.0, 1.0]}
    )

    sample["axes"] = {k: v.float() for k, v in sample["axes"].items()}
    sample["u"] = sample["u"].float()
    sample["parameters"] = {k: float(np.float32(v)) for k, v in p.items()}
    sample["numerical_protocol"] = "advection-source-fp32-mt19937-v1"
    return sample


def generate(config):
    """独立生产 Advection 数据集。"""
    return generate_dataset("advection", config)
