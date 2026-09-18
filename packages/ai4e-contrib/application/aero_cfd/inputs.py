"""外流应用把公共引用绑定到已有领域参数；不把内部键写回用户配置。"""

from copy import deepcopy
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.config.conventions import input_bindings, require_current_keys

REFERENCES = {
    "dataset.root": "inputs.rawprep.source",
    "dataset.manifest": "inputs.rawprep.manifest",
    "dataset.partition": "inputs.trainprep.partition",
    "dataset.train_h5": "inputs.rawprep.train_h5",
    "dataset.test_h5": "inputs.rawprep.test_h5",
    "dataset.connectivity_h5": "inputs.rawprep.connectivity_h5",
    "train.manifest": "inputs.trainprep.dataset",
    "train.preparation": "inputs.train.preparation",
    "train.resume": "inputs.train.resume",
    "model.initial_weights": "inputs.train.initial_weights",
    "trainprep.normalization.statistics": "inputs.trainprep.statistics",
    "infer.preparation": "inputs.infer.preparation",
    "infer.checkpoint": "inputs.infer.checkpoint",
    "post.results": "inputs.post.results",
}


def bind_inputs(config: dict, *, output_dirs=None) -> dict:
    """领域内部参数副本；公共输入之外不接受旧路径别名。"""
    require_current_keys(config, {**REFERENCES, "paths": "data_root", "post.checkpoint": "inputs.infer.checkpoint", "infer.results": "inputs.post.results"})
    input_bindings(config)
    cfg = OmegaConf.create(deepcopy(config))
    for old, public in REFERENCES.items():
        value = OmegaConf.select(cfg, public)
        # 未选择输入不应改变冻结的科学声明（例如额外插入 statistics: null）。
        if value is not None or old == "model.initial_weights":
            OmegaConf.update(cfg, old, value, force_add=True)
    partitions = cfg.get("dataset", {}).pop("partitions", None)
    if partitions is not None:
        if OmegaConf.select(cfg, "inputs.trainprep.partition") is not None:
            raise ValueError("dataset.partitions 与 inputs.trainprep.partition 不能同时指定")
        cfg.dataset.partition = partitions
    root = Path(config["data_root"])
    directories = output_dirs or {s: root / s for s in ("rawprep", "trainprep", "infer", "post")}
    physical = Path(directories["rawprep"])
    normalized = Path(directories["trainprep"]) / "normalize"
    cfg.paths = {"datasets": {
        "root": str(physical), **{s: str(physical / s) for s in ("train", "test", "eval", "validation")},
        "normalize": {"root": str(normalized), **{s: str(normalized / s) for s in ("train", "test", "eval", "validation")}},
        "predictions": str(Path(directories["infer"]) / "predictions"),
        "post": str(Path(directories["post"]) / "analysis"),
    }}
    return OmegaConf.to_container(cfg, resolve=True)


def public_inputs(config: dict) -> dict:
    """把领域默认解析得到的输入归回唯一公共位置，不保留内部输出树。"""
    cfg = OmegaConf.create(deepcopy(config))
    for old, public in REFERENCES.items():
        node = cfg
        parts = old.split(".")
        for part in parts[:-1]:
            node = node.get(part, {})
        if parts[-1] in node:
            value = node.pop(parts[-1])
            if old == "dataset.partition" and (
                isinstance(value, (dict,))
                or OmegaConf.is_dict(value)
                or value in {"official", "unsplit"}
            ):
                cfg.dataset.partitions = value
                OmegaConf.update(cfg, public, None, force_add=True)
                continue
            OmegaConf.update(cfg, public, value, force_add=True)
    cfg.pop("paths", None)
    cfg.get("post", {}).pop("checkpoint", None)
    cfg.get("infer", {}).pop("results", None)
    return OmegaConf.to_container(cfg, resolve=True)
