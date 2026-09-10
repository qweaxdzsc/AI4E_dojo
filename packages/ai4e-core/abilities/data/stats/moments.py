"""沿实体首维流式累计总体矩，保留尾维而不合并实体和通道。"""

from collections.abc import Iterable

import numpy as np

from ai4e_core.base.events import traced


@traced("流式统计")
def accumulate_moments(batches: Iterable[np.ndarray]) -> dict:
    """消费一次数组流；总体标准差除以 N，标量以单通道输出。"""
    count = 0
    mean = moment2 = lowest = highest = None
    shape = None
    for raw in batches:
        values = np.asarray(raw, dtype=np.float64)
        if values.ndim == 0:
            raise ValueError("统计数组必须有实体首维")
        if values.ndim == 1:
            values = values[:, None]
        if shape is None:
            shape = values.shape[1:]
        elif values.shape[1:] != shape:
            raise ValueError(f"统计量尾维不一致: {shape} / {values.shape[1:]}")
        if not np.isfinite(values).all():
            raise ValueError("统计量不接受非有限数值")
        n = len(values)
        if not n:
            continue
        local_mean = values.mean(axis=0)
        local_m2 = ((values - local_mean) ** 2).sum(axis=0)
        if count == 0:
            mean, moment2 = local_mean, local_m2
            lowest, highest = values.min(axis=0), values.max(axis=0)
        else:
            delta = local_mean - mean
            total = count + n
            mean = mean + delta * n / total
            moment2 = moment2 + local_m2 + delta**2 * count * n / total
            lowest = np.minimum(lowest, values.min(axis=0))
            highest = np.maximum(highest, values.max(axis=0))
        count += n
    if not count:
        raise ValueError("至少需要一个非空数组才能累计统计量")
    return {
        "mean": mean,
        "std": np.sqrt(moment2 / count),
        "min": lowest,
        "max": highest,
        "count": count,
    }
