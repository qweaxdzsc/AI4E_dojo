"""业务字段选择、实体身份声明和统一筛选，不承担编码或写入。"""

import numpy as np

from ai4e_core.abilities.data.extract import extract_coordinates
from ai4e_core.abilities.data.filter.records import filter_records
from ai4e_core.abilities.data.validate import require_valid_records, validate_filemap


def select_fields(ctx: dict, *, output: dict) -> dict:
    """选择已提取或已生成的场；映射声明 domain/field，fields. 前缀表示物理场。"""
    data = ctx["data"]
    filemap = output["filemap"]
    validate_filemap(filemap)
    specifications = output.get("fields", {})
    bundles = output.get("bundles", {})
    optional = set(output.get("optional", []))
    if set(specifications) & set(bundles):
        raise ValueError("普通场和打包输出逻辑名重复")
    if set(filemap) != set(specifications) | set(bundles):
        raise ValueError("filemap 必须与 fields/bundles 的输出逻辑名完全对应")
    if optional - set(filemap):
        raise ValueError("optional 含未声明输出")
    groups, records, routes, skipped = {}, [], {}, []

    def group_for(domain, association):
        key = f"{domain}:{association}"
        if key not in groups:
            mesh = data[domain]["vtk"]
            count = mesh.GetNumberOfPoints() if association == "point" else mesh.GetNumberOfCells()
            ids = np.arange(count, dtype=np.int64)
            ids.setflags(write=False)
            groups[key] = {
                "source": domain,
                "association": association,
                "count": count,
                "entity_ids": ids,
            }
        return key, groups[key]

    def collect(logical, domain, field):
        payload = data[domain]
        if field.startswith("fields."):
            physical = field.removeprefix("fields.")
            values = payload["fields"][physical]
            spec = payload["field_specs"][physical]
            association, kind = spec["association"], spec["kind"]
        else:
            values = extract_coordinates(payload["vtk"]) if field == "points" else payload[field]
            association = "point"
            kind = "scalar" if np.asarray(values).ndim == 1 else "vector"
        key, group = group_for(domain, association)
        # 提取和几何 API 均承诺原 VTK 身份。外部重排的字段应直接提供 FieldRecord。
        return {
            "name": logical,
            "values": np.asarray(values),
            "association": association,
            "kind": kind,
            "group": key,
            "source": domain,
            "entity_ids": group["entity_ids"],
        }

    for logical, spec in specifications.items():
        try:
            record = collect(logical, spec["domain"], spec["field"])
        except KeyError as exc:
            if logical in optional:
                skipped.append(logical)
                continue
            raise ValueError(f"缺少必需输出 {logical}: {spec}") from exc
        records.append(record)
        routes[logical] = (logical, None)
    for logical, spec in bundles.items():
        domain, association = spec["domain"], spec["association"]
        if association not in ("point", "cell"):
            raise ValueError(f"非法 bundle 归属: {association}")
        payload = data.get(domain, {})
        selected = [
            name
            for name, field in payload.get("field_specs", {}).items()
            if field["association"] == association
        ]
        if not selected and logical not in optional:
            raise ValueError(f"缺少必需输出: {logical}")
        if not selected:
            skipped.append(logical)
        for name in selected:
            record_name = f"{logical}/{name}"
            records.append(collect(record_name, domain, f"fields.{name}"))
            routes[record_name] = (logical, name)
    if not records:
        raise ValueError("输出为空，不能报告写入成功")
    return {
        **ctx,
        "records": records,
        "groups": groups,
        "routes": routes,
        "output": output,
        "skipped": skipped,
    }


def validate_fields(ctx: dict) -> dict:
    """落盘前强制验证同组身份，结果可随样本摘要交付。"""
    report = require_valid_records(ctx["records"], ctx["groups"], sample=str(ctx.get("sample", "")))
    return {**ctx, "validation": report}


def filter_points(ctx: dict, *, filters: dict) -> dict:
    """按域配置合并显式点标记，不自动套用其他已有 mask。"""
    masks = {}
    for domain, names in filters.items():
        if domain not in ctx["data"]:
            raise ValueError(f"筛选域不存在: {domain}")
        key = f"{domain}:point"
        if not names or key not in ctx["groups"]:
            continue
        if not isinstance(names, list) or len(names) != len(set(names)):
            raise ValueError(f"筛选标记必须是不重复的名称列表: {domain}")
        mask = np.ones(ctx["groups"][key]["count"], dtype=bool)
        for name in names:
            if name not in ctx["data"][domain]:
                raise ValueError(f"筛选标记未生成: {domain}.{name}")
            raw = np.asarray(ctx["data"][domain][name])
            if raw.dtype != bool or raw.shape != mask.shape:
                raise ValueError(f"筛选标记须为等长一维布尔数组: {domain}.{name}")
            mask &= raw
        masks[key] = mask
    records, groups = filter_records(ctx["records"], ctx["groups"], masks)
    report = require_valid_records(records, groups, sample=str(ctx.get("sample", "")))
    return {
        **ctx,
        "records": records,
        "groups": groups,
        "filtered_validation": report,
        "filters": filters,
    }
