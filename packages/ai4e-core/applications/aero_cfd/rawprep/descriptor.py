"""数据集声明的公共解析：默认配置、字段选择与依赖，不识别具体数据集。"""

from copy import deepcopy
from importlib import import_module
from pathlib import Path

import yaml


def merge_defaults(defaults: dict, values: dict) -> dict:
    """递归补缺；显式空映射、空列表及 False 保持用户意图。"""
    result = deepcopy(defaults)
    for key, value in values.items():
        result[key] = (
            merge_defaults(result[key], value)
            if isinstance(value, dict) and value and isinstance(result.get(key), dict)
            else deepcopy(value)
        )
    return result


def load_description(path, config=None) -> dict:
    """读取组件提供的 manifest；旧自定义 manifest 可继承已安装的处理描述。

    来源文件名写入 source_files，并补到对应域的输出，供页面回填提取对话框。
    """
    path = Path(path)
    declared = yaml.safe_load(path.read_text())
    custom = (config or {}).get("dataset", {}).get("manifest")
    if custom:
        supplied = yaml.safe_load(Path(custom).read_text())
        declared = merge_defaults(declared, supplied)
    profile = deepcopy(declared["rawprep"])
    profile["source_files"] = {
        name: spec["filename"]
        for name, spec in declared.get("sources", {}).items()
        if isinstance(spec, dict) and spec.get("filename")
    }
    for item in profile.get("outputs", []):
        filename = profile["source_files"].get(item.get("domain"))
        if filename and not item.get("filename"):
            item["filename"] = filename
    profile["source_fields"] = deepcopy(declared.get("fields", {}))
    profile["output_routes"] = deepcopy(
        declared.get(
            "outputs",
            {
                item["name"]: {"domain": item["domain"], "field": "fields." + item["name"]}
                for item in profile["outputs"]
            },
        )
    )
    profile.update(schema_version=1, dataset_id=declared["name"])
    return profile


def dataset_component(config):
    """解析已声明的组件；仅历史配置识别留在算法边界。"""
    name = config.get("components", {}).get("dataset")
    if not name:
        suffix = "nasa_crm" if (config.get("dataset") or {}).get("train_h5") else "shapenet_car"
        name = "ai4e_contrib.application.datasets." + suffix
    return import_module(name)


def resolve_rawprep(config, *, validate=False, config_path=None):
    """返回统一公开配置；无描述的用户组件保持原样。"""
    cfg = deepcopy(config)
    manifest = cfg.get("dataset", {}).get("manifest")
    if manifest and config_path and not Path(manifest).is_absolute():
        cfg["dataset"]["manifest"] = str((Path(config_path).resolve().parent / manifest).resolve())
    component = dataset_component(cfg)
    if not hasattr(component, "describe_rawprep"):
        return cfg
    profile = component.describe_rawprep(cfg)
    raw = cfg.get("rawprep", {})
    cfg["rawprep"] = _promote_legacy_volume_normals(merge_defaults(profile["defaults"], raw))
    resolved_workers(cfg["rawprep"])
    if validate:
        validate_rawprep(cfg["rawprep"], profile)
    return cfg


def _promote_legacy_volume_normals(raw: dict) -> dict:
    """历史任务把体积法向挂在最近顶点下；提升为独立能力后再校验。"""
    names = set(raw.get("save_fields") or [])
    extraction = raw.get("extraction")
    if isinstance(extraction, dict):
        for entry in extraction.get("entries") or []:
            for item in entry.get("outputs") or []:
                names.update(filter(None, (item.get("name"), item.get("source_field"))))
    if "volume_normals" not in names:
        return raw
    geometry = raw.get("geometry")
    if isinstance(geometry, list):
        if "nearest_vertex" in geometry and "volume_normals" not in geometry:
            return {**raw, "geometry": [*geometry, "volume_normals"]}
    elif isinstance(geometry, dict) and "nearest_vertex" in geometry and "volume_normals" not in geometry:
        inherited = geometry.get("nearest_vertex")
        return {
            **raw,
            "geometry": {
                **geometry,
                "volume_normals": dict(inherited) if isinstance(inherited, dict) else {},
            },
        }
    return raw


