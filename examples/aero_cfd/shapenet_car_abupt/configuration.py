"""案例配置边界：五段输入归 recipe 所有，业务库继续消费既有参数结构。"""

from copy import deepcopy
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_contrib.application.aero_cfd import load, resolve_config
from ai4e_core.applications.aero_cfd.configuration import resolve_paths
from ai4e_core.base.config import load_config

RAW_KEYS = (
    "sources",
    "fields",
    "geometry",
    "save_fields",
    "filters",
    "statistics",
    "vtkhdf",
    "extraction",
    "format",
)
SHARED_KEYS = ("sampling", "normalization")
STAGES = ("rawprep", "trainprep", "train", "post")


def _plain(config) -> dict:
    return OmegaConf.to_container(OmegaConf.create(config), resolve=True)


def application_parameters(config) -> dict:
    """从用户配置提取独立业务参数副本；不改变字段顺序或填充计算结果。"""
    cfg = _plain(config)
    for key in (*RAW_KEYS, *SHARED_KEYS, "pre", "datapre"):
        if key in cfg:
            target = f"trainprep.{key}" if key in SHARED_KEYS else f"rawprep.{key}"
            if key in {"pre", "datapre"}:
                target = "rawprep"
            raise ValueError(f"旧案例配置键 {key} 已移除，请改用 {target}")
    for section in ("rawprep", "trainprep", "model", "train", "post"):
        if not isinstance(cfg.get(section), dict):
            raise TypeError(f"{section} 必须为配置映射")
    stages = cfg.get("pipeline", {}).get("stages", [])
    if any(name in {"pre", "datapre"} for name in stages):
        raise ValueError("旧案例阶段 pre/datapre 已移除，请改用 rawprep")
    if not stages or any(name not in STAGES for name in stages) or len(set(stages)) != len(stages):
        raise ValueError("未知、重复或空阶段选择")
    if list(stages) != sorted(stages, key=STAGES.index):
        raise ValueError("阶段必须按 rawprep → trainprep → train → post 顺序声明")
    raw = cfg.pop("rawprep")
    unknown = raw.keys() - set(RAW_KEYS)
    if unknown:
        raise ValueError(f"未知 rawprep 配置: {sorted(unknown)}")
    cfg.update(raw)
    if "sampling" in cfg["model"] and "sampling" in cfg["trainprep"]:
        raise ValueError("model.sampling 与旧 trainprep.sampling 不能同时存在")
    if "sampling" in cfg["model"]:
        cfg["trainprep"]["sampling"] = cfg["model"].pop("sampling")
    for key in SHARED_KEYS:
        value = cfg["trainprep"].pop(key, None)
        if value is None:
            value = {}
        if not isinstance(value, dict):
            target = "model.sampling" if key == "sampling" else "trainprep.normalization"
            raise TypeError(f"{target} 必须为配置映射")
        cfg[key] = value
    return deepcopy(cfg)


def _public(config: dict) -> dict:
    cfg = deepcopy(config)
    cfg["rawprep"] = {key: cfg.pop(key) for key in RAW_KEYS if key in cfg}
    prep = cfg.setdefault("trainprep", {})
    for key in SHARED_KEYS:
        if key in cfg:
            target = cfg.setdefault("model", {}) if key == "sampling" else prep
            target[key] = cfg.pop(key)
    return cfg


def load_configuration(path: str | Path, overrides=None):
    """合并覆盖和默认值，以配置文件位置解析路径，返回唯一五段生效配置。"""
    cfg = load_config(path, overrides)
    internal = application_parameters(cfg)
    selected = set(internal["pipeline"]["stages"])
    internal = resolve_config(internal, validate=bool(selected & {"train", "trainprep"}))
    internal = resolve_paths(internal, path)
    for field in getattr(load(internal).dataset, "SOURCE_PATH_FIELDS", ()):
        value = internal["dataset"].get(field)
        if value:
            source = Path(value).expanduser()
            internal["dataset"][field] = str(
                (source if source.is_absolute() else Path(path).resolve().parent / source).resolve()
            )
    return OmegaConf.create(_public(internal))
