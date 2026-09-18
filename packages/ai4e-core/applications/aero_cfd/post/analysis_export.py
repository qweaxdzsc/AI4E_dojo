"""单样本物理分析事务提交；大数据只写数据目录。"""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.abilities.postproc.export.visualization import save_image, save_mesh, save_profile

from .field_binding import verify_source


def safe_name(value: Any) -> str:
    """仅允许单个可移植文件名，禁止相对目录穿越。"""
    value = str(value)
    if not re.fullmatch(r"[\w.-]+", value) or value in {".", ".."}:
        raise ValueError("输出名称必须是单个安全文件名")
    return value


def write_metrics(path: str | Path, rows: list[dict], statistics: dict | None = None) -> None:
    """长表完整保存逐指标值、数量和不可定义原因。"""
    with (
        atomic_path(Path(path)) as temporary,
        temporary.open("w", newline="", encoding="utf-8") as stream,
    ):
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "field",
                "component",
                "metric",
                "value",
                "unit",
                "count",
                "excluded",
                "region",
                "status",
                "reason",
            ],
        )
        writer.writeheader()
        all_rows = list(rows)
        for label, result in (statistics or {}).items():
            all_rows.append(
                {
                    **result,
                    "field": result.get("field", label),
                    "component": result.get("component", "scalar"),
                    "status": "succeeded",
                    "values": {
                        key: result[key]
                        for key in ("min", "max", "mean", "std", "median", "p90")
                        if key in result
                    },
                }
            )
        for row in all_rows:
            for name, value in (row.get("values") or {"unavailable": None}).items():
                writer.writerow(
                    {
                        "field": row["field"],
                        "component": row["component"],
                        "metric": name,
                        "value": value,
                        "unit": row.get("unit"),
                        "count": row.get("count"),
                        "excluded": row.get("excluded"),
                        "region": json.dumps(row.get("region"), ensure_ascii=False),
                        "status": row["status"],
                        "reason": row.get("undefined", {}).get(name, row.get("reason")),
                    }
                )


def save_sample(
    sample: dict,
    *,
    output: str | Path,
    meshes: dict | None = None,
    images: dict | None = None,
    profiles: dict | None = None,
    metrics: list[dict] | None = None,
    statistics: dict | None = None,
    overwrite: bool = False,
) -> dict:
    """同目录暂存整份样本；失败保留原成品，不发布成功清单。"""
    verify_source(sample)
    statistics = {
        **{row["id"]: row["statistics"] for row in metrics or [] if "statistics" in row},
        **(statistics or {}),
    }
    origin = sample["origin"]
    source_id = safe_name(origin.get("id") or fingerprint(origin))
    identity = sample["metadata"]["identity"]
    sample_name = str(identity["sample"])
    if any(part in {".", "..", ""} for part in sample_name.split("/")) or "\\" in sample_name:
        raise ValueError("样本名称不能包含路径穿越")
    name = (
        safe_name(sample_name)
        if "/" not in sample_name
        else safe_name(sample_name.replace("/", "--") + "-" + fingerprint(sample_name)[:10])
    )
    root = Path(output).resolve() / source_id
    target = root / name
    if target.exists() and not overwrite:
        raise FileExistsError(f"分析结果已存在: {target}")
    root.mkdir(parents=True, exist_ok=True)
    temporary = root / ("." + name + "-" + uuid4().hex)
    backup = root / ("." + name + "-backup-" + uuid4().hex)
    temporary.mkdir()
    files = []
    try:

        def record(path, kind, parameters=None):
            files.append(
                {
                    "path": str(path.relative_to(temporary)),
                    "kind": kind,
                    "sha256": file_fingerprint(path),
                    "parameters": parameters or {},
                }
            )

        for label, mesh in (meshes or {}).items():
            from ai4e_core.abilities.postproc.visualization.fields import pyvista

            name = safe_name(label)
            folder = "analysis" if "post_transform" in mesh.field_data else "fields"
            path = (
                temporary
                / folder
                / (name + (".vtp" if isinstance(mesh, pyvista().PolyData) else ".vtu"))
            )
            save_mesh(mesh, path)
            parameters = (
                json.loads(str(mesh.field_data["post_transform"][0]))
                if "post_transform" in mesh.field_data
                else {}
            )
            record(path, "mesh", parameters)
        for label, image in (images or {}).items():
            path = temporary / "figures" / (safe_name(label) + ".png")
            save_image(image["pixels"] if isinstance(image, dict) else image, path)
            record(path, "image", image.get("parameters") if isinstance(image, dict) else None)
        for label, profile in (profiles or {}).items():
            path = temporary / "profiles" / (safe_name(label) + ".csv")
            save_profile(profile, path)
            record(path, "profile", {"interpolation": profile["interpolation"]})
        values = {"rows": metrics or [], "statistics": statistics or {}}
        save_json(temporary / "metrics.json", values)
        write_metrics(temporary / "metrics.csv", metrics or [], statistics)
        record(temporary / "metrics.json", "metrics")
        record(temporary / "metrics.csv", "metrics")
        report = {
            "version": 1,
            "status": "succeeded",
            "identity": identity,
            "domains": sample["metadata"]["domains"],
            "origin": origin,
            "timings": sample.get("timings", {}),
            "sources": sample.get("revisions", {}),
            "files": files,
            **values,
        }
        save_json(temporary / "manifest.json", report)
        verify_source(sample)
        if target.exists():
            target.rename(backup)
        try:
            temporary.rename(target)
        except BaseException:
            if backup.exists():
                backup.rename(target)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return {
            "sample": identity["sample"],
            "timings": sample.get("timings", {}),
            "origin": origin,
            "status": "succeeded",
            "manifest": str(target / "manifest.json"),
            "metrics": metrics or [],
            "statistics": statistics or {},
        }
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