def selected_outputs(raw, profile):
    """将逐场选择映射为来源和文件名；旧容器独立保留。"""
    catalog = {item["name"]: item for item in profile["outputs"]}
    if raw.get("extraction", {}).get("layout") == "fields":
        return [
            {
                "name": out["name"],
                "source_field": out["members"][0]["source_field"],
                "components": out["members"][0].get("components", 1),
            }
            for entry in raw["extraction"]["entries"]
            for out in entry["outputs"]
        ]
    return [
        {**catalog.get(name, {}), "name": name, "source_field": name}
        for name in raw.get("save_fields", [])
    ]


def resolved_formats(raw: dict) -> list[str]:
    """解析输出格式；新旧键同时出现且不一致时拒绝。"""
    has_list = "formats" in raw and raw.get("formats") is not None
    has_one = "format" in raw
    if has_list:
        formats = list(raw["formats"])
        if has_one and [raw.get("format")] != formats:
            raise ValueError("rawprep.format: 不能同时声明不一致的 format 与 formats")
    else:
        formats = [raw.get("format", "pt")]
    if (
        not formats
        or len(formats) != len(set(formats))
        or not all(item in {"pt", "zarr"} for item in formats)
    ):
        raise ValueError("rawprep.formats: 至少选择一种支持的输出格式")
    return formats


def primary_format(formats: list[str]) -> str:
    """读盘优先 PT，否则取声明的第一种格式。"""
    return "pt" if "pt" in formats else formats[0]


def resolved_workers(raw: dict) -> int:
    """解析并行样本线程数；缺省 1，超出 1–64 拒绝。"""
    value = 1 if raw.get("workers") is None else raw.get("workers")
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 64:
        raise ValueError("rawprep.workers: 需要 1 到 64 的整数")
    return value


