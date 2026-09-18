"""GenCP 场状态分解与联合通道构造，不依赖运行配置。"""

import torch


def join_fsi(states):
    """同一网格的 u/v/p 与 SDF 按原通道顺序连接。"""
    if states["fluid"].shape[:-1] != states["structure"].shape[:-1]:
        raise ValueError("FSI 两场时空布局不一致")
    return torch.cat((states["fluid"], states["structure"]), dim=-1)


def split_fsi(value):
    """返回流体和结构视图；后续更新必须生成新张量。"""
    if value.shape[-1] != 4:
        raise ValueError("FSI 需要四个状态通道")
    return {"fluid": value[..., :3], "structure": value[..., 3:4]}


def joint_condition(condition, target):
    """拼接条件与目标，空间身份须已由准备记录核验。"""
    if condition.shape[:-1] != target.shape[:-1]:
        raise ValueError("条件和目标网格不匹配")
    return torch.cat((condition, target), dim=-1)
