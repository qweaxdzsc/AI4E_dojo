"""MeshGraphNet 配置校验和默认值。"""

from __future__ import annotations


def resolve(config: dict) -> dict:
    """返回副本，不改写调用方配置。"""
    result = dict(config)
    model = {"hidden_dim": 128, "processor_layers": 15, **result.get("model", {})}
    rawprep = {
        "splits": ["train", "valid", "test"],
        "max_trajectories": None,
        **result.get("rawprep", {}),
    }
    train = {
        "batch_size": 2,
        "noise_std": 0.02,
        "normalizer_warmup": 1000,
        "updates": 10_000_000,
        "lr": 1e-4,
        "lr_decay_steps": 5_000_000,
        "lr_decay_rate": 0.1,
        "lr_floor": 1e-6,
        "device": "auto",
        **result.get("train", {}),
    }
    infer = {"steps": "all", "device": train["device"], **result.get("infer", {})}
    if model["hidden_dim"] <= 0 or model["processor_layers"] <= 0:
        raise ValueError("MeshGraphNet 模型维度和处理层数必须为正")
    if train["updates"] <= 0 or train["normalizer_warmup"] < 0 or train["batch_size"] <= 0:
        raise ValueError("训练更新数和 batch_size 必须为正，warmup 不能为负")
    if train["lr"] <= 0 or train["lr_floor"] < 0 or train["lr_decay_steps"] <= 0:
        raise ValueError("学习率和衰减步数无效")
    if not 0 < train["lr_decay_rate"] <= 1:
        raise ValueError("lr_decay_rate 必须位于 (0, 1]")
    if infer["steps"] != "all" and int(infer["steps"]) < 0:
        raise ValueError("rollout 步数不能为负")
    if not rawprep["splits"] or any(
        item not in {"train", "valid", "test"} for item in rawprep["splits"]
    ):
        raise ValueError("rawprep.splits 只能选择 train、valid、test")
    if rawprep["max_trajectories"] is not None and int(rawprep["max_trajectories"]) <= 0:
        raise ValueError("max_trajectories 必须为正或 null")
    result.update(model=model, rawprep=rawprep, train=train, infer=infer)
    return result
