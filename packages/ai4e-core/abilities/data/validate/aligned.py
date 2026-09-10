"""校验多个数组首维对齐。"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def require_same_leading_dim(
    *arrays: np.ndarray,
    labels: Sequence[str],
) -> None:
    """要求各组数组首维相等，否则列出各字段长度。

    Args:
        *arrays: 待校验数组。
        labels: 与数组一一对应的字段名。

    Raises:
        ValueError: 个数对不上，或首维不一致。
    """
    if len(arrays) != len(labels):
        raise ValueError(f"字段名数量与数组数量不一致: labels={len(labels)}, arrays={len(arrays)}")
    if not arrays:
        raise ValueError("至少需要一个数组才能校验点数")
    lengths = [int(np.asarray(array).shape[0]) for array in arrays]
    if len(set(lengths)) > 1:
        detail = ", ".join(f"{name}={length}" for name, length in zip(labels, lengths, strict=True))
        raise ValueError(f"字段点数不对齐: {detail}")
