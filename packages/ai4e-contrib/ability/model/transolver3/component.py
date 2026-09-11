"""Transolver 组件出口和参考案例默认值；不持有工作流循环。"""

from copy import deepcopy

from .inference import SurfaceInference
from .model import SOURCE, construct, describe, predict

__all__ = ["SOURCE", "SurfaceInference", "construct", "describe", "predict", "resolve"]


def resolve(config, *, validate=True):
    """展开 Transolver 声明，不借用 AB-UPT 默认参数。"""
    cfg = deepcopy(config)
    parameters = cfg.setdefault("model", {}).setdefault("parameters", {})
    defaults = {
        "n_hidden": 256,
        "n_layers": 24,
        "n_head": 8,
        "mlp_ratio": 2,
        "slice_num": 64,
        "space_dim": 12,
        "fun_dim": 0,
        "out_dim": 4,
        "unified_pos": False,
        "gradient_checkpointing": True,
    }
    for key, value in defaults.items():
        parameters.setdefault(key, value)
    train = cfg.setdefault("train", {})
    defaults = {
        "max_epochs": 2,
        "batch_size": 1,
        "num_workers": 0,
        "device": "auto",
        "precision": "fp32",
        "optimizer": "adamw",
        "learning_rate": 0.001,
        "weight_decay": 0.0,
        "betas": [0.9, 0.999],
        "scheduler_unit": "epoch",
        "min_lr_ratio": 0.01,
        "gradient_clip": 1.0,
        "accumulate": 1,
        "validation_interval": 1,
        "evaluation_split": "validation",
        "best_on_equal": True,
        "restore_history": True,
        "loss_reduction": "elements",
        "snapshot": True,
        "save_on_interrupt": True,
    }
    for key, value in defaults.items():
        train.setdefault(key, value)
    sampling = cfg.setdefault("sampling", {})
    sampling.setdefault("seed", 2)
    sampling.setdefault("stride", 4)
    cfg.setdefault("post", {})
    if validate:
        if train["batch_size"] != 1 or train["num_workers"] != 0 or train["accumulate"] != 1:
            raise ValueError("参考流程需要批次 1、零读取子进程和无梯度累积")
        if train["evaluation_split"] != "validation" or train["precision"] != "fp32":
            raise ValueError("参考流程需要 validation 选优和 fp32")
        if train["max_epochs"] < 1 or train["validation_interval"] < 1:
            raise ValueError("训练轮数和验证间隔必须为正")
        if train["scheduler_unit"] != "epoch" or train["optimizer"] != "adamw":
            raise ValueError("当前参考优化为逐轮余弦调度和 AdamW")
        if cfg["sampling"].get("stride", 4) != 4:
            raise ValueError("参考训练抽稀步长为 4")
    return cfg


from .preparation import loss, predict_sample, prepare_sample

__all__ += ["loss", "predict_sample", "prepare_sample", "training_parameters"]


def training_parameters(config):
    """返回模型完整构造参数，不要求调用方解释布局。"""
    return dict(config["model"]["parameters"])


# 当前参考优化和点场损失的真实限制，供平台按能力呈现。
TRAINING_CONSTRAINTS = {
    "batch_size": {"allowed": [1], "readOnly": True},
    "num_workers": {"allowed": [0], "readOnly": True},
    "accumulate": {"allowed": [1], "readOnly": True},
    "precision": {"allowed": ["fp32"], "readOnly": True},
    "evaluation_split": {"allowed": ["validation"], "readOnly": True},
    "scheduler_unit": {"allowed": ["epoch"], "readOnly": True},
    "optimizer": {"allowed": ["adamw"], "readOnly": True},
}
PLATFORM_LOSSES = {
    "configurable": False,
    "fixed": "mse",
    "reason": "参考点场等权标准化逐元素均方误差",
}
