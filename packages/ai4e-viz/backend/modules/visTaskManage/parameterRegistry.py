"""Versioned VisualizationSpec parameter schemas.

The catalog describes *which* visualization functions are legal.  This module
describes *how* each legal function can be configured.  Schemas are standard
JSON Schema Draft 2020-12 documents so the API, generated forms, advanced JSON
editor and CI contracts all validate exactly the same payload.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_REVISION = "2026-08-25.2"
PALETTES = ["engineering", "viridis", "plasma", "turbo", "coolwarm", "grayscale"]
LEGEND_POSITIONS = ["top", "right", "bottom", "left", "hidden"]
COLOR_SCHEMA = {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}


def _field_choices(profile: dict[str, Any]) -> list[str]:
    choices: list[str] = []
    for key in ("columns", "field_arrays", "numeric_columns", "coordinate_arrays"):
        for value in profile.get(key, []) or []:
            if isinstance(value, str) and value not in choices:
                choices.append(value)
    for item in profile.get("field_variables", []) or []:
        name = item.get("name") if isinstance(item, dict) else None
        if name and name not in choices:
            choices.append(name)
    for key in ("main_array", "scalar_array", "time_column", "level_column"):
        value = profile.get(key)
        if isinstance(value, str) and value not in choices:
            choices.append(value)
    return choices


def _enum_or_string(choices: list[str], *, title: str, description: str = "") -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string", "title": title}
    if description:
        schema["description"] = description
    if choices:
        schema["enum"] = choices
    return schema


def _array_of_fields(choices: list[str], *, title: str, maximum: int = 12) -> dict[str, Any]:
    item: dict[str, Any] = {"type": "string"}
    if choices:
        item["enum"] = choices
    return {
        "type": "array",
        "title": title,
        "items": item,
        "uniqueItems": True,
        "maxItems": maximum,
    }


def _common_properties() -> dict[str, dict[str, Any]]:
    return {
        "title": {"type": "string", "title": "图表标题", "maxLength": 120, "default": ""},
        "subtitle": {"type": "string", "title": "副标题", "maxLength": 240, "default": ""},
        "palette": {"type": "string", "title": "配色方案", "enum": PALETTES, "default": "engineering"},
        "background_color": {**COLOR_SCHEMA, "title": "背景颜色", "default": "#FFFFFF"},
        "font_size": {"type": "integer", "title": "基础字号", "minimum": 10, "maximum": 24, "default": 12},
        "show_legend": {"type": "boolean", "title": "显示图例", "default": True},
        "legend_position": {"type": "string", "title": "图例位置", "enum": LEGEND_POSITIONS, "default": "top"},
        "show_tooltip": {"type": "boolean", "title": "启用提示框", "default": True},
        "animation": {"type": "boolean", "title": "启用动画", "default": False},
        "width": {"type": "integer", "title": "导出宽度", "minimum": 320, "maximum": 2400, "default": 960},
        "height": {"type": "integer", "title": "导出高度", "minimum": 240, "maximum": 1600, "default": 480},
    }


def _tabular_properties(fields: list[str], numeric: list[str]) -> dict[str, dict[str, Any]]:
    filter_field = _enum_or_string(fields, title="筛选字段")
    return {
        "sample_limit": {"type": "integer", "title": "最大采样数", "minimum": 50, "maximum": 5000, "default": 720},
        "missing_policy": {"type": "string", "title": "缺失值处理", "enum": ["gap", "drop", "zero", "forward-fill"], "default": "gap"},
        "sort_order": {"type": "string", "title": "排序方式", "enum": ["source", "ascending", "descending"], "default": "source"},
        "filters": {
            "type": "array",
            "title": "数据筛选",
            "maxItems": 12,
            "default": [],
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["field", "operator", "value"],
                "properties": {
                    "field": filter_field,
                    "operator": {"type": "string", "enum": ["eq", "neq", "gt", "gte", "lt", "lte", "contains"]},
                    "value": {"type": ["string", "number", "boolean"]},
                },
            },
        },
        "color_field": _enum_or_string(fields, title="颜色映射字段"),
        "numeric_field": _enum_or_string(numeric, title="数值字段"),
    }


def _scientific_properties(fields: list[str]) -> dict[str, dict[str, Any]]:
    return {
        "field": _enum_or_string(fields, title="活动数组/物理量"),
        "colormap": {"type": "string", "title": "科学色图", "enum": ["viridis", "plasma", "turbo", "coolwarm", "inferno", "grayscale"], "default": "viridis"},
        "reverse_colormap": {"type": "boolean", "title": "反转色图", "default": False},
        "range_min": {"type": ["number", "null"], "title": "显示下限", "default": None},
        "range_max": {"type": ["number", "null"], "title": "显示上限", "default": None},
        "opacity": {"type": "number", "title": "整体不透明度", "minimum": 0, "maximum": 1, "multipleOf": 0.01, "default": 1},
        "show_edges": {"type": "boolean", "title": "显示网格边线", "default": False},
        "slice_axis": {"type": "string", "title": "切片方向", "enum": ["x", "y", "z"], "default": "z"},
        "slice_index": {"type": "integer", "title": "切片索引", "minimum": 0, "maximum": 100000, "default": 0},
        "contours": {"type": "integer", "title": "等值线数量", "minimum": 0, "maximum": 40, "default": 0},
        "camera_projection": {"type": "string", "title": "相机投影", "enum": ["perspective", "orthographic"], "default": "perspective"},
        "camera_position": {"type": "array", "title": "相机位置", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1.6, 1.2, 1.6]},
        "camera_target": {"type": "array", "title": "相机目标", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0]},
    }


def _groups_for(kind: str, renderer: str, properties: dict[str, Any]) -> list[dict[str, Any]]:
    groups = [
        {"id": "mapping", "label": "数据映射", "fields": [key for key in ("x", "y", "field", "scalar_field", "vector_components", "magnitude_field", "fields", "columns", "color_field", "size_field", "id", "time", "position") if key in properties]},
        {"id": "transform", "label": "数据处理", "fields": [key for key in ("filters", "aggregation", "sort_order", "sample_limit", "missing_policy", "bins", "top_n") if key in properties]},
        {"id": "scale", "label": "坐标与尺度", "fields": [key for key in ("x_scale", "y_scale", "range_min", "range_max", "slice_axis", "slice_index", "contours", "vector_density", "glyph_scale") if key in properties]},
        {"id": "style", "label": "视觉样式", "fields": [key for key in ("title", "subtitle", "display_style", "representation", "vector_style", "palette", "colormap", "reverse_colormap", "background_color", "value_color", "font_size", "line_width", "line_style", "show_symbols", "smooth", "opacity", "show_edges", "point_size", "trail_length", "show_delta", "show_target") if key in properties]},
        {"id": "interaction", "label": "交互", "fields": [key for key in ("show_legend", "legend_position", "show_tooltip", "animation", "zoom", "brush", "playback_fps", "loop", "controls", "autoplay") if key in properties]},
        {"id": "camera", "label": "相机与三维", "fields": [key for key in ("camera_projection", "camera_position", "camera_target", "up_axis", "auto_fit", "material_color") if key in properties]},
        {"id": "export", "label": "输出", "fields": [key for key in ("width", "height", "alt_text", "caption", "poster", "fit", "start_time", "end_time") if key in properties]},
    ]
    return [group for group in groups if group["fields"]]


def parameter_contract(function: dict[str, Any], profile: dict[str, Any] | None = None, encoding: dict[str, Any] | None = None) -> dict[str, Any]:
    """根据方法、数据画像和字段映射生成JSON Schema与默认参数。"""

    profile = profile or {}
    encoding = encoding or {}
    kind = function["compatible_kinds"][0]
    function_id = function["id"]
    renderer = function["renderer"]
    fields = _field_choices(profile)
    numeric = [value for value in profile.get("numeric_columns", []) or [] if isinstance(value, str)] or fields
    properties = _common_properties()

    if kind == "scalar":
        properties.update({
            "unit": {"type": "string", "title": "单位", "maxLength": 24, "default": ""},
            "precision": {"type": "integer", "title": "小数位数", "minimum": 0, "maximum": 8, "default": 2},
            "target": {"type": ["number", "null"], "title": "目标值", "default": None},
        })
        if function_id == "core.scalar-number@2.0.0":
            properties.update({
                "display_style": {"type": "string", "title": "数字样式", "enum": ["plain", "compact", "status"], "default": "plain"},
                "value_color": {**COLOR_SCHEMA, "title": "数值颜色", "default": "#1677FF"},
                "show_delta": {"type": "boolean", "title": "显示与目标的差值", "default": True},
                "show_target": {"type": "boolean", "title": "显示目标值", "default": True},
            })
        else:
            properties.update({
                "orientation": {"type": "string", "title": "柱形方向", "enum": ["vertical", "horizontal"], "default": "vertical"},
                "bar_width": {"type": "integer", "title": "柱宽", "minimum": 12, "maximum": 120, "default": 48},
                "baseline": {"type": "number", "title": "基线", "default": 0},
                "show_target": {"type": "boolean", "title": "显示目标线", "default": True},
                "show_value_label": {"type": "boolean", "title": "显示数值标签", "default": True},
            })
    if kind in {"table", "series", "distribution", "matrix", "optimization", "ensemble", "uncertainty"}:
        properties.update(_tabular_properties(fields, numeric))
    if kind == "table":
        properties.update({
            "columns": _array_of_fields(fields, title="显示列", maximum=40),
            "page_size": {"type": "integer", "title": "每页行数", "enum": [10, 20, 50, 100, 250], "default": 50},
            "density": {"type": "string", "title": "表格密度", "enum": ["compact", "normal", "comfortable"], "default": "normal"},
            "show_search": {"type": "boolean", "title": "显示搜索", "default": True},
        })
    if kind in {"series", "ensemble", "uncertainty"}:
        properties.update({
            "x": _enum_or_string(fields, title="横轴字段"),
            "y": _array_of_fields(numeric, title="纵轴序列", maximum=12),
            "x_scale": {"type": "string", "title": "横轴尺度", "enum": ["category", "linear", "time", "log"], "default": "category"},
            "y_scale": {"type": "string", "title": "纵轴尺度", "enum": ["linear", "log", "symlog"], "default": "linear"},
            "line_width": {"type": "number", "title": "线宽", "minimum": 0.5, "maximum": 8, "multipleOf": 0.5, "default": 2},
            "line_style": {"type": "string", "title": "线型", "enum": ["solid", "dashed", "dotted"], "default": "solid"},
            "show_symbols": {"type": "boolean", "title": "显示数据点", "default": False},
            "smooth": {"type": "boolean", "title": "平滑曲线", "default": False},
            "zoom": {"type": "boolean", "title": "启用缩放", "default": True},
            "brush": {"type": "boolean", "title": "启用框选", "default": False},
        })
    if kind == "distribution":
        properties.update({
            "field": _enum_or_string(fields, title="统计字段"),
            "bins": {"type": "integer", "title": "分箱数量", "minimum": 5, "maximum": 100, "default": 24},
            "top_n": {"type": "integer", "title": "类别显示数量", "minimum": 5, "maximum": 100, "default": 20},
            "orientation": {"type": "string", "title": "方向", "enum": ["vertical", "horizontal"], "default": "vertical"},
        })
    if kind in {"matrix", "tensor", "raster", "volume", "field"}:
        properties.update(_scientific_properties(fields))
        properties.update({
            "fields": _array_of_fields(numeric, title="参与计算的字段", maximum=20),
            "array": _enum_or_string(fields, title="数组"),
            "aspect": {"type": "string", "title": "单元格比例", "enum": ["auto", "equal", "wide"], "default": "auto"},
        })
    if function_id in {
        "scientific.raster-scalar@2.1.0", "scientific.volume-scalar@2.1.0", "scientific.field-scalar@2.1.0"
    }:
        representation = {
            "scientific.raster-scalar@2.1.0": "surface",
            "scientific.volume-scalar@2.1.0": "volume",
            "scientific.field-scalar@2.1.0": "surface",
        }[function_id]
        scalar_field = _enum_or_string(fields, title="标量数组")
        scalar_field["default"] = fields[0] if fields else "scalar"
        properties.update({
            "scalar_field": scalar_field,
            "representation": {"type": "string", "title": "显示方式", "enum": ["surface", "slice", "contour", "volume", "isosurface"], "default": representation},
            "show_colorbar": {"type": "boolean", "title": "显示色标", "default": True},
        })
    if function_id in {
        "scientific.raster-vector@2.1.0", "scientific.volume-vector@2.1.0", "scientific.field-vector@2.1.0"
    }:
        properties.pop("field", None)
        vector_components = _array_of_fields(fields, title="矢量分量", maximum=3)
        preferred_components = [item for item in fields if item.lower() in {"u", "v", "w", "ux", "uy", "uz", "velocity_x", "velocity_y", "velocity_z"}][:3]
        vector_components["default"] = preferred_components or (fields[:3] if fields else ["u", "v"])
        properties.update({
            "vector_components": vector_components,
            "magnitude_field": _enum_or_string(fields, title="幅值数组（可选）"),
            "vector_style": {"type": "string", "title": "矢量显示方式", "enum": ["arrows", "streamlines", "tubes"], "default": "streamlines"},
            "vector_density": {"type": "integer", "title": "采样密度", "minimum": 4, "maximum": 80, "default": 24},
            "glyph_scale": {"type": "number", "title": "箭头缩放", "minimum": 0.05, "maximum": 10, "multipleOf": 0.05, "default": 1},
            "color_by_magnitude": {"type": "boolean", "title": "按速度幅值着色", "default": True},
            "seed_count": {"type": "integer", "title": "流线种子数", "minimum": 4, "maximum": 500, "default": 48},
        })
    if kind in {"point_set", "trajectory"}:
        properties.update(_scientific_properties(fields))
        properties.update({
            "id": _enum_or_string(fields, title="实体/轨迹 ID"),
            "time": _enum_or_string(fields, title="时间字段"),
            "position": _array_of_fields(fields, title="空间坐标", maximum=3),
            "point_size": {"type": "number", "title": "点大小", "minimum": 1, "maximum": 30, "default": 4},
            "trail_length": {"type": "integer", "title": "尾迹长度", "minimum": 1, "maximum": 500, "default": 90},
            "max_tracks": {"type": "integer", "title": "最大轨迹数", "minimum": 1, "maximum": 500, "default": 64},
            "playback_fps": {"type": "integer", "title": "播放帧率", "minimum": 1, "maximum": 60, "default": 12},
        })
    if kind == "graph":
        properties.update({
            "layout": {"type": "string", "title": "布局", "enum": ["force", "dagre", "circular", "manual"], "default": "force"},
            "node_size": {"type": "integer", "title": "节点大小", "minimum": 10, "maximum": 80, "default": 28},
            "edge_width": {"type": "number", "title": "连线宽度", "minimum": 0.5, "maximum": 8, "default": 1.5},
            "show_labels": {"type": "boolean", "title": "显示标签", "default": True},
            "zoom": {"type": "boolean", "title": "启用缩放", "default": True},
        })
    if kind == "mesh":
        properties.update({
            "material_color": {**COLOR_SCHEMA, "title": "默认材质颜色", "default": "#D6DEE8"},
            "show_edges": {"type": "boolean", "title": "显示边线", "default": False},
            "background_color": {**COLOR_SCHEMA, "title": "背景颜色", "default": "#161A20"},
            "camera_projection": {"type": "string", "title": "相机投影", "enum": ["perspective", "orthographic"], "default": "perspective"},
            "camera_position": {"type": "array", "title": "相机位置", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [1.6, 1.2, 1.6]},
            "camera_target": {"type": "array", "title": "相机目标", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0, 0, 0]},
            "up_axis": {"type": "string", "title": "向上轴", "enum": ["x", "y", "z"], "default": "y"},
            "auto_fit": {"type": "boolean", "title": "加载后自动适配", "default": True},
        })
    if kind == "text_document":
        properties.update({
            "theme": {"type": "string", "title": "阅读主题", "enum": ["report", "technical", "compact"], "default": "report"},
            "show_toc": {"type": "boolean", "title": "显示目录", "default": True},
            "max_width": {"type": "integer", "title": "正文最大宽度", "minimum": 560, "maximum": 1200, "default": 820},
        })
    if kind == "image":
        properties.update({
            "fit": {"type": "string", "title": "适配方式", "enum": ["contain", "cover", "natural"], "default": "contain"},
            "caption": {"type": "string", "title": "图片说明", "maxLength": 500, "default": ""},
            "alt_text": {"type": "string", "title": "替代文本", "maxLength": 500, "default": ""},
        })
    if kind == "video":
        properties.update({
            "controls": {"type": "boolean", "title": "显示播放控件", "default": True},
            "autoplay": {"type": "boolean", "title": "自动播放", "default": False},
            "loop": {"type": "boolean", "title": "循环播放", "default": False},
            "muted": {"type": "boolean", "title": "静音", "default": True},
            "start_time": {"type": "number", "title": "起始秒数", "minimum": 0, "default": 0},
            "end_time": {"type": ["number", "null"], "title": "结束秒数", "minimum": 0, "default": None},
            "caption": {"type": "string", "title": "视频说明", "maxLength": 500, "default": ""},
            "alt_text": {"type": "string", "title": "替代文本", "maxLength": 500, "default": ""},
        })

    defaults: dict[str, Any] = {}
    for key, prop in properties.items():
        if "default" in prop:
            defaults[key] = deepcopy(prop["default"])
    for key, value in encoding.items():
        if key in properties and value is not None:
            defaults[key] = deepcopy(value)
            properties[key]["default"] = deepcopy(value)

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:qoder-viz:{function['id']}:{SCHEMA_REVISION}",
        "title": f"{function['id']} 参数",
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
    }
    return {
        "schema_revision": SCHEMA_REVISION,
        "parameter_schema": schema,
        "ui_schema": {"groups": _groups_for(kind, renderer, properties)},
        "default_parameters": defaults,
    }


def enrich_recommendations(payload: dict[str, Any], profile: dict[str, Any], functions: list[dict[str, Any]]) -> dict[str, Any]:
    """为推荐候选附加当前画像对应的参数契约。"""

    function_by_id = {item["id"]: item for item in functions}
    enriched = deepcopy(payload)
    for key in ("candidates", "detected_candidates", "recovery_candidates"):
        rows = []
        for candidate in enriched.get(key, []) or []:
            function = function_by_id.get(candidate["function_id"])
            contract = parameter_contract(function, profile, candidate.get("encoding")) if function else {}
            rows.append({**candidate, **contract})
        if key in enriched:
            enriched[key] = rows
    return enriched


def normalize_and_validate(function: dict[str, Any], profile: dict[str, Any], encoding: dict[str, Any], parameters: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """合并默认参数并返回符合统一格式的Schema校验错误。"""

    contract = parameter_contract(function, profile, encoding)
    normalized = deepcopy(contract["default_parameters"])
    if isinstance(parameters, dict):
        normalized.update(deepcopy(parameters))
    validator = Draft202012Validator(contract["parameter_schema"])
    errors = []
    for error in sorted(validator.iter_errors(normalized), key=lambda item: list(item.absolute_path)):
        path = "/" + "/".join(str(value) for value in error.absolute_path)
        errors.append({
            "path": path or "/",
            "message": error.message,
            "validator": error.validator,
            "legal": error.validator_value if error.validator in {"enum", "minimum", "maximum"} else None,
        })
    return normalized, errors


def enrich_function(function: dict[str, Any]) -> dict[str, Any]:
    """为目录方法附加无数据画像时的基础参数契约。"""

    return {**function, **parameter_contract(function)}
