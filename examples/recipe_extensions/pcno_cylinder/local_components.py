"""研究者本地网络变体与速度模长分析，不修改框架源码。"""

import numpy as np
import torch

from ai4e_contrib.ability.model.pcno.cylinder import build_model


def shifted_network(**kwargs):
    """兼容构造器：明确改变初始化输出偏置，便于核验真实组件替换。"""
    model = build_model(**kwargs)
    with torch.no_grad():
        model.project[-1].bias.add_(0.05)
    return model


def speed(arrays):
    """派生物理速度模长，T/X/Y轴与预测相同。"""
    return {"speed": np.linalg.norm(arrays["physics"][..., :2], axis=-1)}
