"""可复制 WDNO 配置：严格校验、相对路径和普通函数加载。"""

import importlib
import math
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import (
    load_recipe_config,
    normalize_recipe_config,
    require_current_keys,
)

STAGES = ["rawprep", "trainprep", "train", "infer", "post"]
INPUTS = {
    "rawprep": {"source", "indices"},
    "trainprep": {"dataset", "validation", "test"},
    "train": {"preparation", "validation", "test", "resume"},
    "infer": {"preparation", "validation", "test", "checkpoint"},
    "post": {"validation", "test"},
}
RETIRED = {
    "data": "inputs.<stage> / data_root",
    "train.resume": "inputs.train.resume",
    "infer.checkpoint": "inputs.infer.checkpoint",
    "post.results": "inputs.post",
}

_KEYS = {
    "seed": None,
    "run_root": None,
    "data_root": None,
    "inputs": set(INPUTS),
    "model": {"dim", "dim_mults", "groups", "ddim_steps"},
    "train": {"updates", "batch_size", "lr", "device", "seconds"},
    "infer": {"device", "batch_size", "checkpoint_format"},
    "components": {"reader", "transform", "network", "objective", "predict", "metrics", "derived"},
}


def validate(value: dict) -> dict:
    """文件、覆盖与程序入口共用检查，拼错参数不能静默忽略。"""
    value = OmegaConf.to_container(value, resolve=True) if OmegaConf.is_config(value) else value
    require_current_keys(value, RETIRED)
    if set(value) - {"pipeline", "execution"} != set(_KEYS):
        raise ValueError("WDNO 顶层配置字段不完整或未知")
    for key, allowed in _KEYS.items():
        actual = set(value[key]) if allowed is not None else set()
        if key == "components":
            actual -= {"optimizer", "scheduler", "update"}
        if allowed is not None and actual != allowed:
            raise ValueError(f"{key} 配置字段不完整或未知")
    for name in ("optimizer", "scheduler", "update"):
        target = value["components"].get(name)
        if (
            target is not None
            and not callable(target)
            and (not isinstance(target, str) or "." not in target)
        ):
            raise ValueError(f"components.{name} 须为模块级函数路径或普通函数")
    for item in [
        value["seed"],
        value["model"]["dim"],
        value["model"]["groups"],
        value["model"]["ddim_steps"],
        value["train"]["updates"],
        value["train"]["batch_size"],
        value["infer"]["batch_size"],
    ]:
        if type(item) is not int or item < 0:
            raise ValueError("整数参数非法")
    m, t = value["model"], value["train"]
    if (
        m["dim"] < 8
        or m["groups"] < 1
        or m["dim"] % m["groups"]
        or not 1 <= m["ddim_steps"] <= 1000
    ):
        raise ValueError("网络宽度/分组或采样步数非法")
    if (
        not m["dim_mults"]
        or len(m["dim_mults"]) > 4
        or any(type(x) is not int or x < 1 for x in m["dim_mults"])
    ):
        raise ValueError("网络层级非法")
    if t["updates"] < 1 or min(t["batch_size"], value["infer"]["batch_size"]) < 1:
        raise ValueError("训练或推理批量非法")
    if (
        not math.isfinite(t["lr"])
        or t["lr"] <= 0
        or not math.isfinite(t["seconds"])
        or t["seconds"] <= 0
    ):
        raise ValueError("学习率和阶段时间须为正")
    if value["infer"]["checkpoint_format"] not in ("dojo", "source"):
        raise ValueError("检查点格式必须显式指定 dojo/source")
    for stage, keys in INPUTS.items():
        if not isinstance(value["inputs"][stage], dict) or set(value["inputs"][stage]) != keys:
            raise ValueError(f"inputs.{stage} 配置字段不完整或未知")
    value = normalize_recipe_config(value, base=Path.cwd())
    selected = value.get("pipeline", {}).get("stages", STAGES)
    if not selected or selected != [stage for stage in STAGES if stage in selected]:
        raise ValueError("WDNO 阶段必须为非空、无重复的研究顺序子集")
    value["pipeline"] = {"stages": selected}
    return value


def load_configuration(path: str | Path, overrides=None) -> dict:
    """配置文件和程序调用采用同一公共输入树。"""
    value = load_recipe_config(path, overrides)
    return validate(value)


def component(path):
    """组件可直接传普通 callable；字符串只负责定位，不注册。"""
    if path is None or callable(path):
        return path
    module, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)
