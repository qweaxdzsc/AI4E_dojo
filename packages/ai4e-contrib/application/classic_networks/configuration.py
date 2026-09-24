"""经典案例的配置及普通构造器选择；不创建全仓网络注册机制。"""

import math
from copy import deepcopy
from importlib import import_module

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import load_recipe_config


def component(path):
    """解析显式全限定函数，不要求继承专用基类。"""
    if path is None:
        return None
    module, name = path.rsplit(".", 1)
    return getattr(import_module(module), name)


def validate(cfg):
    """局部校验数据和训练参数，缺值不静默回落到另一种研究。"""
    value = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else deepcopy(cfg)
    data, model = value["dataset"], value["model"]
    if data["case"] not in {"darcy", "shapenet_volume", "double_cylinder"}:
        raise ValueError("未知经典数据案例")
    if any(type(data[k]) is not int or data[k] < 1 for k in ("train_count", "test_count")):
        raise ValueError("样本计数必须为正整数")
    if model["family"] not in {
        "mlp",
        "cnn",
        "resnet",
        "unet",
        "transformer",
        "gnn",
        "rnn",
        "custom",
    }:
        raise ValueError("未知模型族")
    if (model["family"] == "rnn") != (data["case"] == "double_cylinder") and model[
        "family"
    ] != "custom":
        raise ValueError("循环基线只绑定真实时间窗口")
    for key in ("updates", "batch_size", "checkpoint_every"):
        if type(value["train"][key]) is not int or value["train"][key] < 1:
            raise ValueError(f"train.{key}必须为正整数")
    if value["train"]["batch_size"] != 1:
        raise ValueError("本批对照冻结batch_size=1；改研究需另声明协议")
    if (
        not 0 < value["train"]["seconds"] <= 10800
        or not math.isfinite(value["train"]["lr"])
        or value["train"]["lr"] <= 0
    ):
        raise ValueError("训练时限或学习率非法")
    points = value["train"]["sample_points"]
    if points is not None and (type(points) is not int or points < 1):
        raise ValueError("sample_points必须为正整数或null")
    if data["case"] == "darcy" and (type(data["stride"]) is not int or data["stride"] < 1):
        raise ValueError("Darcy采样步长须为正整数")
    if data["case"] == "shapenet_volume" and (
        type(data["grid_size"]) is not int or data["grid_size"] < 2
    ):
        raise ValueError("三维格点数须为至少2的整数")
    expected = {"darcy": (3, 1, 2), "shapenet_volume": (5, 3, 3), "double_cylinder": (4, 4, 2)}[
        data["case"]
    ]
    if tuple(model[k] for k in ("in_channels", "out_channels", "spatial_dims")) != expected:
        raise ValueError("模型通道/空间维度不符合所选数据绑定")
    if not value["components"]["model"]:
        raise ValueError("须显式声明模型构造器")
    allowed = {"rawprep", "trainprep", "train", "infer", "post"}
    if set(value["pipeline"]["stages"]) - allowed:
        raise ValueError("未知研究步骤")
    return value


def load_configuration(path, overrides=None):
    """以配置位置解析输入/输出路径及覆盖，再检查局部含义。"""
    return validate(load_recipe_config(path, overrides))
