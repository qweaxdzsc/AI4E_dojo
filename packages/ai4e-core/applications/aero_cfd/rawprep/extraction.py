"""提取容器编译为既有字段路由；每个输出成员独立保留实体归属。"""


def compile_extraction(
    extraction: dict, *, format: str = "pt", declarations=None, source_catalog=None
) -> dict:
    """编译显式来源到 output.members，不在弹窗声明格式或输出目录。"""
    if format not in {"pt", "zarr"}:
        raise ValueError("rawprep.format 必须为 pt 或 zarr")
    layout = extraction.get("layout", "containers")
    if layout not in {"containers", "fields"}:
        raise ValueError("extraction.layout: 未知输出布局")
    outputs, ids, requested, aliases = {}, set(), {}, {}
    for entry in extraction.get("entries", []):
        identity = entry["id"]
        if identity in ids:
            raise ValueError("提取容器身份重复")
        ids.add(identity)
        for output in entry.get("outputs", []):
            name = output["name"]
            if name in outputs:
                raise ValueError("提取输出名称重复")
            members = {}
            for member in output["members"]:
                target = member["output_member"]
                source = member["source_field"]
                if isinstance(source, str):
                    if source in (declarations or {}):
                        source = declarations[source]
                    else:
                        parts = source.split("/")
                        if len(parts) != 3 or parts[1] not in {
                            "geometry",
                            "point",
                            "cell",
                            "global",
                            "array",
                        }:
                            raise ValueError(f"非法来源字段: {source}")
                        if parts[1] in {"point", "cell"}:
                            requested.setdefault(parts[0], {})[parts[2]] = {
                                "array": parts[2],
                                "association": parts[1],
                                "components": member.get("components", 1),
                            }
                        source = {
                            "domain": parts[0],
                            "field": "points" if parts[1] == "geometry" else "fields." + parts[2],
                        }
                if target in members or not target or "/" in target or target in {".", ".."}:
                    raise ValueError("输出成员名称重复或非法")
                members[target] = dict(source)
                for semantic, declaration in (declarations or {}).items():
                    normalized = dict(source)
                    field = normalized.get("field", "").removeprefix("fields.")
                    for semantic_field, detail in (
                        (source_catalog or {}).get(normalized.get("domain"), {}).items()
                    ):
                        if detail.get("array") == field:
                            normalized["field"] = "fields." + semantic_field
                    if dict(declaration) == normalized:
                        reference = name if layout == "fields" else name + "/" + target
                        if semantic != reference:
                            aliases.setdefault(semantic, reference)
            if not members:
                raise ValueError("提取输出必须有成员")
            if layout == "fields" and len(members) != 1:
                raise ValueError("逐场输出必须恰好包含一个逻辑字段")
            outputs[name] = members
    if not outputs:
        raise ValueError("提取容器必须有输出")
    from ai4e_core.abilities.data.validate import validate_filemap

    validate_filemap({name: name + "." + format for name in outputs})
    return {
        "source_fields": requested,
        "field_aliases": aliases,
        "members": outputs if layout == "containers" else {},
        "fields": {name: next(iter(members.values())) for name, members in outputs.items()}
        if layout == "fields"
        else {},
        "filemap": {name: name + "." + format for name in outputs},
        "optional": [],
    }
