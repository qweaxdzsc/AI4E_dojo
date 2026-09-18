"""外流既有配置的路径解析兼容接口，不识别 recipe 的展示分组。"""

from copy import deepcopy
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.base.config import load_config


def resolve_paths(config: dict, path: str | Path) -> dict:
    """按配置文件位置解析既有业务输入中的路径，并检查归一化声明。"""
    path = Path(path).resolve()
    cfg = deepcopy(config)

    def absolute(value):
        p = Path(value).expanduser()
        return str((p if p.is_absolute() else path.parent / p).resolve())

    for key in ("data_root", "run_root"):
        cfg[key] = absolute(cfg[key])
    cfg["dataset"]["root"] = absolute(cfg["dataset"]["root"])
    for key in ("manifest", "partition"):
        value = cfg["dataset"].get(key)
        if isinstance(value, str) and value not in {"official", "unsplit"}:
            cfg["dataset"][key] = absolute(value)

    def paths(node):
        return {k: paths(v) if isinstance(v, dict) else absolute(v) for k, v in node.items()}

    cfg["paths"] = paths(cfg["paths"])
    normalization = cfg.get("normalization", {})
    if normalization.get("statistics"):
        normalization["statistics"] = absolute(normalization["statistics"])
    if cfg.get("train", {}).get("manifest"):
        cfg["train"]["manifest"] = absolute(cfg["train"]["manifest"])
    for section, key in (
        ("train", "preparation"),
        ("train", "resume"),
        ("model", "initial_weights"),
        ("post", "checkpoint"),
        ("post", "results"),
        ("infer", "checkpoint"),
        ("infer", "preparation"),
        ("infer", "results"),
    ):
        value = cfg.get(section, {}).get(key)
        if value and str(value) not in {"last", "best", "latest"}:
            cfg[section][key] = absolute(value)
    for group in ("conditioning", "geometry_conditioning"):
        for declaration in cfg.get("trainprep", {}).get(group, {}).values():
            if declaration.get("path"):
                declaration["path"] = absolute(declaration["path"])
    fields = normalization.get("fields", {})
    if not isinstance(fields, dict):
        raise TypeError("normalization.fields 必须为字段到变换声明的映射")
    for field, declaration in fields.items():
        if not isinstance(declaration, dict) or not isinstance(declaration.get("method"), str):
            raise TypeError(f"非法归一化字段声明: {field}")
        if not isinstance(declaration.get("parameters", {}), dict):
            raise TypeError(f"归一化 parameters 必须为映射: {field}")
    run_root = Path(cfg["run_root"])
    code = path.parent
    raw = Path(cfg["dataset"]["root"])
    for target in cfg["paths"]["datasets"].values():
        if isinstance(target, str):
            dest = Path(target)
            if dest == code or dest.is_relative_to(code):
                raise ValueError("数据产物不能位于 recipe 代码目录内")
            if dest.is_relative_to(run_root) or run_root.is_relative_to(dest):
                raise ValueError("运行记录和数据产物目录必须独立")
    if run_root.is_relative_to(raw) or raw.is_relative_to(run_root):
        raise ValueError("运行记录不能覆盖原始数据")
    return cfg


def load_configuration(path, overrides=None):
    """保留旧调用者的配置加载行为；新 recipe 自行声明加载函数。"""
    return OmegaConf.create(resolve_paths(load_config(path, overrides), path))
