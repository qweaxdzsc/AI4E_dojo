"""GenCP 冻结归一化，保留输入/目标分离和原参考算术。"""

import torch

from ai4e_core.abilities.transform.field_transforms import logarithm, signed_range

BOUNDS = {
    "neutron": ([0.0], [3.258]),
    "solid": ([100.0], [1500.0]),
    "fluid": ([100.0, -50.0, -0.006, 0.0], [1200.0, 250.0, 0.006, 0.6]),
}


def nt_normalize(value, field, *, inverse=False):
    """最后一维为通道；中子含 log/exp，流体四通道分别变换。"""
    value = value.float().clone()
    lo, hi = BOUNDS[field]
    count = value.shape[-1]
    if count > len(lo):
        raise ValueError("归一化通道数量不匹配")
    if field == "neutron" and not inverse:
        value = logarithm(value)
    if inverse:
        result = (value + 1) * 0.5 * (
            value.new_tensor(hi[:count]) - value.new_tensor(lo[:count])
        ) + value.new_tensor(lo[:count])
    else:
        result = (value - value.new_tensor(lo[:count])) / (
            value.new_tensor(hi[:count]) - value.new_tensor(lo[:count])
        ) * 2.0 - 1.0
    return logarithm(result, inverse=True) if field == "neutron" and inverse else result


def fsi_normalize(value, statistics, *, role="target", inverse=False):
    """四通道范围变换；input 与 target 的压力尺度各自独立。"""
    return signed_range(
        value, statistics[role]["minimum"], statistics[role]["maximum"], inverse=inverse
    )


def load_fsi_statistics(path):
    """读取原作者统计量顺序 max_input/min_input/max_target/min_target。"""
    maxima, minima, target_max, target_min = torch.load(path, map_location="cpu", weights_only=True)
    return {
        "input": {"minimum": minima.tolist(), "maximum": maxima.tolist()},
        "target": {"minimum": target_min.tolist(), "maximum": target_max.tolist()},
    }
