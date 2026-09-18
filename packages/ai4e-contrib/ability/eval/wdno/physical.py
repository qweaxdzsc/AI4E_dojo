"""WDNO 原基础预测评价定义。"""

import numpy as np
import torch

from .metrics import mse_deviation


def metrics(arrays: dict) -> dict:
    """排除初始帧、float32 每样本平均，再用样本等权平均。"""
    predicted = torch.from_numpy(np.array(arrays["prediction"], copy=True))
    target = torch.from_numpy(np.array(arrays["target"], copy=True))
    values = mse_deviation(predicted[:, 1:], target[:, 1:])
    return {
        "mse": float(np.mean(values.tolist())),
        "sample_mse": values.tolist(),
        "paper_mse": 0.00014,
        "paper_protocol_matched": False,
        "initial_condition_max_abs": float((predicted[:, 0] - target[:, 0]).abs().max()),
    }
