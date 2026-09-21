"""时间窗口、节点轨迹布局与初态回加。"""

import numpy as np


def time_window(times, values, requested, *, axis=0):
    """按精确时间取窗口；缺失或重复时间拒绝，不外推。"""
    times = np.asarray(times)
    if len(np.unique(times)) != len(times):
        raise ValueError("重复时间")
    ids = []
    for time in requested:
        match = np.flatnonzero(times == time)
        if len(match) != 1:
            raise ValueError(f"缺少时间 {time}")
        ids.append(int(match[0]))
    return np.take(values, ids, axis=axis)


def flatten_trajectory(values):
    """[B,T,N,C] 转 [B,N,T*C]，支持 numpy 和 torch。"""
    b, t, n, c = values.shape
    if hasattr(values, "permute"):
        return values.permute(0, 2, 1, 3).reshape(b, n, t * c)
    return values.transpose(0, 2, 1, 3).reshape(b, n, t * c)


def restore_trajectory(values, frames: int, channels: int, *, initial=None, initial_channels=0):
    """[B,N,T*C] 还原 [B,T,N,C]；可对前若干通道加初态 [B,N,C0]。"""
    b, n, width = values.shape
    if frames < 1 or channels < 1 or width != frames * channels:
        raise ValueError("轨迹宽度与帧/通道不一致")
    result = values.reshape(b, n, frames, channels)
    result = (
        result.permute(0, 2, 1, 3).clone()
        if hasattr(result, "permute")
        else result.transpose(0, 2, 1, 3).copy()
    )
    if initial is not None:
        if initial.shape != (b, n, initial_channels) or not 0 < initial_channels <= channels:
            raise ValueError("初态通道不一致")
        result[..., :initial_channels] += initial[:, None]
    return result
