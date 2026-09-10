"""按配置提取具名物理量，交接原 VTK 对象、共享数组和原点序 mask。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, NotRequired, TypedDict

import numpy as np
from vtkmodules.vtkCommonDataModel import vtkDataObject

from ai4e_core.abilities.data.extract import extract_coordinates, extract_field
from ai4e_core.abilities.data.extract.vtk_fields import Association, FieldKind
from ai4e_core.abilities.data.filter import used_vertex_mask
from ai4e_core.abilities.data.filter.used_vertices import resolve_cell_type
from ai4e_core.abilities.data.source.read import read_file


class FieldConfig(TypedDict):
    """物理量的原始数组名称、点/单元归属和分量类别。"""

    array: str
    association: Association
    kind: FieldKind


class DomainResult(TypedDict):
    """域内原 VTK 引用、共享数组及字段描述；mask 仅对应原点序。"""

    vtk: vtkDataObject
    points: np.ndarray
    fields: dict[str, np.ndarray]
    field_specs: dict[str, FieldConfig]
    mask: NotRequired[np.ndarray]


class _DomainConfig(TypedDict):
    """经过读取前校验的域配置。"""

    source: str
    fields: dict[str, FieldConfig]
    cell_type: NotRequired[int]


class _SourceConfig(TypedDict):
    """单个数据源的文件路径与可选格式。"""

    filename: str
    format: str | None


def _text(value: Any, label: str) -> str:
    """校验必填字符串，保留精确数组名和路径，不自动修剪。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 必须是非空字符串")
    return value


def _validate(
    config: dict[str, Any],
) -> tuple[Path, dict[str, _SourceConfig], dict[str, _DomainConfig]]:
    """在任何文件读取前验证全部来源与两个域，拒绝旧配置及静默覆盖。"""
    dataset, source, pre = (config.get(key) for key in ("dataset", "source", "pre"))
    if not isinstance(dataset, dict) or not isinstance(dataset.get("root"), (str, Path)):
        raise TypeError("配置缺少有效 dataset.root")
    root = Path(_text(str(dataset["root"]), "dataset.root"))
    if not isinstance(source, dict) or not isinstance(source.get("files"), list):
        raise TypeError("source.files 必须是列表")
    files: dict[str, _SourceConfig] = {}
    for item in source["files"]:
        if not isinstance(item, dict):
            raise TypeError("source.files 每项必须是映射")
        name = _text(item.get("name"), "source.files.name")
        if name in files:
            raise ValueError(f"source.files.name 重复: {name}")
        filename = _text(item.get("filename"), f"source.{name}.filename")
        fmt = item.get("format")
        if fmt is not None:
            fmt = _text(fmt, f"source.{name}.format")
        files[name] = {"filename": filename, "format": fmt}
    if not isinstance(pre, dict):
        raise TypeError("配置 pre 必须是映射")
    domains: dict[str, _DomainConfig] = {}
    for role in ("surface", "volume"):
        if role not in pre:
            continue
        spec = pre.get(role)
        if not isinstance(spec, dict):
            raise TypeError(f"配置 pre.{role} 必须是映射")
        if "field" in spec:
            raise ValueError(
                f"pre.{role}.field 已移除，请迁移到 fields，声明 array/association/kind"
            )
        name = _text(spec.get("source"), f"pre.{role}.source")
        if name not in files:
            raise ValueError(f"pre.{role}.source 未在 source.files 中声明: {name}")
        fields = spec.get("fields")
        if not isinstance(fields, dict):
            raise ValueError(f"pre.{role}.fields 必须显式声明为映射（允许空映射）")  # noqa: TRY004 - 保持输入门禁统一 ValueError 契约
        parsed: dict[str, FieldConfig] = {}
        for physical, field in fields.items():
            physical = _text(physical, f"pre.{role} 物理量名称")
            label = f"pre.{role}.fields.{physical}"
            if not isinstance(field, dict):
                raise TypeError(f"{label} 必须是映射")
            array = _text(field.get("array"), f"{label}.array")
            association, kind = field.get("association"), field.get("kind")
            if association not in ("point", "cell"):
                raise ValueError(f"{label}.association 必须是 point 或 cell")
            if kind not in ("scalar", "vector"):
                raise ValueError(f"{label}.kind 必须是 scalar 或 vector")
            parsed[physical] = {"array": array, "association": association, "kind": kind}
        domain: _DomainConfig = {"source": name, "fields": parsed}
        if "cell_type" in spec:
            cell_type = spec["cell_type"]
            if isinstance(cell_type, bool) or not isinstance(cell_type, (str, int)):
                raise ValueError(f"pre.{role}.cell_type 必须是名称或整数")
            domain["cell_type"] = resolve_cell_type(cell_type)
        domains[role] = domain
    return root, files, domains


