"""明确轴的固定数组滤波；原数组不会被原地覆盖。"""

import numpy as np


def gaussian_spatial(values, *, sigma, channels):
    """对 B,T,H,W,C 的选定通道逐帧二维平滑。"""
    from scipy.ndimage import gaussian_filter

    if values.ndim != 5 or sigma < 0 or any(c < 0 or c >= values.shape[-1] for c in channels):
        raise ValueError("平滑参数非法")
    result = np.array(values, copy=True)
    for b in range(len(result)):
        for t in range(result.shape[1]):
            for c in channels:
                result[b, t, :, :, c] = gaussian_filter(values[b, t, :, :, c], sigma=sigma)
    return result
