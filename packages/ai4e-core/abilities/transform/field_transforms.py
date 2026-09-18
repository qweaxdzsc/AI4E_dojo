"""冻结可逆场变换，明确常量分量和浮点运算顺序。"""

import torch


def signed_range(value, minimum, maximum, *, inverse=False):
    """参考范围映射到 [-1,1]；常量跨度用 1，不截断输出。"""
    lo, hi = value.new_tensor(minimum), value.new_tensor(maximum)
    if not torch.isfinite(lo).all() or not torch.isfinite(hi).all() or (hi < lo).any():
        raise ValueError("归一化范围非法")
    span = torch.where(hi == lo, torch.ones_like(hi), hi - lo)
    return (value + 1) * span / 2 + lo if inverse else 2 * (value - lo) / span - 1


def logarithm(value, *, inverse=False):
    """保持 log(x+1)/exp(x)-1 算术；不以 log1p 改变参考舍入。"""
    if not inverse and (value <= -1).any():
        raise ValueError("对数变换要求值大于 -1")
    return torch.exp(value) - 1 if inverse else torch.log(value + 1)
