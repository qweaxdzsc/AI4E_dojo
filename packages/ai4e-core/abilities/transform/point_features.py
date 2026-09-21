"""按显式字段顺序拼接点特征，不推断数据集或模型语义。"""

from collections.abc import Mapping, Sequence

import torch


def concatenate_fields(
    fields: Mapping[str, torch.Tensor], names: Sequence[str], *, ids: torch.Tensor
) -> torch.Tensor:
    """返回 [N,C] 特征；同一实体组须使用唯一的一维整数身份。"""
    if ids.ndim != 1 or ids.dtype not in (torch.int32, torch.int64):
        raise ValueError("实体身份须为一维整数")
    if not len(ids) or len(torch.unique(ids)) != len(ids):
        raise ValueError("实体身份为空或重复")
    if not names or len(set(names)) != len(names):
        raise ValueError("特征字段为空或重复")
    values = []
    for name in names:
        value = fields[name]
        if value.ndim != 2 or len(value) != len(ids) or not torch.isfinite(value).all():
            raise ValueError(f"{name}: 点特征行数、维数或有限性非法")
        values.append(value)
    return torch.cat(values, dim=-1)
