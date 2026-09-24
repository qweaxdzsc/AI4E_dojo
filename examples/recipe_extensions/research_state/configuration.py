"""扩展局部研究参数；基案例配置继续由原公开校验器解释。"""

import math
from copy import deepcopy

from ai4e_contrib.application.geotransolver import component
from ai4e_contrib.application.geotransolver import validate as validate_base
from ai4e_core.base.config.conventions import load_recipe_config


def validate(value):
    """仅增加验证周期、EMA系数及原始训练留出人数，不修改公共配置树。"""
    value = deepcopy(value)
    extra = {
        name: value["train"].pop(name)
        for name in ("evaluate_every", "ema_decay", "validation_count")
    }
    if any(
        type(extra[key]) is not int or extra[key] < 1
        for key in ("evaluate_every", "validation_count")
    ):
        raise ValueError("验证周期及人数须为正整数")
    if not math.isfinite(extra["ema_decay"]) or not 0 <= extra["ema_decay"] < 1:
        raise ValueError("EMA系数须在[0,1)")
    resolved = validate_base(value)
    resolved["train"].update(extra)
    return resolved


def load_configuration(path, overrides=None):
    """文件和点号覆盖先解析相对路径，再经过同一局部校验。"""
    return validate(load_recipe_config(path, overrides))


__all__ = ["component", "load_configuration", "validate"]