def validate_rawprep(raw: dict, profile: dict) -> None:
    """校验可表达的处理配置与功能依赖；未知扩展由复制 recipe 自行声明。"""
    from .extraction import compile_extraction

    def require(ok, path, message):
        if not ok:
            raise ValueError(f"rawprep.{path}: {message}")

    formats = resolved_formats(raw)
    resolved_workers(raw)
    require(set(formats) <= set(profile["formats"]), "formats", "不支持的输出格式")
    require(isinstance(raw.get("vtkhdf", False), bool), "vtkhdf", "需要布尔值")
    require(not raw.get("vtkhdf") or profile["vtkhdf"], "vtkhdf", "数据集未接入网格附加输出")
    for key in ("fields", "filters", "statistics"):
        require(isinstance(raw.get(key, {}), dict), key, "需要映射")
    for key in ("sources", "save_fields"):
        require(
            isinstance(raw.get(key, []), list)
            and all(isinstance(v, str) for v in raw.get(key, [])),
            key,
            "需要字符串列表",
        )
    for key in ("fields", "position_fields"):
        require(
            isinstance(raw.get("statistics", {}).get(key, []), list)
            and all(isinstance(v, str) for v in raw.get("statistics", {}).get(key, [])),
            "statistics." + key,
            "需要字符串列表",
        )
    sources = raw.get("sources", [])
    require(
        isinstance(sources, list)
        and bool(sources)
        and len(sources) == len(set(sources))
        and not set(sources) - set(profile["domains"]),
        "sources",
        "未知、空或重复来源",
    )
    for domain, fields in raw.get("fields", {}).items():
        require(domain in sources and isinstance(fields, dict), "fields", "提取域未读取")
        for name, spec in fields.items():
            require(isinstance(spec, dict), "fields", "字段设置需要映射")
            known = profile["source_fields"].get(domain, {})
            require(
                name in known or {"array", "association", "components"} <= set(spec),
                "fields",
                f"未知字段 {domain}.{name} 必须明确来源、归属及分量",
            )
    geometry = raw.get("geometry", [])
    require(isinstance(geometry, (list, dict)), "geometry", "需要能力列表或参数映射")
    require(all(isinstance(v, str) for v in geometry), "geometry", "能力名称需要字符串")
    allowed = {item["id"]: item for item in profile["geometry"]}
    require(
        not set(geometry) - set(allowed) and len(geometry) == len(set(geometry)),
        "geometry",
        "未知或重复能力",
    )
    for name in geometry:
        item = allowed[name]
        if isinstance(geometry, dict):
            import math

            options = geometry[name]
            params = item.get("parameters", {})
            require(
                isinstance(options, dict) and not set(options) - set(params),
                "geometry." + name,
                "不支持的能力参数",
            )
            for key, value in options.items():
                require(
                    type(value) in (int, float) and math.isfinite(value) and value > 0,
                    "geometry." + name + "." + key,
                    "需要正有限数",
                )
        require(
            not set(item.get("conflicts", [])) & set(geometry), "geometry", "互斥能力不能同时启用"
        )
        require(set(item.get("domains", [])) <= set(sources), "geometry", "缺少所需数据域")
    filters = raw.get("filters", {})
    require(isinstance(filters, dict), "filters", "需要映射")
    filter_options = {(item["domain"], item["id"]): item for item in profile["filters"]}
    for domain, names in filters.items():
        require(domain in sources and isinstance(names, list), "filters", "未知域或非法筛选列表")
        for name in names:
            require((domain, name) in filter_options, "filters", "未知筛选")
            require(
                set(filter_options[(domain, name)].get("requires", [])) <= set(geometry),
                "filters",
                "筛选依赖的几何能力未启用",
            )
    extraction = raw.get("extraction")
    require(extraction is None or isinstance(extraction, dict), "extraction", "需要映射")
    if extraction:
        compile_extraction(
            extraction,
            declarations=profile["output_routes"],
            source_catalog=profile["source_fields"],
        )
        if extraction.get("layout") != "fields":
            return  # 历史容器由其既有编译与样本校验执行。
    outputs = selected_outputs(raw, profile)
    require(bool(outputs), "save_fields", "至少选择一个输出")
    names = [item["name"] for item in outputs]
    require(len(names) == len(set(names)), "save_fields", "输出名称重复")
    from ai4e_core.abilities.data.validate import validate_filemap

    validate_filemap({name: name + ".pt" for name in names})
    declarations = {item["name"]: item for item in profile["outputs"]}
    selected = {item["source_field"] for item in outputs}
    for item in outputs:
        ref = item["source_field"]
        if ref in declarations:
            definition = declarations[ref]
            require(definition["domain"] in sources, "save_fields", "输出域未读取")
            require(
                set(definition.get("requires", [])) <= set(geometry),
                "save_fields",
                f"{ref} 依赖未启用",
            )
            require(
                not definition.get("requires_any")
                or bool(set(definition["requires_any"]) & set(geometry)),
                "save_fields",
                f"{ref} 需要距离能力",
            )
        else:
            require(bool(extraction) and len(ref.split("/")) == 3, "save_fields", f"未知字段 {ref}")
    for item in profile["outputs"]:
        if item.get("required") and item["domain"] in sources:
            require(
                item["name"] in selected or item["source_field"] in selected,
                "save_fields",
                "必须保留坐标与实体身份: " + item["name"],
            )
    stats = raw.get("statistics", {})
    require(
        stats.get("mode", "none") in profile["statistics_modes"],
        "statistics.mode",
        "不支持的统计策略",
    )
    require(set(stats.get("fields", [])) <= set(names), "statistics.fields", "统计字段必须保存")
    if stats.get("mode") == "reference":
        require(
            all(
                item["source_field"] in declarations and item["name"] == item["source_field"]
                for item in outputs
            ),
            "statistics",
            "新增或重命名字段请选择重算或不生成统计",
        )
