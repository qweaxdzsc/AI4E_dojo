"""十三个经典网络小数据组合及显式时间预估，不执行训练。"""

from __future__ import annotations

import math
from copy import deepcopy
from pathlib import Path

import yaml

FAMILIES = ("mlp", "cnn", "resnet", "unet", "gnn", "transformer")
COMBINATIONS = tuple(
    (case, family) for family in FAMILIES for case in ("darcy", "shapenet_volume")
) + (("double_cylinder", "rnn"),)
UPDATE_CANDIDATES = (100, 50, 20)
TARGET_SECONDS = 9000.0


def model_parameters(family, spatial_dims):
    """匹配当前实际核心构造签名；不把分类网络名冒充原论文设置。"""
    if spatial_dims not in (2, 3):
        raise ValueError("只支持二维或三维")
    parameters = {
        "mlp": {"hidden_features": [64, 64, 64], "activation": "gelu"},
        "cnn": {"hidden_channels": 16, "hidden_layers": 4},
        "resnet": {"base_channels": 16},
        "unet": {"base_channels": 8, "levels": 3},
        "transformer": {
            "patch_shape": [5, 5] if spatial_dims == 2 else [4, 4, 4],
            "dim": 64,
            "num_heads": 4,
            "num_layers": 2,
            "feed_forward_dim": 256,
            "dropout": 0.0,
        },
        "gnn": {"hidden_dim": 64, "processor_layers": 3, "aggregation": "sum"},
        "rnn": {"hidden_size": 32, "num_layers": 2},
    }
    if family not in parameters:
        raise ValueError(f"未知组合模型族: {family}")
    return deepcopy(parameters[family])


def configuration_for(case, family, *, updates=100, recipe_root=None):
    """复制三基配置并覆盖明确模型参数；保持数据来源与阶段接口交由主控。"""
    if (case, family) not in COMBINATIONS:
        raise ValueError("不在十三组合协议内")
    if updates not in UPDATE_CANDIDATES:
        raise ValueError("正式候选更新数只允许100/50/20")
    if recipe_root is None:
        recipe_root = Path(__file__).resolve().parents[3] / "recipes" / "classic_networks"
    cfg = yaml.safe_load((Path(recipe_root) / case / "config.yaml").read_text())
    cfg["model"]["family"] = family
    cfg["model"]["parameters"] = model_parameters(family, cfg["model"]["spatial_dims"])
    cfg["train"]["updates"] = updates
    cfg["train"]["checkpoint_every"] = min(20, updates)
    cfg["train"]["seconds"] = TARGET_SECONDS
    cfg["components"]["model"] = "ai4e_contrib.application.classic_networks.binding.build_network"
    return cfg


def select_updates(
    dojo_step_seconds,
    reference_step_seconds=None,
    *,
    available_seconds=10800.0,
    spent_seconds=0.0,
    fixed_seconds=60.0,
    reference_factor=1.0,
    dojo_train_factor=1.0,
    evaluation_factor=0.25,
    recovery_factor=0.10,
    safety_factor=1.5,
):
    """按实测一步耗时选择最大候选，使预计整组计算不超过150分钟。

    固定项须含尚未记账的准备/保存等开销；评价与恢复系数以一侧等量更新计算
    为基准，采用两侧较慢一步估算。系数与分项随结果交付，不伪装成实测。
    available_seconds给出硬预算剩余额度；spent_seconds显式记录已计账开销，
    计入150分钟总预计，但不再乘安全系数或放入fixed_seconds重复计入。
    """
    reference_step_seconds = (
        dojo_step_seconds if reference_step_seconds is None else reference_step_seconds
    )
    values = (
        dojo_step_seconds,
        reference_step_seconds,
        available_seconds,
        spent_seconds,
        fixed_seconds,
        reference_factor,
        dojo_train_factor,
        evaluation_factor,
        recovery_factor,
        safety_factor,
    )
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("耗时和系数必须是有限非负数")
    if (
        min(dojo_step_seconds, reference_step_seconds, reference_factor, dojo_train_factor) <= 0
        or safety_factor < 1
    ):
        raise ValueError("双方测速与训练系数必须为正，安全系数至少为1")
    ceiling = max(0.0, min(TARGET_SECONDS - spent_seconds, available_seconds))
    coefficients = {
        "reference": reference_factor,
        "dojo_train": dojo_train_factor,
        "evaluation": evaluation_factor,
        "recovery": recovery_factor,
        "safety": safety_factor,
    }
    trials = []
    for updates in UPDATE_CANDIDATES:
        slower = max(dojo_step_seconds, reference_step_seconds) * updates
        parts = {
            "reference": reference_step_seconds * updates * reference_factor,
            "dojo_train": dojo_step_seconds * updates * dojo_train_factor,
            "evaluation": slower * evaluation_factor,
            "recovery": slower * recovery_factor,
            "fixed": fixed_seconds,
        }
        estimate = sum(parts.values()) * safety_factor
        trial = {
            "updates": updates,
            "estimated_seconds": estimate,
            "estimated_total_seconds": spent_seconds + estimate,
            "parts_seconds": parts,
        }
        trials.append(trial)
        if estimate <= ceiling:
            return {
                **trial,
                "ceiling_seconds": ceiling,
                "spent_seconds": spent_seconds,
                "coefficients": coefficients,
                "dojo_step_seconds": dojo_step_seconds,
                "reference_step_seconds": reference_step_seconds,
                "tried": trials,
                "estimate_only": True,
            }
    raise ValueError(
        f"最小20次更新预计仍超预算: {trials[-1]['estimated_seconds']:.3f}s > {ceiling:.3f}s；禁止开跑"
    )
