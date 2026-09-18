"""平台配置合成：明确编辑覆盖原值，算法校验和默认值仍归既有入口。"""

from copy import deepcopy
from itertools import pairwise

# 仅描述平台可编辑区域；不复制算法默认值或数值规则。
_FIELDS = {
    "rawprep": {
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
    },
    "trainprep": {
        "domains",
        "normalization",
        "split",
        "use_physics_features",
        "sampling",
        "sample",
    },
    "model": {"parameters", "data_specs", "supervision", "sampling"},
    "train": {
        "optimizer",
        "learning_rate",
        "weight_decay",
        "precision",
        "accumulate",
        "gradient_clip",
        "scheduler",
        "scheduler_unit",
        "warmup_ratio",
        "min_lr",
        "min_lr_ratio",
        "max_epochs",
        "batch_size",
        "device",
        "num_workers",
        "ema_decay",
        "ema_save_every",
        "log_every",
        "log_every_updates",
        "snapshot",
        "test_repeat",
        "evaluate_repeat",
        "evaluation_split",
        "training_split",
        "evaluation_enabled",
        "evaluation_metrics",
        "evaluation_fields",
        "evaluation_aggregate",
        "loss_x_axis",
        "validation_unit",
        "export_predictions",
        "export_vtk",
        "export_split",
        "validation_interval",
        "save_on_interrupt",
        "parameter_group_policy",
    },
}


def _merge(original, patch):
    result = deepcopy(original)
    for key, value in patch.items():
        result[key] = (
            _merge(result[key], value)
            if isinstance(value, dict) and isinstance(result.get(key), dict)
            else deepcopy(value)
        )
    return result


def _get(value, path):
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise ValueError("configuration_edit_value_missing: " + "/".join(path))
        value = value[key]
    return value


def _write(value, path, incoming=None, *, remove=False):
    for key in path[:-1]:
        if key not in value:
            if remove:
                return
            value[key] = {}
        if not isinstance(value[key], dict):
            raise ValueError("configuration_edit_parent_not_mapping")  # noqa: TRY004 - HTTP配置业务错误
        value = value[key]
    if remove:
        value.pop(path[-1], None)
    else:
        value[path[-1]] = deepcopy(incoming)


def compose_configuration(
    original: dict,
    stage: str,
    values: dict,
    *,
    edited_paths: list[list[str]] | None = None,
    removed_paths: list[list[str]] | None = None,
    rawprep_profile: dict | None = None,
) -> dict:
    """合成完整任务配置；路径相对阶段，空列表表示没有编辑，None兼容旧请求。

    不修改输入，不解析插值；越界、重叠路径和缺失赋值抛 ValueError。
    页面管理的映射整体赋值时替换；普通叶子编辑保留相邻研究参数。
    """
    result = deepcopy(original)
    old = deepcopy(original.get(stage, {}))
    removed = removed_paths or []
    requested = (edited_paths if edited_paths is not None else [[key] for key in values]) + removed
    if (
        stage == "model"
        and any(path and path[0] == "sampling" for path in requested)
        and "sampling" not in old
        and "sampling" in original.get("trainprep", {})
    ):
        old["sampling"] = deepcopy(original["trainprep"]["sampling"])

    if edited_paths is None:
        if removed:
            raise ValueError("configuration_edit_paths_required")
        # 旧阶段接口仍为补丁；原始处理完整段由该接口调用方显式提供空底稿。
        current = _merge(old, values)
        changed = [[key] for key in values]
    else:
        if stage not in _FIELDS:
            raise ValueError("unsupported_configuration_edit_stage")
        changed = edited_paths
        paths = changed + removed
        for path in paths:
            if not path or any(not isinstance(key, str) or not key for key in path):
                raise ValueError("invalid_configuration_edit_path")
            if path[0] not in _FIELDS[stage]:
                raise ValueError("unsupported_configuration_edit_path: " + "/".join(path))
        ordered = sorted(tuple(path) for path in paths)
        for left, right in pairwise(ordered):
            if right[: len(left)] == left:
                raise ValueError("overlapping_configuration_edit_paths")
        current = deepcopy(old)
        for path in changed:
            _write(current, path, _get(values, path))
        for path in removed:
            _write(current, path, remove=True)
    result[stage] = current
    touched = {path[0] for path in changed + removed}
    if stage == "rawprep" and "formats" in touched and "formats" in current:
        current.pop("format", None)
    if stage == "rawprep":
        _rawprep_selection(current, old, touched, rawprep_profile or {})
    if stage == "model" and "sampling" in touched:
        result.setdefault("trainprep", {}).pop("sampling", None)
    if stage == "trainprep" and "normalization" in touched:
        old_fields = old.get("normalization", {}).get("fields", {})
        fields = current.get("normalization", {}).get("fields", {})
        for name, field in fields.items():
            before = old_fields.get(name, {})
            if field.get("method") != before.get("method"):
                # 切换选择仅清理已知旧方法参数，未知研究扩展保持。
                for key in ("parameters", "statistics_keys", "target"):
                    prefix = ["normalization", "fields", name, key]
                    explicit = edited_paths is not None and any(
                        path[: len(prefix)] == prefix for path in changed
                    )
                    supplied = values.get("normalization", {}).get("fields", {}).get(name, {})
                    explicit = explicit or (key in supplied and supplied[key] != before.get(key))
                    if not explicit:
                        field.pop(key, None)
                field.pop("unified_space", None)
    return result


def _rawprep_selection(current, old, touched, profile):
    """按平台既有能力描述联动选项，不计算几何或复制算法默认值。"""
    if "geometry" in touched and isinstance(current.get("geometry"), dict):
        geometry = current["geometry"]
        added = set(geometry) - set(old.get("geometry", {}))
        for option in profile.get("geometry", []):
            if option["id"] in added:
                for conflict in option.get("conflicts", []):
                    geometry.pop(conflict, None)
        disabled = set()
        for output in profile.get("outputs", []):
            if (set(output.get("requires", [])) - set(geometry)) or (
                output.get("requires_any") and not set(output["requires_any"]) & set(geometry)
            ):
                disabled.add(output["name"])
        if "save_fields" in current:
            current["save_fields"] = [
                name for name in current["save_fields"] if name not in disabled
            ]
        for item in profile.get("filters", []):
            if set(item.get("requires", [])) - set(geometry):
                domain = item["domain"]
                filters = current.get("filters", {}).get(domain)
                if isinstance(filters, list):
                    current["filters"][domain] = [value for value in filters if value != item["id"]]
    if {"save_fields", "geometry"} & touched and "save_fields" in current:
        selected = set(current["save_fields"])
        for key in ("fields", "position_fields"):
            statistics = current.get("statistics", {})
            if key in statistics:
                statistics[key] = [name for name in statistics[key] if name in selected]
        extraction = current.get("extraction")
        if isinstance(extraction, dict) and extraction.get("layout") == "fields":
            for entry in extraction.get("entries", []):
                entry["outputs"] = [
                    output for output in entry.get("outputs", []) if output["name"] in selected
                ]
