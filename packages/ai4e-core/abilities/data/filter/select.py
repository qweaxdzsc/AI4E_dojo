"""按布尔 mask 沿首维筛选一组对齐数组，不改原数组。"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np


def apply_aligned_mask(
    arrays: Mapping[str, np.ndarray],
    mask: np.ndarray,
) -> dict[str, np.ndarray]:
    """用同一份布尔 mask 筛选同组数组，原数组保持不变。

    Args:
        arrays: 逻辑名到数组；每个数组首维必须等于 mask 长度。
        mask: 一维布尔数组，``True`` 表示保留。

    Returns:
        筛后的新数组映射，点序与 ``True`` 的出现顺序一致。

    Raises:
        ValueError: mask 不是一维布尔，或任一数组首维与 mask 长度不一致。
        TypeError: 输入不是映射或数组。
    """
    if not isinstance(arrays, Mapping):
        raise TypeError("套 mask 需要名字到数组的映射")
    mask_array = np.asarray(mask)
    if mask_array.ndim != 1 or mask_array.dtype != bool:
        raise ValueError("mask 必须是一维布尔数组")
    length = int(mask_array.shape[0])
    selected: dict[str, np.ndarray] = {}
    for name, array in arrays.items():
        if not isinstance(name, str) or not name:
            raise ValueError("套 mask 的字段名必须是非空字符串")
        values = np.asarray(array)
        if values.ndim == 0:
            raise ValueError(f"字段 {name} 必须有实体首维")
        if values.shape[0] != length:
            raise ValueError(
                f"字段 {name} 首维 {values.shape[0]} 与 mask 长度 {length} 不一致，"
                "不得按点序号硬配单元场"
            )
        selected[name] = values[mask_array]
    return selected
