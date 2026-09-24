"""NASA 全局代理及双圆柱降维代理的局部配置，运行器不解释模型参数。"""

import math
from copy import deepcopy
from importlib import import_module

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import load_recipe_config


def component(path):
    """解析用户显式选择的普通函数；不建立全仓组件注册或基类。"""
    if callable(path):
        return path
    if not isinstance(path, str) or "." not in path:
        raise ValueError("组件须为全限定函数路径或普通可调用对象")
    module, name = path.rsplit(".", 1)
    operation = getattr(import_module(module), name)
    if not callable(operation):
        raise TypeError("组件目标不可调用")
    return operation


def validate(cfg):
    """核本应用案例、模型族、阶段与总时限，模型细节仍由实际消费者检查。"""
    result = (
        OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else deepcopy(cfg)
    )
    if result["dataset"]["case"] not in {"nasa_global", "double_cylinder_pod"}:
        raise ValueError("未知代理案例")
    if result["model"]["family"] not in {"rsm", "rbf", "kriging", "lightgbm", "custom"}:
        raise ValueError("未知代理模型族")
    if not isinstance(result["model"]["parameters"], dict):
        raise TypeError("模型 parameters 须为字典")
    seconds = result["train"]["seconds"]
    if (
        not isinstance(seconds, (int, float))
        or isinstance(seconds, bool)
        or not math.isfinite(seconds)
        or not 0 < seconds <= 10800
    ):
        raise ValueError("每组合时限须为 (0,10800] 秒；累计计账由主控负责")
    stages = result["pipeline"]["stages"]
    if (
        not isinstance(stages, list)
        or not stages
        or len(set(stages)) != len(stages)
        or set(stages) - {"trainprep", "train", "infer", "post"}
    ):
        raise ValueError("阶段名单为空、重复或包含未知阶段")
    if "infer" in result and (
        type(result["infer"]["batch_size"]) is not int or result["infer"]["batch_size"] < 1
    ):
        raise ValueError("infer.batch_size 须为正整数")
    return result


def load_configuration(path, overrides=None):
    """从配置文件位置解析公共路径/覆盖，并校验代理局部配置。"""
    return validate(load_recipe_config(path, overrides))
