# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""规则标量场和位置轨迹的可组合编码，不识别模型或数据集名称。"""

import numpy as np
import torch

from ai4e_core.abilities.data.stats.tensor_moments import sample_mean_square_moments, tensor_moments

from .standardization import Standardization
from .trajectory import restore_trajectory


def scalar_statistics(arrays, *, names):
    """多个具名标量各自按样本及实体轴计算标量统计。"""
    result = {}
    for name in names:
        mean, std = tensor_moments(arrays[name], axes=tuple(range(arrays[name].ndim)))
        result[name] = {"mean": [float(mean)], "std": [float(std)]}
    return result


def position_statistics(arrays, *, name):
    """逐样本等权平方矩位置统计；最终分母包含参考的额外 epsilon。"""
    mean, std = sample_mean_square_moments(arrays[name])
    return {name: {"mean": mean.tolist(), "std": (std + 1e-8).tolist()}}


def standardizer(stats):
    """将冻结统计构造成可微正反变换。"""
    return Standardization(tuple(stats["mean"]), tuple(stats["std"]), arithmetic="divide")


def encode_scalar_grid(arrays, stats, *, input_name, target_name, coordinate_name):
    """合并坐标与归一化输入，保存归一化目标及物理真值。"""
    coeff = standardizer(stats[input_name]).apply(torch.from_numpy(arrays[input_name]).float())
    target = torch.from_numpy(arrays[target_name]).float()
    coords = torch.from_numpy(arrays[coordinate_name]).float()
    local = torch.cat((coords, coeff), dim=-1).numpy()
    return {
        "local_embedding": local,
        "geometry": local.copy(),
        "target": standardizer(stats[target_name]).apply(target).numpy(),
        "physical_target": target[:, None].numpy(),
        "coordinates": arrays[coordinate_name],
        "entity_ids": arrays["entity_ids"],
    }


def encode_position_trajectory(arrays, stats, *, position_name, dynamic_name, condition_name):
    """归一化位置并保留动态场尺度；初帧为输入，后续帧为目标。"""
    positions = (
        standardizer(stats[position_name]).apply(torch.from_numpy(arrays[position_name])).numpy()
    )
    coords = positions[:, 0]
    target = np.concatenate((positions[:, 1:], arrays[dynamic_name][:, 1:]), axis=-1)
    physical = np.concatenate((arrays[position_name][:, 1:], arrays[dynamic_name][:, 1:]), axis=-1)
    return {
        "local_embedding": coords,
        "local_positions": coords.copy(),
        "geometry": coords.copy(),
        "global_embedding": arrays[condition_name][:, None].astype(np.float32),
        "target": target,
        "physical_target": physical,
        "coordinates": arrays[position_name][:, 0],
        "entity_ids": arrays["entity_ids"],
    }


def decode_scalar_field(raw, item, *, stats, physical=True):
    """将标量输出还原为 [B,1,N,1] 物理场。"""
    value = standardizer(stats).inverse(raw) if physical else raw
    return value[:, None]


def decode_position_trajectory(raw, item, *, frames, channels, position_stats, physical):
    """还原输出布局并加回初态坐标，按需反归一化位置通道。"""
    result = restore_trajectory(
        raw, frames, channels, initial=item["local_embedding"], initial_channels=3
    )
    if physical:
        result[..., :3] = standardizer(position_stats).inverse(result[..., :3])
    return result


def preserve_geometry(encoded, arrays):
    """附带原实体身份及面连接，供独立推理/后处理重建网格。"""
    return {**encoded, "faces": arrays["faces"]}
