"""GeoTransolver 网络参数与参考优化策略的语义绑定。"""

import torch

from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
from ai4e_core.abilities.training.parameter_partition import partition_parameters
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler


def build_model(options: dict):
    """普通 PyTorch 网络；未知扩展由网络入口明确拒绝。"""
    from ai4e_contrib.ability.model.geotransolver import GeoTransolver

    return GeoTransolver(**options)


def build_optimizer(model, *, lr, weight_decay):
    """二维参数选择 Muon，其余选择 AdamW；计算/状态实现属于 core。"""
    groups = partition_parameters(
        model, {"matrix": lambda n, p: p.ndim == 2, "other": lambda n, p: p.ndim != 2}
    )
    optimizers = []
    if groups["matrix"]:
        optimizers.append(
            torch.optim.Muon(
                groups["matrix"], lr=lr, weight_decay=weight_decay, adjust_lr_fn="match_rms_adamw"
            )
        )
    if groups["other"]:
        optimizers.append(torch.optim.AdamW(groups["other"], lr=lr, weight_decay=weight_decay))
    return CombinedOptimizer(optimizers)


def build_scheduler(optimizer, *, policy, updates_per_epoch, epochs, end_lr):
    """保留原研究的逐更新预热/余弦或逐轮余弦，不按短训目标压缩日程。"""
    if policy == "warmup_cosine":
        warmup = updates_per_epoch * 2
        return torch.optim.lr_scheduler.SequentialLR(
            optimizer,
            [
                torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=0.01, total_iters=warmup),
                torch.optim.lr_scheduler.CosineAnnealingLR(
                    optimizer, T_max=updates_per_epoch * epochs - warmup, eta_min=end_lr
                ),
            ],
            milestones=[warmup],
        )
    if policy == "epoch_cosine":
        return EpochBoundaryScheduler(
            torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=end_lr),
            updates_per_epoch,
        )
    raise ValueError("未知调度策略")


def component(path):
    """显式全限定路径或普通函数，不建立注册表。"""
    import importlib

    if path is None or callable(path):
        return path
    module, name = path.rsplit(".", 1)
    return getattr(importlib.import_module(module), name)


def validate(config):
    """文件、覆盖和程序调用共用公共路径及参数检查。"""
    from pathlib import Path

    from omegaconf import OmegaConf

    config = OmegaConf.to_container(config, resolve=True) if OmegaConf.is_config(config) else config
    from ai4e_core.base.config.conventions import normalize_recipe_config, require_current_keys

    require_current_keys(
        config,
        {
            "data": "inputs",
            "train.resume": "inputs.train.resume",
            "infer.checkpoint": "inputs.infer.checkpoint",
        },
    )
    expected = {
        "seed",
        "run_root",
        "data_root",
        "pipeline",
        "inputs",
        "model",
        "train",
        "infer",
        "components",
    }
    if set(config) - {"execution"} != expected:
        raise ValueError("配置顶层字段缺失或未知")
    required = {
        "train": {
            "updates",
            "batch_size",
            "lr",
            "weight_decay",
            "schedule",
            "schedule_epochs",
            "end_lr",
            "device",
            "seconds",
            "checkpoint_every",
        },
        "infer": {"batch_size", "device"},
        "components": {"loss", "derived", "consume"},
    }
    for name, keys in required.items():
        if set(config[name]) != keys:
            raise ValueError(f"{name} 字段缺失或未知")
    import math

    for name in ("lr", "weight_decay", "end_lr", "seconds"):
        if not math.isfinite(config["train"][name]) or config["train"][name] < 0:
            raise ValueError(f"train.{name} 须为有限非负数")
    if config["model"].get("include_local_features", False):
        radii = config["model"].get("radii", [])
        neighbors = config["model"].get("neighbors_in_radius", [])
        if not radii or len(radii) != len(neighbors) or any(r <= 0 for r in radii):
            raise ValueError("局部编码须显式提供正半径及对应邻居数")
    inputs = {
        "rawprep": {"source"},
        "trainprep": {"dataset"},
        "train": {"preparation", "resume"},
        "infer": {"preparation", "checkpoint"},
        "post": {"results"},
    }
    if set(config["inputs"]) != set(inputs) or any(
        set(config["inputs"][s]) != keys for s, keys in inputs.items()
    ):
        raise ValueError("阶段输入字段缺失或未知")
    for key in ("updates", "batch_size", "checkpoint_every", "schedule_epochs"):
        if type(config["train"][key]) is not int or config["train"][key] < 1:
            raise ValueError(f"train.{key} 须为正整数")
    if (
        config["infer"]["batch_size"] < 1
        or config["train"]["seconds"] <= 0
        or config["train"]["lr"] <= 0
    ):
        raise ValueError("批量、预算和学习率须为正")
    stages = ["rawprep", "trainprep", "train", "infer", "post"]
    selected = config["pipeline"]["stages"]
    if not selected or selected != [stage for stage in stages if stage in selected]:
        raise ValueError("阶段须为无重复的顺序子集")
    return normalize_recipe_config(config, base=Path.cwd())


def load_configuration(path, overrides=None):
    """按配置所在目录解析所有相对路径，支持点号覆盖。"""
    from ai4e_core.base.config.conventions import load_recipe_config

    return validate(load_recipe_config(path, overrides))
