"""真实研究变体：固体边界温度平滑，固定结果增加速度模长。"""

import numpy as np

from ai4e_contrib.ability.transform.gencp.conditions import fluid_condition


def averaged_fluid_condition(states, boundary):
    """两列温度先平均再广播，是显式变体而非参考默认。"""
    condition = fluid_condition(states, boundary)
    mean = condition.mean(dim=3, keepdim=True)
    return mean.expand_as(condition)


def speed_pair(pair):
    """核热固定流体结果的 u/v 模长；输出仍为五维分场数组。"""
    return tuple(np.sqrt(value[..., 1:2] ** 2 + value[..., 2:3] ** 2) for value in pair)
