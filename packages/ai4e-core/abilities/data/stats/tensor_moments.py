# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""保留显式归约轴、计算精度和样本修正的张量统计。"""

import torch


def tensor_moments(
    values, *, axes: tuple[int, ...], dtype=torch.float32, correction=1, epsilon=1e-8
):
    """返回 mean/std；epsilon 在标准差之后相加，不改已有总体统计接口。"""
    tensor = torch.as_tensor(values).to(dtype=dtype)
    if not axes or len({a % tensor.ndim for a in axes}) != len(axes):
        raise ValueError("归约轴非法")
    if not torch.isfinite(tensor).all():
        raise ValueError("统计输入非有限")
    mean, std = tensor.mean(dim=axes), tensor.std(dim=axes, correction=correction)
    if not torch.isfinite(std).all():
        raise ValueError("统计自由度不足")
    return mean, std + epsilon


def sample_mean_square_moments(values, *, axes=(0, 1), epsilon=1e-8):
    """按样本顺序累加均值/平方均值，保留 float32 参考舍入顺序。"""
    if len(values) == 0:
        raise ValueError("样本为空")
    first = torch.as_tensor(values[0], dtype=torch.float32)
    mean = torch.zeros_like(first.mean(dim=axes))
    square = torch.zeros_like(mean)
    for value in values:
        tensor = torch.as_tensor(value, dtype=torch.float32)
        mean += tensor.mean(dim=axes) / len(values)
        square += (tensor * tensor).mean(dim=axes) / len(values)
    return mean, torch.sqrt(torch.clamp(square - mean * mean, min=0) + epsilon)
