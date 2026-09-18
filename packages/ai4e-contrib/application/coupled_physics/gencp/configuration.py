"""GenCP 案例配置加载、路径解析与显式用户能力加载。"""

import importlib
from pathlib import Path

from omegaconf import OmegaConf


def load_configuration(path, overrides=None):
    """相对路径均以配置文件为基准，覆盖后再展开插值。"""
    from ai4e_core.base.config.conventions import load_recipe_config, require_current_keys

    value = load_recipe_config(path, overrides)
    require_current_keys(value, {
        "data.root": "inputs.rawprep.source", "data.processed_root": "data_root",
        "paths.output": "data_root", "train.preparation": "inputs.train.preparation",
        "train.resume": "inputs.train.resume", "infer.checkpoints": "inputs.infer.checkpoint",
        "post.results": "inputs.post.results",
    })
    if value["train"].get("single_points", 10) < 2 or value["infer"]["flow_steps"] < 1:
        raise ValueError("单场网格至少两个点，耦合积分至少一步")
    if value["dataset"]["name"] not in {"ntcouple", "double_cylinder", "turek_hron"}:
        raise ValueError("未知数据集")
    if value["profile"] != "scaled":
        raise ValueError("当前验收入口只接受 scaled，不能将缩小实验标成论文复现")
    if not 1 <= value["train"]["updates"] <= 1000 or value["train"]["batch_size"] < 1:
        raise ValueError("缩小训练预算非法")
    for name, field in value["fields"].items():
        settings = {**value["train"], **field}
        for key in ("updates", "batch_size", "updates_per_run"):
            number = settings.get(key, settings["updates"])
            if isinstance(number, bool) or not isinstance(number, int) or number < 1:
                raise ValueError(f"场 {name} 的 {key} 必须为正整数")
        if not 1 <= settings["updates"] <= 1000 or settings["batch_size"] < 1:
            raise ValueError(f"场 {name} 的缩小训练预算非法")
    return value


def component(path):
    """加载用户普通函数，不要求继承或注册。"""
    module, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)
