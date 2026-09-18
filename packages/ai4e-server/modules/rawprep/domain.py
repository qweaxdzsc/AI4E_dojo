"""配置编辑规则只接受现有案例能准确表达的字段、过滤和几何。"""

from copy import deepcopy

from ..capabilities.aero_cfd import OUTPUTS

ALLOWED = {
    "sources",
    "fields",
    "geometry",
    "save_fields",
    "filters",
    "statistics",
    "vtkhdf",
    "format",
    "formats",
    "extraction",
}


def validate(raw):
    """返回校验后的独立配置；错误携带配置位置。"""

    def require(condition, location, reason):
        if not condition:
            raise ValueError(location + ": " + reason)

    require(isinstance(raw, dict) and not set(raw) - ALLOWED, "rawprep", "unsupported_keys")
    require(
        raw.get("sources") in (["surface", "volume"], ["surface"]),
        "rawprep.sources",
        "仅支持表面或表面与体积完整样本",
    )
    require(
        raw.get("fields")
        == {
            source: fields
            for source, fields in {
                "surface": {"pressure": {"components": 1}},
                "volume": {"velocity": {"components": 3}},
            }.items()
            if source in raw.get("sources", [])
        },
        "rawprep.fields",
        "当前案例仅支持 point_scalars 压力与 point_vectors 速度；不支持重命名和单元场",
    )
    formats = raw.get("formats")
    selected = list(formats) if formats is not None else [raw.get("format") or "pt"]
    if not selected or any(item not in {"pt", "zarr"} for item in selected):
        raise ValueError("rawprep.formats: unsupported_format")
    if "extraction" in raw:
        entries = raw["extraction"].get("entries", [])
        require(isinstance(entries, list), "rawprep.extraction.entries", "需要列表")
        for entry in entries:
            require(
                bool(entry.get("id")) and bool(entry.get("name")),
                "rawprep.extraction",
                "条目名称和身份不能为空",
            )
            for output in entry.get("outputs", []):
                require(
                    bool(output.get("name")) and bool(output.get("members")),
                    "rawprep.extraction.outputs",
                    "输出名称和成员不能为空",
                )
    outputs = raw.get("save_fields", [])
    require(
        isinstance(outputs, list) and all(isinstance(x, str) for x in outputs),
        "rawprep.save_fields",
        "输出应为具名列表",
    )
    require(
        bool(outputs) and len(set(outputs)) == len(outputs) and not set(outputs) - OUTPUTS.keys(),
        "rawprep.save_fields",
        "不支持的输出或重复输出",
    )
    geometry = raw.get("geometry", [])
    require(
        isinstance(geometry, list) and all(isinstance(x, str) for x in geometry),
        "rawprep.geometry",
        "几何配置应为列表",
    )
    require(
        not set(geometry)
        - {
            "nearest_vertex",
            "volume_normals",
            "nearest_surface",
            "mesh_signed_distance",
            "surface_normals",
            "exterior_mask",
        }
        and len(geometry) == len(set(geometry)),
        "rawprep.geometry",
        "未知或重复能力",
    )
    require(
        not {"nearest_vertex", "nearest_surface"} <= set(geometry)
        and not {"nearest_vertex", "mesh_signed_distance"} <= set(geometry)
        and not {"volume_normals", "mesh_signed_distance"} <= set(geometry),
        "rawprep.geometry",
        "两种距离算法需要择一",
    )
    if "surface_normals" in outputs:
        require(
            "surface_normals" in geometry, "rawprep.save_fields.surface_normals", "需要启用表面法向"
        )
    if "volume_sdf" in outputs:
        require(
            bool({"nearest_vertex", "nearest_surface"} & set(geometry)),
            "rawprep.save_fields",
            "最近距离输出需要启用最近顶点距离",
        )
    if "volume_normals" in outputs:
        require(
            "volume_normals" in geometry or "nearest_vertex" in geometry,
            "rawprep.save_fields",
            "体积法向输出需要启用体积法向",
        )
    filters = raw.get("filters", {})
    require(
        isinstance(filters, dict) and not set(filters) - {"surface", "volume"},
        "rawprep.filters",
        "未知来源",
    )
    for source, key in [("surface", "mask"), ("volume", "exterior_mask")]:
        require(filters.get(source, []) in ([], [key]), "rawprep.filters." + source, "未知过滤规则")
    if filters.get("volume"):
        require("exterior_mask" in geometry, "rawprep.filters.volume", "体积清洗需要启用重合标记")
    require(isinstance(raw.get("vtkhdf"), bool), "rawprep.vtkhdf", "需要布尔值")
    stats = raw.get("statistics", {})
    require(
        isinstance(stats, dict) and not set(stats) - {"mode", "fields", "position_fields"},
        "rawprep.statistics",
        "不支持的统计设置",
    )
    require(
        stats.get("mode") in {"reference", "fit", "none"},
        "rawprep.statistics.mode",
        "只支持 reference/fit/none",
    )
    for key in ("fields", "position_fields"):
        require(
            isinstance(stats.get(key, []), list)
            and all(isinstance(x, str) for x in stats.get(key, [])),
            "rawprep.statistics." + key,
            "需要字段列表",
        )
    require(
        not set(stats.get("fields", [])) - OUTPUTS.keys(),
        "rawprep.statistics.fields",
        "未知统计字段",
    )
    require(
        not set(stats.get("position_fields", [])) - {"surface_position", "volume_position"},
        "rawprep.statistics.position_fields",
        "未知坐标字段",
    )
    if stats.get("mode") == "fit":
        require(
            bool(stats.get("fields")) and not set(stats["fields"]) - set(outputs),
            "rawprep.statistics.fields",
            "拟合统计字段必须已经输出",
        )
    return deepcopy(raw)