def dataread(ctx: dict, *, config: dict | None = None) -> dict:
    """校验全部来源配置后按样本读取，复用同源 VTK；不提取字段。"""
    config = ctx["config"] if config is None else config
    root, files, domains = _validate(config)
    relative = Path(ctx.get("sample") or ".")
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("样本必须是数据根下的相对路径")
    loaded_sources = {}
    loaded = {}
    paths = {}
    for role, spec in domains.items():
        name = spec["source"]
        item = files[name]
        path = root / relative / item["filename"]
        try:
            if name not in loaded_sources:
                loaded_sources[name] = read_file(path, format=item["format"])
        except (ValueError, TypeError, OSError) as exc:
            raise type(exc)(f"域={role}, 来源={path}: {exc}") from exc
        loaded[role] = loaded_sources[name]
        paths[role] = str(path)
    return {
        **ctx,
        "config": config,
        "loaded": loaded,
        "domain_specs": domains,
        "source_paths": paths,
    }


def extract_fields(ctx: dict) -> dict:
    """从已加载 VTK 提取字段与坐标，保持原身份；不执行几何或筛选。"""
    result = {}
    for role, spec in ctx["domain_specs"].items():
        loaded = ctx["loaded"][role]
        context = f"域={role}, 来源={ctx['source_paths'][role]}"
        try:
            points = extract_coordinates(loaded)
            fields = {}
            for physical, field in spec["fields"].items():
                try:
                    fields[physical] = extract_field(
                        loaded,
                        name=field["array"],
                        association=field["association"],
                        kind=field["kind"],
                    )
                except (ValueError, TypeError) as exc:
                    raise type(exc)(f"物理量={physical}: {exc}") from exc
            payload = {
                "vtk": loaded,
                "points": points,
                "fields": fields,
                "field_specs": spec["fields"],
            }
            if "cell_type" in spec:
                payload["mask"] = used_vertex_mask(loaded, cell_type=spec["cell_type"])
            result[role] = payload
        except (ValueError, TypeError) as exc:
            raise type(exc)(f"{context}: {exc}") from exc
    return {**ctx, "data": result}


def extract_configured_sample(config: dict, *, sample_relative=None) -> dict[str, DomainResult]:
    """直接读取并提取单样本的便捷入口，内部复用两个独立步骤。"""
    return extract_fields(dataread({"config": config, "sample": sample_relative}))["data"]


def enumerate_sample_relatives(root, *, param_count=9, exclude=None, expected_total=None):
    """保留参数分片业务枚举接口；不执行任何样本。"""
    root = Path(root)
    relatives = []
    for index in range(param_count):
        folder = root / f"param{index}"
        if not folder.is_dir():
            raise FileNotFoundError(f"参数目录不存在: {folder}")
        relatives.extend(
            p.relative_to(root)
            for p in sorted(folder.iterdir())
            if p.is_dir() and p.name not in (exclude or ())
        )
    if expected_total is not None and len(relatives) != expected_total:
        raise ValueError(f"期望 {expected_total} 个样本，实际 {len(relatives)}")
    return relatives


def discover_samples(ctx: dict, *, config: dict | None = None) -> dict:
    """发现稳定排序的样本引用；支持显式相对路径、glob 或参数分片。"""
    from ai4e_core.applications.aero_cfd.rawprep.save import sample_destination

    config = ctx["config"] if config is None else config
    root = Path(config["dataset"]["root"])
    spec = config["pre"].get("discover", {})
    if "samples" in spec:
        samples = [Path(p) for p in spec["samples"]]
    elif "glob" in spec:
        samples = sorted(p.relative_to(root) for p in root.glob(spec["glob"]) if p.is_dir())
    elif "param_count" in spec:
        samples = enumerate_sample_relatives(
            root, param_count=spec["param_count"], exclude=spec.get("exclude")
        )
    else:
        raise ValueError("discover 必须声明 samples、glob 或 param_count")
    samples = [p for p in samples if p.name not in spec.get("exclude", [])]
    if not samples:
        raise ValueError("未选择任何样本")
    if spec.get("expected_total") is not None and len(samples) != spec["expected_total"]:
        raise ValueError(f"期望 {spec['expected_total']} 个样本，实际 {len(samples)}")
    targets = set()
    for sample in samples:
        if sample.is_absolute() or ".." in sample.parts:
            raise ValueError(f"非法样本相对路径: {sample}")
        target = sample_destination(config, sample).resolve()
        if target in targets:
            raise ValueError(f"样本目标重复: {sample}: {target}")
        targets.add(target)
    return {**ctx, "config": config, "items": [str(p) for p in samples]}
