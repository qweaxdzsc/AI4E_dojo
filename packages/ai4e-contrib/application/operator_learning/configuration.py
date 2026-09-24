"""算子案例参数与现有场数据准备连接；配置不进入通用运行器。"""

import math
from copy import deepcopy

from ai4e_contrib.application.classic_networks.configuration import component
from ai4e_contrib.application.classic_networks.configuration import validate as validate_field
from ai4e_core.base.config.conventions import load_recipe_config

__all__ = ["component", "load_configuration", "validate"]


def validate(cfg):
    """复用字段/准备检查，独立校验算子布局和物理目标。"""
    cfg = deepcopy(cfg)
    family = cfg["model"]["family"]
    if family not in {"deeponet", "fno"}:
        raise ValueError("未知算子模型")
    compatible = deepcopy(cfg)
    compatible["model"]["family"] = "custom"
    cfg = validate_field(compatible)
    cfg["model"]["family"] = family
    if cfg["train"]["sample_points"] is not None:
        raise ValueError("本案例算子训练消费完整规则场")
    weight = cfg["train"].get("physical_weight", 0.0)
    if not math.isfinite(weight) or weight < 0:
        raise ValueError("物理约束权重须非负有限")
    if weight and cfg["dataset"]["case"] != "darcy":
        raise ValueError("本轮物理约束仅准入Darcy")
    if family == "deeponet" and cfg["dataset"]["case"] == "double_cylinder":
        raise ValueError("本轮双圆柱仅提供历史通道FNO连接")
    if len(cfg["model"]["grid_shape"]) != cfg["model"]["spatial_dims"] or any(
        type(n) is not int or n < 2 for n in cfg["model"]["grid_shape"]
    ):
        raise ValueError("网格维数不符")
    cfg["train"]["physical_weight"] = float(weight)
    return cfg


def load_configuration(path, overrides=None):
    """复用公开路径解析与点号覆盖。"""
    return validate(load_recipe_config(path, overrides))
