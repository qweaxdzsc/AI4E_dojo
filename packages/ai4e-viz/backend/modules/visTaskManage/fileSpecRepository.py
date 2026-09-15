"""任务目录中的不可变配置修订；所有输入仅允许声明式 JSON。"""

from copy import deepcopy
from pathlib import Path

from infrastructure.storage.atomic import canonical, contained, identity, read_json, write_json


def validate_spec(spec: dict) -> dict:
    """拒绝原始数据、机器路径和运行对象，保留有限且可重放的配置。"""
    if not isinstance(spec, dict) or spec.get("schema_version") not in (1, 2):
        raise ValueError("unsupported_visualization_schema")
    allowed = {
        "schema_version",
        "kind",
        "sources",
        "pipeline",
        "layers",
        "views",
        "link_groups",
        "time",
        "renderer",
        "implementation",
        "parameters",
        "method",
        "layout",
        "probes",
    }
    if set(spec) - allowed:
        raise ValueError("unknown_spec_fields: " + ",".join(sorted(set(spec) - allowed)))
    forbidden = {
        "path",
        "root",
        "output_dir",
        "url",
        "port",
        "pid",
        "payload",
        "geometry_buffers",
        "topology_buffers",
        "cells",
        "connectivity",
        "vtk_object",
        "data",
        "arrays",
        "session_id",
    }

    def walk(value):
        """递归检查声明，排除运行对象、网格数组和机器地址。"""
        if isinstance(value, dict):
            if set(value) & forbidden:
                raise ValueError("spec_contains_runtime_or_raw_data")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            if len(value) > 4096:
                raise ValueError("spec_array_too_large")
            for child in value:
                walk(child)
        elif isinstance(value, str) and (
            value.startswith(("file:", "http:", "https:", "ws:", "wss:")) or "\\" in value
        ):
            raise ValueError("spec_contains_machine_location")

    walk(spec)
    if len(canonical(spec)) > 1024 * 1024:
        raise ValueError("spec_too_large")
    sources = spec.get("sources", [])
    empty_workspace = spec.get("kind") == "phys_field" and spec.get("schema_version") == 2
    if (not sources and not empty_workspace) or len({s.get("id") for s in sources}) != len(sources):
        raise ValueError("unique_sources_required")
    for source in sources:
        identity(source["id"])
        ref = source.get("ref", {})
        if not ref.get("asset_id") or not ref.get("revision"):
            raise ValueError("fixed_source_revision_required")
    if spec.get("schema_version") == 2:
        if spec.get("kind") != "phys_field":
            raise ValueError("unsupported_visualization_schema")
        from .physicalSpec import normalize_physical_spec

        normalize_physical_spec(spec)
    return deepcopy(spec)


def write_revision(asset_root: Path, revision: int, spec: dict) -> None:
    """写入尚未被资产索引引用的新修订。"""
    path = contained(asset_root, f"revisions/{revision:06d}/spec.json")
    if path.exists():
        if read_json(path) != spec:
            raise ValueError("spec_revision_conflict")
        return
    write_json(path, spec)


def read_revision(asset_root: Path, revision: int) -> dict:
    """按正整数修订读取配置，不修改历史文件。"""
    if not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid_revision")
    return read_json(contained(asset_root, f"revisions/{revision:06d}/spec.json"))
