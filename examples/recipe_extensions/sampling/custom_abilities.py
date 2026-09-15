"""用户样本组织能力：保留模型布局，反转几何抽样顺序。"""

import torch

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs


def reverse_geometry(fields, config, **kwargs):
    """按当前预算选末端几何点；其余采样保留种子、轮次与原模型行为。"""
    count = len(fields[kwargs["bindings"]["geometry_field"]])
    budget = min(count, int(config["geometry"]["max_points"]))
    indices = dict(kwargs.pop("indices", None) or {})
    indices["geometry"] = torch.arange(count - 1, count - budget - 1, -1)
    return prepare_inputs(fields, config, indices=indices, **kwargs)
