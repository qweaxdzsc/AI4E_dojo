"""规则网格一致采样与原实体索引。"""

import numpy as np


def grid_indices(shape: tuple[int, ...], strides: tuple[int, ...]):
    """按 C 序取每轴步长，返回原始展平身份及采样形状。"""
    if len(shape) != len(strides) or any(x < 1 for x in (*shape, *strides)):
        raise ValueError("网格形状/步长非法")
    sampled = np.arange(np.prod(shape)).reshape(shape)[tuple(slice(None, None, s) for s in strides)]
    return sampled.reshape(-1), sampled.shape


def sample_grid(values, shape: tuple[int, ...], strides: tuple[int, ...], *, axis=0):
    """从已展平网格实体轴采样；返回同一原索引供坐标及标签共用。"""
    ids, sampled_shape = grid_indices(shape, strides)
    if values.shape[axis] != np.prod(shape):
        raise ValueError("实体数与网格不一致")
    return np.take(values, ids, axis=axis), ids, sampled_shape


def grid_faces(shape):
    """C 序二维点网格的四边形 connectivity，可用于 PyVista PolyData。"""
    if len(shape) != 2 or min(shape) < 2:
        raise ValueError("面网格至少为2×2")
    ids = np.arange(np.prod(shape)).reshape(shape)
    a, b, c, d = ids[:-1, :-1], ids[1:, :-1], ids[1:, 1:], ids[:-1, 1:]
    return np.stack((np.full_like(a, 4), a, b, c, d), axis=-1).reshape(-1)
