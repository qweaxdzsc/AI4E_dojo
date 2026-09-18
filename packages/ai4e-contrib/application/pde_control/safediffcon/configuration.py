"""控制案例的参数检查与显式路径解析，复制 recipe 不需要注册。"""

import importlib
import os
from pathlib import Path

from omegaconf import OmegaConf

_KEYS = {
    "case": None,
    "seed": None,
    "run_root": None,
    "data": {"root", "output", "physical", "prepared"},
    "model": {"dim", "ddim_steps"},
    "train": {"updates", "batch_size", "lr", "device", "resume"},
    "posttrain": {
        "rounds",
        "updates_per_round",
        "subset_size",
        "batch_size",
        "calibration_samples",
        "alpha",
        "weight",
        "lr",
        "checkpoint",
    },
    "infer": {
        "device",
        "adaptation_updates",
        "test_samples",
        "batch_size",
        "weight",
        "lr",
        "checkpoint",
    },
    "solver": {"python", "assets", "timeout_seconds"},
    "post": {"results"},
    "components": {"reader", "transform", "model", "objective", "guide", "metrics", "derived"},
}


def _validate_domain(value: dict) -> dict:
    """程序入口与文件入口共用检查，拒绝拼错参数与未授权长训练。"""
    if set(value) - {"pipeline", "execution"} != set(_KEYS):
        raise ValueError(f"案例配置字段不完整或未知: {set(value) ^ set(_KEYS)}")
    for key, allowed in _KEYS.items():
        if allowed is not None and set(value[key]) != allowed:
            raise ValueError(f"{key} 配置字段不完整或未知: {set(value[key]) ^ allowed}")
    if value["case"] not in {"burgers", "tokamak"}:
        raise ValueError("未知控制案例")
    # updates 是包含已恢复步数的总目标；墙钟预算由外层累计监督器负责。
    # 保留短实验规模门禁，不能用步数上限代替实际耗时限制。
    if type(value["train"]["updates"]) is not int or not 1 <= value["train"]["updates"] <= 20000:
        raise ValueError("短实验的预训练总更新数须为 1–20000；仍须累计限时")
    if value["posttrain"]["rounds"] != 2:
        raise ValueError("本模板明确执行两轮后训练，其他流程请编辑 Python")
    for section, key, limit in [
        ("train", "batch_size", 256),
        ("posttrain", "batch_size", 256),
        ("posttrain", "updates_per_round", 320),
        ("posttrain", "subset_size", 48950),
        ("posttrain", "calibration_samples", 1000),
        ("infer", "test_samples", 50),
        ("infer", "batch_size", 50),
    ]:
        if not 1 <= value[section][key] <= limit:
            raise ValueError(f"{section}.{key} 超出支持范围")
    if (
        not 0 <= value["infer"]["adaptation_updates"] <= 5
        or not 0 < value["posttrain"]["alpha"] < 1
    ):
        raise ValueError("推理适配或置信度非法")
    if (
        value["model"]["dim"] < 8
        or value["model"]["dim"] % 8
        or not 1 <= value["model"]["ddim_steps"] <= 1000
    ):
        raise ValueError("网络宽度或 DDIM 步数非法")
    for section in ("train", "posttrain", "infer"):
        if value[section]["lr"] <= 0:
            raise ValueError("学习率须为正")
    for section in ("posttrain", "infer"):
        if value[section]["weight"] < 0:
            raise ValueError("安全权重不能为负")
    if value["train"]["device"] != value["infer"]["device"]:
        raise ValueError("当前完整流程训练和推理设备必须一致")
    return value


def application_parameters(config, *, stage="train"):
    """将公共用户配置绑定为本领域调用参数，不改变保存的用户配置。"""
    from copy import deepcopy

    from ai4e_core.base.config.conventions import input_bindings, require_current_keys

    value = (
        OmegaConf.to_container(config, resolve=True)
        if OmegaConf.is_config(config)
        else deepcopy(config)
    )
    require_current_keys(
        value,
        {
            "data": "inputs 与 data_root",
            "train.resume": "inputs.train.resume",
            "posttrain.checkpoint": "inputs.posttrain.checkpoint",
            "infer.checkpoint": "inputs.infer.checkpoint",
            "post.results": "inputs.post.results",
            "solver.assets": "inputs.infer.solver_assets",
        },
    )
    input_bindings(value)
    inputs = value.pop("inputs")
    output = value.pop("data_root")
    for name in ("dataset", "rawprep", "trainprep"):
        value.pop(name, None)
    splits = ("train", "cal", "test")

    def references(section, prefix, names=splits):
        found = {s: inputs.get(section, {}).get(prefix + "_" + s) for s in names}
        if not any(v is not None for v in found.values()):
            return None
        if any(v is None for v in found.values()):
            raise ValueError(f"{section} 缺少完整分片引用")
        return found

    value["data"] = {
        "output": output,
        "physical": references("trainprep", "dataset"),
        "prepared": references(stage, "preparation")
        if stage in ("train", "posttrain", "infer")
        else None,
    }
    value["data"]["root"] = inputs["rawprep"]["source"]
    value["posttrain"]["checkpoint"] = inputs["posttrain"]["checkpoint"]
    value["post"]["results"] = inputs["post"].get("results")
    value["train"]["resume"] = inputs["train"].get("resume")
    value["infer"]["checkpoint"] = inputs["infer"].get("checkpoint")
    value["solver"]["assets"] = inputs["infer"].get("solver_assets")
    return _validate_domain(value)


def validate(config):
    """校验公共配置；返回用户树，内部领域参数不注入冻结配置。"""
    application_parameters(config)
    return OmegaConf.to_container(config, resolve=True) if OmegaConf.is_config(config) else config


def load_configuration(path: str | Path, overrides=None) -> dict:
    """配置文件和程序调用采用同一公共输入树。"""
    from ai4e_core.base.config.conventions import load_recipe_config

    value = load_recipe_config(path, overrides)
    if value["solver"].get("python"):
        # executable是环境入口；resolve会追随venv符号链接，丢失site-packages。
        value["solver"]["python"] = os.path.abspath(
            Path(path).absolute().parent / Path(value["solver"]["python"]).expanduser()
        )
    validate(value)
    return value


def component(path: str | None):
    """从公开路径加载普通函数，None 表示显式未选派生字段。"""
    if path is None:
        return None
    module, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)
