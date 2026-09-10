"""样本输出规划、具名编码和提交；不枚举样本或执行批量循环。"""

import warnings
from pathlib import Path
from typing import TypedDict

from ai4e_core.abilities.data.save import encode_field, write_named_tensors
from ai4e_core.abilities.data.save.store import BackupCleanupWarning
from ai4e_core.abilities.data.validate import ValidationReport, plan_output, require_valid_records


class SampleResult(TypedDict):
    """已提交或预检后的轻量样本结果，不携带网格或数组。"""

    sample: str
    written: bool
    path: str
    names: list[str]
    filemap: dict[str, str]
    available_fields: list[str]
    validation: ValidationReport
    filtered_validation: ValidationReport
    counts: dict[str, int]
    filters: dict[str, list[str]]
    skipped: list[str]
    warnings: list[str]


def sample_destination(config: dict, sample: str | Path | None) -> Path:
    """解析实际样本目录，禁止样本或子目录逃离输出根。"""
    output = config["pre"]["output"]
    base = Path(output["dir"]).absolute()
    subdir = Path(output.get("root_subdir", "."))
    relative = Path(sample or ".")
    for path in (subdir, relative):
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"非法输出相对路径: {path}")
    dest = base / subdir / relative
    if not dest.resolve().is_relative_to(base.resolve()):
        raise ValueError(f"输出路径逃离数据根: {dest}")
    return dest


def tensorize(ctx: dict) -> dict:
    """按显式路由打包张量；单元场与点场均由业务配置选择。"""
    require_valid_records(ctx["records"], ctx["groups"], sample=str(ctx.get("sample", "")))
    payloads = {}
    for record in ctx["records"]:
        logical, member = ctx["routes"][record["name"]]
        tensor = encode_field(record)
        if member is None:
            if logical in payloads:
                raise ValueError(f"输出逻辑名重复: {logical}")
            payloads[logical] = tensor
        else:
            bundle = payloads.setdefault(logical, {})
            if member in bundle:
                raise ValueError(f"打包字段重复: {logical}/{member}")
            bundle[member] = tensor
    return {**ctx, "payloads": payloads}


def write_tensors(ctx: dict) -> dict[str, SampleResult]:
    """dry-run 和提交共用预检；只返回轻量结果，不把整批数组带回 run。"""
    output = ctx["output"]
    dest = sample_destination(ctx["config"], ctx.get("sample"))
    selected = plan_output(
        dest,
        list(ctx["payloads"]),
        output["filemap"],
        optional=output.get("optional", []),
        overwrite=ctx.get("overwrite", False),
    )
    extras = {}
    if ctx.get("vtkhdf"):
        import json
        from functools import partial

        from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf

        mapping = {}
        for domain, data in ctx["data"].items():
            records = [r for r in ctx["records"] if r["source"] == domain]
            extras[domain + ".vtkhdf"] = partial(write_vtkhdf, mesh=data["vtk"], records=records)
            for record in records:
                mapping[record["name"]] = {
                    "mesh": domain + ".vtkhdf",
                    "association": record["association"],
                    "entity_ids": record["entity_ids"].tolist(),
                }
        extras["entity_mapping.json"] = lambda path: path.write_text(json.dumps(mapping))
    notices = []
    if not ctx.get("dry_run", False):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", BackupCleanupWarning)
            write_named_tensors(
                dest,
                ctx["payloads"],
                selected,
                overwrite=ctx.get("overwrite", False),
                extra_writers=extras,
            )
        notices = [str(w.message) for w in caught]
    result: SampleResult = {
        "sample": str(ctx.get("sample") or "."),
        "written": not ctx.get("dry_run", False),
        "path": str(dest),
        "names": list(selected),
        "filemap": selected,
        "available_fields": [a if b is None else f"{a}/{b}" for a, b in ctx["routes"].values()],
        "validation": ctx["validation"],
        "filtered_validation": ctx["filtered_validation"],
        "counts": {k: g["count"] for k, g in ctx["groups"].items()},
        "filters": ctx.get("filters", {}),
        "skipped": ctx["skipped"],
        "warnings": notices,
    }
    if extras:
        result["assets"] = list(extras)
    return {"result": result}
