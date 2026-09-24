"""Transolver 官方参数连接；训练参考限制不进入模型网络。"""

from copy import deepcopy


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
        # 现行准备将 validation 命名为 eval；两者指向同一评价切片。
        if train["evaluation_split"] not in {"validation", "eval"} or train["precision"] != "fp32":
            raise ValueError("参考流程需要 eval（旧名 validation）选优和 fp32")
        if train["max_epochs"] < 1 or train["validation_interval"] < 1:
            raise ValueError("训练轮数和验证间隔必须为正")
        if train["scheduler_unit"] != "epoch" or train["optimizer"] != "adamw":
            raise ValueError("当前参考优化为逐轮余弦调度和 AdamW")
        if cfg["sampling"].get("stride", 4) != 4:
            raise ValueError("参考训练抽稀步长为 4")
    return cfg
