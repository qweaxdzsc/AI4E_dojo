"""原程序的后处理声明：明确保留真值 mask 与平滑来源。"""

import numpy as np

from ai4e_core.abilities.postproc.filters import gaussian_spatial


def fsi_reference(prediction, target, *, threshold=0.04, sigma=0.8):
    """仅平滑结构 SDF，再对全部评价通道使用真值 SDF mask。"""
    smoothed = gaussian_spatial(prediction, sigma=sigma, channels=[3])
    mask = (target[..., 3:4] > threshold).astype(np.float32)
    return smoothed * mask, target * mask, smoothed, mask
