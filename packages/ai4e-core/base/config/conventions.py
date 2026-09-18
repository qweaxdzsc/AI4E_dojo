"""研究脚本的公共配置约定；不解释模型、数据或领域参数。"""

from copy import deepcopy
from pathlib import Path

from .load import apply_overrides, load_config


def input_bindings(config: dict) -> dict[str, str]:
    """列举公共输入路径；附加名称不影响执行，未知类别作为普通资产。"""
    inputs = config.get("inputs", {})
    if not isinstance(inputs, dict):
        raise TypeError("inputs 必须为按阶段分组的映射")
    bindings = {}
    kinds = {
        "source": "dataset", "dataset": "dataset", "preparation": "preparation",
        "checkpoint": "checkpoint", "resume": "checkpoint", "initial_weights": "checkpoint",
    }
    for stage, values in inputs.items():
        if not isinstance(stage, str) or not stage.isidentifier() or not isinstance(values, dict):
            raise ValueError("inputs 的阶段必须为标识符，阶段输入必须为映射")
        for name, value in values.items():
            if not isinstance(name, str) or not name.isidentifier():
                raise ValueError("输入名称必须为标识符")
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise TypeError(f"inputs.{stage}.{name} 必须为路径或 null")
            bindings[f"inputs.{stage}.{name}"] = kinds.get(name, "other")
    return bindings


def normalize_recipe_config(config: dict, *, base: str | Path) -> dict:
    """解析公共路径；存在性由实际消费阶段校验，不要求模板已经绑定数据。"""
    value = deepcopy(config)
    base = Path(base).expanduser().resolve()
    for key in input_bindings(value):
        _, stage, name = key.split(".")
        path = value["inputs"][stage][name]
        if path is not None:
            candidate = Path(path).expanduser()
            value["inputs"][stage][name] = str(
                (base / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
            )
    for key in ("run_root", "data_root"):
        if key in value:
            if not isinstance(value[key], str) or not value[key].strip():
                raise ValueError(f"{key} 必须为输出路径")
            candidate = Path(value[key]).expanduser()
            value[key] = str((base / candidate).resolve())
    if "pipeline" in value:
        stages = value["pipeline"].get("stages")
        if (not isinstance(stages, list) or not stages
                or any(not isinstance(s, str) or not s.isidentifier() for s in stages)
                or len(stages) != len(set(stages))):
            raise ValueError("pipeline.stages 必须为非空、无重复的阶段名称列表")
    return value


def load_recipe_config(path: str | Path, overrides=None) -> dict:
    """读取公共配置；相对输入和输出均以配置文件位置解析。"""
    return normalize_recipe_config(load_config(path, overrides), base=Path(path).resolve().parent)


def require_current_keys(config: dict, retired: dict[str, str]) -> None:
    """领域入口显式指定废弃的公共键；不递归拒绝科学参数的同名字段。"""
    for old, new in retired.items():
        node = config
        for part in old.split("."):
            if not isinstance(node, dict) or part not in node:
                break
            node = node[part]
        else:
            raise ValueError(f"旧配置键 {old} 已移至 {new}；请先迁移配置")


def resolve_input(explicit, configured, *, name: str):
    """本次上游与外部输入冲突时拒绝；不搜索最近产物。"""
    if explicit is not None and configured is not None:
        if Path(explicit).resolve() != Path(configured).resolve():
            raise ValueError(f"输入冲突: {name}")
    result = explicit if explicit is not None else configured
    if result is None:
        raise ValueError(f"缺少输入: {name}")
    return result
