"""逐块带有效域的字段统计，不保存数据副本。"""

import numpy as np


def masked_statistics(chunks):
    """消费 (values, weights)，按通道返回均值、标准差和有效计数。"""
    sums = squares = counts = None
    for values, weights in chunks:
        values = np.asarray(values, dtype=np.float64)
        weights = np.broadcast_to(weights, values.shape)
        if not np.isfinite(values).all() or not np.isfinite(weights).all() or (weights < 0).any():
            raise ValueError("统计输入非有限或权重非法")
        axes = tuple(range(values.ndim - 1))
        a, b, c = (values * weights).sum(axes), (values**2 * weights).sum(axes), weights.sum(axes)
        if sums is None:
            sums, squares, counts = a, b, c
        else:
            sums += a
            squares += b
            counts += c
    if counts is None or (counts <= 0).any():
        raise ValueError("字段没有有效统计样本")
    mean = sums / counts
    scale = np.sqrt(np.maximum(squares / counts - mean**2, 0))
    if (scale <= 0).any():
        raise ValueError("字段标准差为零")
    return {"mean": mean.tolist(), "scale": scale.tolist(), "count": counts.tolist()}
