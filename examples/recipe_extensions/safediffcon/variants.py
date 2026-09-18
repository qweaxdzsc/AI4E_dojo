"""普通研究扩展：更小网络、自定义安全引导和带单位的派生量。"""

import numpy as np
import torch

from ai4e_contrib.ability.model.safediffcon.adapters import build_model


def small_model(**settings):
    """研究者直接改变网络宽度；配置同步记录 dim32。"""
    if settings["dim"] != 32:
        raise ValueError("本变体要求 model.dim=32，避免配置与实际网络不一致")
    return build_model(**settings)


def stricter_safety(x, target, *, case, q, weight):
    """加强采样安全引导并抑制控制能量；评价仍按原论文阈值。"""
    with torch.enable_grad():
        state = x.detach().requires_grad_()
        if case == "burgers":
            score = (state[:, 2, :11] * 10).mean(dim=(-1, -2))
            cost = torch.relu(score + q - 0.7**2) * weight
            cost = cost + 0.1 * (state[:, 1, :10] * 10).square().mean(dim=(-1, -2))
        else:
            score = (state[:, 1, :122] * 7).amin(-1)
            cost = torch.relu(5.1 - score + q) * weight
            cost = cost + 0.1 * state[:, 3:, :121].square().mean(dim=(-1, -2))
        return torch.autograd.grad(cost.sum(), state)[0]


def safety_margin(response, *, case):
    """逐时刻计算物理安全余量，声明身份、单位、有效性和轴。"""
    values = 0.8 - np.abs(response).max(-1) if case == "burgers" else response[:, 1] - 4.98
    return {
        "safety_margin": {
            "values": values,
            "valid": np.isfinite(values),
            "units": "u" if case == "burgers" else "dimensionless",
            "axes": "B,T",
        }
    }
