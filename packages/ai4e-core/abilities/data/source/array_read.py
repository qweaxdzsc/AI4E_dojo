"""原生数值数组按需读取；不转换 VTK，不加载无关时间帧。"""

from pathlib import Path

import numpy as np


def read_array(path, selection=Ellipsis, *, key=None):
    """读取 NPY 或具名 HDF5 数据集的切片，返回独立、有限数值数组。"""
    path = Path(path)
    if path.suffix == ".npy":
        value = np.load(path, mmap_mode="r", allow_pickle=False)[selection]
    elif path.suffix in {".h5", ".hdf5"}:
        import h5py

        if not key:
            raise ValueError("HDF5 读取需要明确的数据集键")
        with h5py.File(path, "r") as handle:
            value = handle[key][selection]
    else:
        raise ValueError(f"不支持原生数组格式: {path.suffix}")
    value = np.array(value, copy=True)
    if value.dtype.kind not in "biufc" or not np.isfinite(value).all():
        raise ValueError(f"非有限或非数值数组: {path}:{key}")
    return value
