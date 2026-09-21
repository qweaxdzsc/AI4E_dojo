"""PCNO 可复制配置，公共路径由 core 解析，算法参数由贡献应用解释。"""

import importlib
import math
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import load_recipe_config, normalize_recipe_config

STAGES = ["rawprep", "trainprep", "train", "infer", "post"]


def component(value):
    """加载普通函数或用户复制目录中的组件。"""
    if callable(value):
        return value
    module, name = value.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)


def validate(cfg):
    """检查真实生效参数，不静默忽略错误的模型、预算或阶段。"""
    cfg = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else cfg
    expected = {
        "seed",
        "run_root",
        "data_root",
        "pipeline",
        "inputs",
        "model",
        "train",
        "infer",
        "post",
        "components",
    }
    if set(cfg) - {"execution"} != expected:
        raise ValueError("PCNO 顶层配置不完整或含未知键")
    cfg = normalize_recipe_config(cfg, base=Path.cwd())
    selected = cfg["pipeline"]["stages"]
    if selected != [s for s in STAGES if s in selected]:
        raise ValueError("阶段顺序非法")
    if set(cfg["model"]) != {"modes", "pres_width", "temp_width"}:
        raise ValueError("模型配置字段非法")
    if len(cfg["model"]["modes"]) != 4 or any(
        type(m) is not int or m < 1 for m in cfg["model"]["modes"]
    ):
        raise ValueError("谱模式非法")
    if any(
        type(cfg["model"][k]) is not int or cfg["model"][k] < 8 or cfg["model"][k] % 8
        for k in ["pres_width", "temp_width"]
    ):
        raise ValueError("宽度须为8的正倍数")
    if set(cfg["train"]) != {"updates", "device", "threads"}:
        raise ValueError("训练字段非法；更新预算与250轮原调度分开")
    if type(cfg["train"]["updates"]) is not int or not 1 <= cfg["train"]["updates"] <= 5250:
        raise ValueError("更新预算须在1至5250之间")
    if cfg["train"]["device"] not in ["cpu", "cuda"]:
        raise ValueError("当前四维复数FFT支持CPU或CUDA")
    if type(cfg["train"]["threads"]) is not int or cfg["train"]["threads"] < 1:
        raise ValueError("线程数非法")
    if set(cfg["infer"]) != {"source", "sample_ids", "device"} or cfg["infer"]["source"] not in [
        "training24",
        "demonstration18",
        "author18",
    ]:
        raise ValueError("推理来源非法")
    if cfg["infer"]["device"] not in ["cpu", "cuda"]:
        raise ValueError("推理设备须为CPU或CUDA")
    ids = cfg["infer"]["sample_ids"]
    if ids is not None and (not isinstance(ids, list) or not ids or len(ids) != len(set(ids))):
        raise ValueError("推理样本名单须非空且不重复或为null")
    if set(cfg["post"]) != {"temperature_threshold", "capacity_factor"}:
        raise ValueError("经济参数非法")
    if not 0 < cfg["post"]["capacity_factor"] <= 1 or not math.isfinite(
        cfg["post"]["temperature_threshold"]
    ):
        raise ValueError("经济参数范围非法")
    inputs = {
        "rawprep": {"source"},
        "trainprep": {"dataset"},
        "train": {"preparation", "pres_resume", "temp_resume"},
        "infer": {"preparation", "checkpoints"},
        "post": {"results"},
    }
    if set(cfg["inputs"]) != set(inputs):
        raise ValueError("阶段输入不完整")
    for stage, names in inputs.items():
        if set(cfg["inputs"][stage]) != names:
            raise ValueError("阶段输入字段非法: " + stage)
    if set(cfg["components"]) != {"network", "objective"}:
        raise ValueError("组件声明非法")
    return cfg


def load_configuration(path, overrides=None):
    """从文件或覆盖项读取配置，路径相对配置文件。"""
    return validate(load_recipe_config(path, overrides))
