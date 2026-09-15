"""同步设备后的墙钟计时；不把异步提交时间当作预测耗时。"""

from contextlib import contextmanager
from time import perf_counter

import torch


def synchronize(device) -> None:
    """仅同步实际计算设备；CPU无异步设备队列。"""
    device = torch.device(device)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elif device.type == "mps":
        torch.mps.synchronize()


@contextmanager
def measure(device="cpu"):
    """返回可记录秒数的字典，成功或异常均记录已耗时。"""
    synchronize(device)
    record = {}
    start = perf_counter()
    try:
        yield record
    finally:
        synchronize(device)
        record["seconds"] = perf_counter() - start
