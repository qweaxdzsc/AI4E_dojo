"""圆柱案例配置及普通组件加载；公共路径沿用core约定。"""

import importlib
import math
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import load_recipe_config, normalize_recipe_config


def component(value):
    """加载研究者提供的普通构造函数。"""
    if callable(value):
        return value
    module, name = value.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)


def validate(cfg):
    """验证实际使用的预算、维度、设备与阶段参数。"""
    cfg = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else cfg
    cfg = normalize_recipe_config(cfg, base=Path.cwd())
    expected = {
        "seed",
        "run_root",
        "data_root",
        "pipeline",
        "inputs",
        "dataset",
        "model",
        "train",
        "loss",
        "infer",
        "components",
    }
    if set(cfg) - {"execution"} != expected:
        raise ValueError("圆柱配置缺键或含未知顶层键")
    stages = ["rawprep", "trainprep", "train", "infer", "post"]
    if cfg["pipeline"]["stages"] != [s for s in stages if s in cfg["pipeline"]["stages"]]:
        raise ValueError("阶段顺序非法")
    if cfg["dataset"] != {"case": "double_cylinder"} and cfg["dataset"] != {
        "case": "cylinder_flow"
    }:
        raise ValueError("案例非法")
    if set(cfg["model"]) != {"modes", "width", "blocks", "history", "horizon"}:
        raise ValueError("网络配置非法")
    if len(cfg["model"]["modes"]) != 3 or any(
        type(v) is not int or v < 1
        for v in [*cfg["model"]["modes"], *[v for k, v in cfg["model"].items() if k != "modes"]]
    ):
        raise ValueError("网络维度须为正整数")
    if set(cfg["train"]) != {"updates", "batch_size", "device", "threads", "learning_rate"}:
        raise ValueError("训练参数非法")
    for key in ("updates", "threads"):
        if type(cfg["train"][key]) is not int or cfg["train"][key] < 1:
            raise ValueError("更新数或线程数非法")
    if cfg["train"]["device"] != "cpu" or cfg["train"]["batch_size"] != 1:
        raise ValueError("本轮验收设备为CPU，batch_size为1")
    if not math.isfinite(cfg["train"]["learning_rate"]) or cfg["train"]["learning_rate"] <= 0:
        raise ValueError("学习率非法")
    if set(cfg["loss"]) != {
        "warmup_fraction",
        "ramp_fraction",
        "gradient_weight",
        "divergence_weight",
    }:
        raise ValueError("损失配置非法")
    loss = cfg["loss"]
    if (
        not all(math.isfinite(v) for v in loss.values())
        or not 0 < loss["warmup_fraction"] < 1
        or not 0 < loss["ramp_fraction"] <= 1 - loss["warmup_fraction"]
        or min(loss["gradient_weight"], loss["divergence_weight"]) < 0
    ):
        raise ValueError("损失调度非法")
    if cfg["infer"] != {"split": "val"}:
        raise ValueError("当前已准入案例仅开放固定val评价")
    if set(cfg["components"]) != {"network"}:
        raise ValueError("组件参数非法")
    inputs = {
        "rawprep": {"source"},
        "trainprep": {"dataset"},
        "train": {"preparation", "resume"},
        "infer": {"preparation", "checkpoints"},
        "post": {"results"},
    }
    if set(cfg["inputs"]) != set(inputs) or any(
        set(cfg["inputs"][k]) != v for k, v in inputs.items()
    ):
        raise ValueError("阶段输入字段非法")
    return cfg


def load_configuration(path, overrides=None):
    """路径以配置文件为准；程序调用使用相同验证。"""
    return validate(load_recipe_config(path, overrides))
