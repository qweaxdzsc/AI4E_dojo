"""MAT 具名数值数组读取，不绑定字段名或实验分片。"""

from pathlib import Path

import numpy as np


def read_matlab(path: str | Path, names: tuple[str, ...]) -> dict[str, np.ndarray]:
    """读取传统 MAT；保留原 dtype/轴，未知字段、对象或非有限值报错。"""
    from scipy.io import loadmat

    if not names or len(set(names)) != len(names):
        raise ValueError("字段名单须非空且唯一")
    raw = loadmat(path, variable_names=list(names))
    arrays = {}
    for name in names:
        value = raw[name]
        if value.dtype.kind not in "biuf" or not np.isfinite(value).all():
            raise ValueError(f"非法数值字段: {name}")
        arrays[name] = value
    return arrays
