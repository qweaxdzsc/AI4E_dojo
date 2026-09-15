"""模型创建、设备精度与用户随机种子入口。"""

import random

import numpy as np
import torch

from ai4e_core.abilities.training.optimization import resolve_device


def build_model(cfg, model_component):
    """一次初始化后迁移至显式设备，不在训练循环中重复初始化。"""
    seed = cfg["train"]["seed"]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    dtype = {"fp32": torch.float32, "fp64": torch.float64}[cfg["train"]["precision"]]
    device = resolve_device(cfg["train"]["device"])
    if device.type == "mps" and dtype == torch.float64:
        raise ValueError("MPS 不支持 fp64，请明确选择 CPU/CUDA 或 fp32")
    return model_component.build(cfg).to(device=device, dtype=dtype)
