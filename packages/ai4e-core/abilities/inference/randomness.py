"""独立推理的可复现随机上下文，不读取训练状态或改变调用方随机流。"""

import random
from contextlib import contextmanager

import numpy as np
import torch


@contextmanager
def preserve_randomness():
    """成功及异常时恢复 Python、NumPy、CPU、CUDA 和可用 MPS 随机流。"""
    python_state, numpy_state = random.getstate(), np.random.get_state()
    mps_state = torch.mps.get_rng_state() if torch.backends.mps.is_available() else None
    try:
        with torch.random.fork_rng():
            yield
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)
        if mps_state is not None:
            torch.mps.set_rng_state(mps_state)


@contextmanager
def seeded_randomness(seed: int):
    """临时设置所有随机种子，退出时恢复调用方的随机流。"""
    with preserve_randomness():
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        yield
