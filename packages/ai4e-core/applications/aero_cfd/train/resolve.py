"""外流训练默认展开与联合校验。"""

from copy import deepcopy

from ai4e_core.abilities.constraint.compare import METHODS

MODEL_DEFAULTS = {
    "dim": 192,
    "geometry_depth": 6,
    "num_heads": 3,
    "blocks": "pscscscscsc",
    "radius": 9.0,
}

POST_DEFAULTS = {
    "random_stream": "global",
    "checkpoint": None,
    "split": "test",
    "evaluate": True,
    "save_predictions": True,
    "export_vtk": True,
    "query": True,
    "query_chunk_size": 16384,
    "overwrite": False,
}

TRAIN_DEFAULTS = {
    "evaluate_repeat": False,
    "max_epochs": 2,
    "batch_size": 1,
    "num_workers": 0,
    "device": "auto",
    "precision": "fp32",
    "optimizer": "lion",
    "learning_rate": 5.0e-5,
    "weight_decay": 0.05,
    "betas": [0.9, 0.99],
    "scheduler": "warmup_cosine",
    "warmup_ratio": 0.05,
    "min_lr": 1.0e-6,
    "accumulate": 1,
    "gradient_clip": 1.0,
    "ema_decay": 0.9999,
    "ema_save_every": 10,
    "test_repeat": 10,
    "snapshot": True,
    "save_on_interrupt": True,
    "evaluation_split": "test",
    "log_every": 1,
    "log_every_updates": None,
    "stability": False,
}


def expand_defaults(config: dict) -> dict:
    """补齐模型、优化、调度、检查点与损失默认值；``gpu`` 映到 ``cuda``，设备默认 ``auto``。"""
    result = deepcopy(config)
    model = result.setdefault("model", {})
    parameters = model.setdefault("parameters", {})
    for key, value in MODEL_DEFAULTS.items():
        parameters.setdefault(key, value)
    model.setdefault("initial_weights", None)
    model.setdefault("freeze", [])
    if model.get("data_specs"):
        parameters.setdefault(
            "num_domain_decoder_blocks", {d: 12 for d in model["data_specs"]["domains"]}
        )
    train = result.setdefault("train", {})
    for key, value in TRAIN_DEFAULTS.items():
        train.setdefault(key, deepcopy(value) if isinstance(value, list) else value)
    if train.get("device") == "gpu":
        train["device"] = "cuda"
    post = result.setdefault("post", {})
    for key, value in POST_DEFAULTS.items():
        post.setdefault(key, value)
    return result


def validate_joint(config: dict) -> None:
    """字段、输出、采样预算和批次限制任一不合则拒绝启动。"""
    train = config.get("train") or {}
    if int(train.get("batch_size", 1)) < 1:
        raise ValueError("批次必须为正")
    if int(train.get("num_workers", 0)) != 0:
        raise ValueError("本期 AB-UPT 仅支持零读取子进程")
    if int(train.get("accumulate", 1)) < 1:
        raise ValueError("梯度累积步必须为正")
    if int(train.get("test_repeat", 10)) < 1:
        raise ValueError("test_repeat 必须为正")
    interval = train.get("log_every_updates")
    if interval not in (None, "") and int(interval) < 1:
        raise ValueError("日志更新间隔必须为正")
    sampling = config.get("sampling") or {}
    geometry = int((sampling.get("geometry") or {}).get("max_points") or 0)
    supernodes = int((sampling.get("supernodes") or {}).get("num_points") or 0)
    if supernodes and geometry and supernodes > geometry:
        raise ValueError("超节点预算超过几何点数")
    heads = int((config.get("model") or {}).get("parameters", {}).get("num_heads") or 0)
    dim = int((config.get("model") or {}).get("parameters", {}).get("dim") or 0)
    if heads and dim and dim % heads != 0:
        raise ValueError("模型宽度必须能被头数整除")
    optimizer = str(train.get("optimizer", "lion")).lower()
    if optimizer not in {"adam", "adamw", "lion"}:
        raise ValueError(f"未知优化器种类: {train.get('optimizer')}")
    scheduler = str(train.get("scheduler", "warmup_cosine")).lower()
    if scheduler not in {"warmup_cosine", "cosine", "constant", "none"}:
        raise ValueError(f"未知调度种类: {train.get('scheduler')}")
    methods = [
        term.get("loss", "mse") for term in ((config.get("model") or {}).get("supervision") or [])
    ]
    if set(config.get("model", {})) & {"losses", "loss_weights"}:
        raise ValueError("旧损失配置不兼容，请使用 supervision")
    for method in methods:
        if method not in METHODS:
            raise ValueError("未知比较方法")


def apply_resolved(config: dict, *, validate: bool = True) -> dict:
    """展开默认值，可选做联合校验，返回最终生效配置。"""
    resolved = expand_defaults(config)
    if validate:
        validate_joint(resolved)
    return resolved
