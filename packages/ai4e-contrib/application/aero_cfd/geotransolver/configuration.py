"""GeoTransolver 外流基础协议；不复用 Darcy/轨迹的配置树。"""

from copy import deepcopy


def resolve(config: dict, *, validate: bool = True) -> dict:
    """绑定默认训练与点流参数；拒绝当前案例未验证的网络分支。"""
    cfg = deepcopy(config)
    model = cfg.setdefault("model", {})
    defaults = {
        "n_layers": 4,
        "n_hidden": 128,
        "n_head": 4,
        "slice_num": 64,
        "mlp_ratio": 2,
        "dropout": 0.0,
        "include_local_features": False,
        "use_te": False,
        "plus": False,
    }
    params = model.setdefault("parameters", {})
    for key, value in defaults.items():
        params.setdefault(key, value)
    model.setdefault("initial_weights", None)
    model.setdefault("freeze", [])
    train = cfg.setdefault("train", {})
    defaults = {
        "max_epochs": 2,
        "batch_size": 1,
        "num_workers": 0,
        "device": "auto",
        "precision": "fp32",
        "optimizer": "muon_adamw",
        "learning_rate": 1e-3,
        "weight_decay": 1e-4,
        "accumulate": 1,
        "gradient_clip": None,
        "evaluation_enabled": False,
        "snapshot": True,
        "save_on_interrupt": True,
        "scheduler": "step",
        "step_size": 100,
        "gamma": 0.5,
    }
    for key, value in defaults.items():
        train.setdefault(key, value)
    sampling = cfg.setdefault("sampling", {})
    sampling.setdefault("seed", 42)
    sampling.setdefault("geometry", {"method": "random", "max_points": 8192})
    sampling.setdefault("domains", {})
    for domain in model["data_specs"]["domains"]:
        sampling["domains"].setdefault(domain, {"train": {"method": "random", "max_points": 8192}})
    infer = cfg.setdefault("infer", {})
    infer.setdefault("seed", 42)
    infer.setdefault("query_chunk_size", 8192)
    if validate:
        if (
            any(
                params.get(k)
                for k in (
                    "include_local_features",
                    "use_te",
                    "plus",
                    "activation_checkpointing",
                    "structured_shape",
                    "time_input",
                    "concrete_dropout",
                )
            )
            or params.get("attention_type", "GALE") != "GALE"
        ):
            raise ValueError("外流基础案例仅支持普通非结构 GALE、无局部编码")
        if list(cfg["trainprep"]["domains"]) != list(model["data_specs"]["domains"]):
            raise ValueError("域顺序与模型声明不一致")
        if train["optimizer"] != "muon_adamw" or train["scheduler"] != "step":
            raise ValueError("外流参考协议使用 muon_adamw 与 step；自定义请显式替换工厂")
        if train["accumulate"] != 1 or train["batch_size"] != 1:
            raise ValueError("外流基础协议要求单样本、无梯度累积")
        selections = [sampling["geometry"], *[v["train"] for v in sampling["domains"].values()]]
        for item in selections:
            if (
                item["method"] != "random"
                or type(item["max_points"]) is not int
                or item["max_points"] < 1
            ):
                raise ValueError("点流需要正整数随机采样预算")
        for domain, spec in model["data_specs"]["domains"].items():
            binding = cfg["trainprep"]["domains"][domain]
            if list(binding["features"]) != list(spec["feature_dim"]) or list(
                binding["targets"]
            ) != list(spec["output_dims"]):
                raise ValueError("特征或输出字段顺序不一致")
            if set(binding["features"].values()) & set(binding["targets"].values()):
                raise ValueError("监督真值不能作为输入特征")
        if infer["query_chunk_size"] < 1 or train["step_size"] < 1 or not 0 < train["gamma"] <= 1:
            raise ValueError("块大小或调度参数非法")
    return cfg
