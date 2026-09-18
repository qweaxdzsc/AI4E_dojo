"""NTcouple 原场间条件映射，操作的是归一化场。"""

import torch


def neutron_condition(states, boundary):
    """固体/流体温度沿宽度拼接，并广播中子外部边界。"""
    temperatures = torch.cat((states["solid"], states["fluid"][..., :1]), dim=-2)
    return torch.cat((temperatures, boundary["neutron"].repeat(1, 1, 1, 20, 1)), dim=-1)


def solid_condition(states, boundary):
    """使用中子左八列、流体第一列温度与外部固体左边界。"""
    return torch.cat(
        (
            states["neutron"][:, :, :, :8, :],
            states["fluid"][:, :, :, :1, :1].repeat(1, 1, 1, 8, 1),
            boundary["solid"].repeat(1, 1, 1, 8, 1),
        ),
        dim=-1,
    )


def fluid_condition(states, boundary):
    """重复固体最右两列归一化温度；保留原实现而非解释成热通量。"""
    del boundary
    pair = torch.cat((states["solid"][:, :, :, -2:-1, :], states["solid"][:, :, :, -1:, :]), dim=-2)
    return pair.repeat(1, 1, 1, states["fluid"].shape[3] // 2, 1)
