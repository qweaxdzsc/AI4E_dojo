"""沿明确流时间网格积分，支持逐步观察与取消。"""

import itertools

import torch


def integrate(
    states, times, *, step, velocities, order, boundary=None, observe=None, cancelled=None
):
    """推进具名异形场；不改变物理时间帧或推断自动回滚。"""
    if (
        len(times) < 2
        or len(order) != len(set(order))
        or set(order) != set(states)
        or set(order) != set(velocities)
    ):
        raise ValueError("流时间或场集合非法")
    if not all(float(b) > float(a) for a, b in itertools.pairwise(times)):
        raise ValueError("流时间必须严格递增")
    current = states
    for index, (time, next_time) in enumerate(itertools.pairwise(times)):
        if cancelled and cancelled():
            raise InterruptedError(f"生成积分在第 {index} 步取消")
        current = step(current, time, next_time - time, velocities, order, boundary)
        if any(not torch.isfinite(v).all() for v in current.values()):
            raise FloatingPointError(f"生成积分第 {index} 步非有限")
        if observe:
            observe(index + 1, next_time, current)
    return current
