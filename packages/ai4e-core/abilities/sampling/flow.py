"""生成流时间与噪声的显式采样；顺序与设备均由调用者确定。"""

import torch


def flow_randomness(value, *, initial=None, time=None, noise=None):
    """按初始噪声、CPU 时间再迁移、路径噪声的顺序采样；零 sigma 仍抽噪声。"""
    initial = torch.randn_like(value) if initial is None else initial
    time = torch.rand(value.shape[0]).type_as(value) if time is None else time
    noise = torch.randn_like(value) if noise is None else noise
    if (
        initial.shape != value.shape
        or noise.shape != value.shape
        or time.shape != (value.shape[0],)
    ):
        raise ValueError("流匹配随机量形状不匹配")
    return initial, time, noise
