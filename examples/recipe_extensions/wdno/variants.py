"""复制到自己的 recipe 即可使用；不需要登记框架组件。"""

import numpy as np

from ai4e_contrib.application.spatiotemporal_pde.wdno.model import network


def custom_network(options: dict):
    """示例换成两层去噪网络，仍交付九个小波通道。"""
    return network({**options, "dim_mults": [1, 1]})


def custom_loss(model, values):
    """示例替换目标权重；真实损失仍由 WDNO 能力计算。"""
    return model(values) * 0.5


def energy(arrays: dict) -> tuple[dict, dict]:
    """对预测按空间平均平方，保留 sample/time 身份和单位。"""
    return (
        {"energy": np.mean(arrays["prediction"] ** 2, axis=-1)},
        {"energy": {"units": "u^2", "axes": ["sample", "time"]}},
    )
