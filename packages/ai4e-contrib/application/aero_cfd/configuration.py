"""案例配置边界：五段输入归 recipe 所有，业务库继续消费既有参数结构。"""

from copy import deepcopy
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

from omegaconf import OmegaConf

from ai4e_contrib.application.aero_cfd import resolve_config
from ai4e_core.applications.aero_cfd import resolve_paths
from ai4e_core.base.config import load_config, validate_step_parameters

# 额外步骤参数约定不决定执行顺序；复制案例可在此声明自己的配置块。
STEP_PARAMETERS = {}


def load_components(cfg):
    """只加载所选数据集和模型，不选择整段工作流。"""
    from ai4e_contrib.application.aero_cfd import DEFAULTS

    selected = {**DEFAULTS, **dict(cfg.get("components", {}))}
    return SimpleNamespace(**{key: import_module(selected[key]) for key in ("dataset", "model")})


def validate_extensions(cfg, declarations=None):
    """在配置文件、命令行和程序入口统一校验案例扩展参数。"""
    validate_step_parameters(cfg, declarations=declarations or {})


def _raw_keys(declarations=None):
    return set(RAW_KEYS) | {
        path.split(".")[1] for path in (declarations or {}) if path.startswith("rawprep.")
    }


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
    "formats",
    "workers",
)
SHARED_KEYS = ("sampling", "normalization")
STAGES = ("rawprep", "trainprep", "train", "infer", "post")


def _plain(config) -> dict:
    return OmegaConf.to_container(OmegaConf.create(config), resolve=True)


def application_parameters(config, *, declarations=None, output_dirs=None) -> dict:
    """从用户配置提取独立业务参数副本；不改变字段顺序或填充计算结果。"""
    from .inputs import bind_inputs

    cfg = bind_inputs(_plain(config), output_dirs=output_dirs)
    validate_post_analysis(cfg)
    validate_extensions(cfg, declarations)
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
        raise ValueError("阶段必须按 rawprep → trainprep → train → infer → post 顺序声明")
    raw = cfg.pop("rawprep")
    unknown = raw.keys() - _raw_keys(declarations)
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
    if cfg.get("infer") is not None:
        from ai4e_core.applications.aero_cfd.infer import resolve_infer

        cfg = resolve_infer(cfg)
    return deepcopy(cfg)


def validate_post_analysis(config):
    """校验显式后处理参数；不向历史案例或训练契约注入显示默认值。"""
    post = config.get("post", {})
    every = post.get("snapshot_every", 0)
    if isinstance(every, bool) or not isinstance(every, int) or every < 0:
        raise ValueError("post.snapshot_every 必须为非负整数")
    if every and not post.get("snapshot_sample"):
        raise ValueError("启用训练快照必须显式指定 post.snapshot_sample")
    figures = post.get("figures", [])
    if not isinstance(figures, list) or set(figures) - {
        "surface",
        "slice",
        "clip",
        "vectors",
        "streamlines",
        "contour",
        "profile",
    }:
        raise ValueError("未知物理场图片类型")
    if "streamlines" in figures and not post.get("streamline_seeds"):
        raise ValueError("流线必须显式配置种子")
    if "profile" in figures and not all(key in post for key in ("profile_start", "profile_end")):
        raise ValueError("剖面必须显式配置端点")
    if "contour" in figures and not post.get("contour_values"):
        raise ValueError("等值面必须显式配置等值列表")
    if post.get("analysis_enabled") or every:
        paths = config.setdefault("paths", {}).setdefault("datasets", {})
        if not paths.get("post"):
            from pathlib import Path

            paths["post"] = str(Path(config["data_root"]) / "post")


def _public(config: dict, declarations=None) -> dict:
    cfg = deepcopy(config)
    cfg["rawprep"] = {key: cfg.pop(key) for key in list(cfg) if key in _raw_keys(declarations)}
    prep = cfg.setdefault("trainprep", {})
    for key in SHARED_KEYS:
        if key in cfg:
            target = cfg.setdefault("model", {}) if key == "sampling" else prep
            target[key] = cfg.pop(key)
    from .inputs import public_inputs

    return public_inputs(cfg)


def convert_configuration(config: dict) -> dict:
    """显式转换旧采样位置，返回新副本；冲突拒绝，不修改历史文件。"""
    from copy import deepcopy

    result = deepcopy(config)
    preparation = result.get("trainprep", {})
    if "sampling" in preparation:
        model = result.setdefault("model", {})
        if "sampling" in model:
            raise ValueError("model.sampling 与旧 trainprep.sampling 不能同时存在")
        model["sampling"] = preparation.pop("sampling")
    return result


def load_configuration(path: str | Path, overrides=None, *, declarations=None):
    """合并覆盖和默认值，以配置文件位置解析路径，返回唯一五段生效配置。"""
    from ai4e_core.base.config.conventions import load_recipe_config
    from .inputs import bind_inputs, public_inputs

    cfg = load_recipe_config(path, overrides)
    from ai4e_core.applications.aero_cfd.rawprep import resolve_rawprep

    cfg = OmegaConf.create(
        resolve_rawprep(
            bind_inputs(cfg), config_path=path
        )
    )
    internal = application_parameters(public_inputs(_plain(cfg)), declarations=declarations)
    selected = set(internal["pipeline"]["stages"])
    internal = resolve_config(internal, validate=bool(selected & {"train", "trainprep"}))
    internal = resolve_paths(internal, path)
    for field in getattr(load_components(internal).dataset, "SOURCE_PATH_FIELDS", ()):
        value = internal["dataset"].get(field)
        if value:
            source = Path(value).expanduser()
            internal["dataset"][field] = str(
                (source if source.is_absolute() else Path(path).resolve().parent / source).resolve()
            )
    return OmegaConf.create(_public(internal, declarations))
