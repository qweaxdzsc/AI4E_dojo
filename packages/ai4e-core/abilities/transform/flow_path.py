"""独立条件流匹配概率路径；计算与随机采样分离。"""

import math


def conditional_path(initial, target, time, noise, *, sigma=0.0):
    """返回插值加噪状态和端点速度；不推断哪个通道属于条件。"""
    if (
        initial.shape != target.shape
        or noise.shape != target.shape
        or time.shape != (target.shape[0],)
    ):
        raise ValueError("概率路径输入形状不匹配")
    if not math.isfinite(sigma) or sigma < 0:
        raise ValueError("sigma 必须非负且有限")
    t = time.reshape(-1, *([1] * (target.ndim - 1)))
    return t * target + (1 - t) * initial + sigma * noise, target - initial
