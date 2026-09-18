"""按运行清单列出推理交付，不扫描旧文件或加载物理场数组。"""

from pathlib import Path

from ..storage.files import read_json
from .checkpoints import file_digest, inspect_inference
from .inference import read_inference_batch
from .records import get_run

MESH_SUFFIXES = {
    ".vtk",
    ".vtu",
    ".vtp",
    ".vts",
    ".vtr",
    ".vti",
    ".vtm",
    ".pvtu",
    ".pvtp",
    ".vtkhdf",
    ".pvd",
}


def _member(path: Path, run: dict) -> dict:
    """结果成员必须属于本次子运行的数据或运行目录。"""
    resolved = path.resolve()
    roots = [Path(run[key]).resolve() for key in ("data_dir", "run_dir")]
    if not any(resolved.is_relative_to(root) for root in roots) or path.is_symlink():
        raise ValueError("inference_result_outside_run")
    if not resolved.is_file():
        raise ValueError("inference_result_missing: " + path.name)
    return {
        "name": path.name,
        "path": str(resolved),
        "size": resolved.stat().st_size,
        "revision": file_digest(resolved),
    }


def inference_results(project: str | Path, task_id: str, identity: str) -> dict:
    """读取部分/完整结果，完整比较由公开算法检查门面判断。"""
    batch = read_inference_batch(project, task_id, identity)
    items, reports, records = [], [], []
    request_path = (
        Path(project) / "tasks" / task_id / ".dojo/inference_batches" / identity / "request.json"
    )
    try:
        request = read_json(request_path)
    except FileNotFoundError as exc:
        raise ValueError("inference_batch_not_found: 推理批次不存在或已被清理") from exc
    children = [*request.get("inherited_children", []), *batch["children"]]
    for child in children:
        run = get_run(project, child["run_id"])
        if run["task_id"] != task_id:
            raise ValueError("inference_run_task_mismatch")
        root = Path(run["run_dir"]) / "artifacts"
        report_path = next(
            (
                p
                for name in ("inference-results.json", "physical-predictions.json")
                if (p := root / name).is_file()
            ),
            None,
        )
        report = (
            read_json(report_path)
            if report_path
            else child.get("progress")
            if child.get("progress", {}).get("results")
            else None
        )
        if report:
            reports.append(
                {
                    **report,
                    "run_id": run["id"],
                    "checkpoint": child["checkpoint"]["name"],
                    "status": "succeeded"
                    if run["status"] == "succeeded" and report.get("status") == "succeeded"
                    else "partial",
                }
            )
            manifests = [
                (r["sample"], Path(r["manifest"]))
                for r in report.get("results", [])
                if r.get("manifest")
            ]
        else:
            # 仅读取账本确认已提交的样本清单，不能从残留目录猜测成功。
            manifests = []
            progress = child.get("progress", {})
            for op in progress.get("operations", {}).values():
                for filename in op.get("artifacts", []):
                    path = Path(filename)
                    if path.name == "manifest.json":
                        manifests.append((None, path))
        split = child.get("split") or (report or {}).get("protocol", {}).get(
            "split", request["request"].get("split", "unknown")
        )
        entries = (report or {}).get("results", [])
        if not entries:
            entries = [{"sample": sample, "manifest": str(path)} for sample, path in manifests]
        seen = set()
        for entry in entries:
            path = Path(entry["manifest"]) if entry.get("manifest") else None
            manifest_member = _member(path, run) if path else None
            record = read_json(path) if path else entry
            sample = entry.get("sample", entry.get("sample_id")) or record.get("identity", {}).get(
                "sample"
            )
            if sample is None or (split, sample) in seen:
                continue
            seen.add((split, sample))
            files = [manifest_member] if manifest_member else []
            if path:
                for name in record.get("filemap", {}).values():
                    member = Path(name)
                    if member.is_absolute() or ".." in member.parts:
                        raise ValueError("inference_member_escape")
                    files.append(_member(path.parent / member, run))
                for mesh in record.get("meshes", {}).values():
                    files.append(_member(path.parent / mesh["path"], run))
            cp = {k: child["checkpoint"].get(k) for k in ("id", "name", "revision", "epoch")}
            vtk = record.get("vtk") if isinstance(record.get("vtk"), dict) else {}
            has_mesh = any(Path(file["name"]).suffix.lower() in MESH_SUFFIXES for file in files)
            exported = bool(vtk.get("exported", has_mesh))
            item = {
                "run_id": run["id"],
                "checkpoint": cp,
                "split": split,
                "sample": sample,
                "sample_id": (record.get("identity") or {}).get("sample") or sample,
                "files": files,
                "metrics": record.get("metrics", {}),
                "status": run["status"],
                "metric_records": entry.get("metric_records", record.get("metric_records", [])),
                "timings": entry.get("timings", {}),
                "vtk": {
                    "exported": exported,
                    "reason": None if exported else (vtk.get("reason") or "该次推理未导出网格"),
                    "kind": vtk.get("kind"),
                    "sample_id": (record.get("identity") or {}).get("sample") or sample,
                },
            }
            items.append(item)
            for row in item["metric_records"]:
                records.append(
                    {
                        **row,
                        "run_id": run["id"],
                        "checkpoint_id": cp["id"],
                        "checkpoint_revision": cp["revision"],
                        "checkpoint": cp["name"] + " · " + cp["id"].split(":", 1)[0][:8],
                        "split": split,
                        "sample": sample,
                        "expected_all": sum(
                            len(c.get("samples", request["request"].get("samples", [])))
                            for c in children
                            if c["checkpoint"]["id"] == cp["id"]
                        ),
                        "expected": len(
                            child.get("samples", request["request"].get("samples", []))
                        ),
                        "timings": item["timings"],
                        "protocol": (report or {}).get("protocol", {}).get("digest"),
                    }
                )
    comparison = (
        inspect_inference("compare", reports=reports)
        if reports
        else {"status": "insufficient", "reason": "尚无完整推理指标", "rows": []}
    )
    if batch["status"] != "succeeded":
        comparison = {
            "status": "insufficient",
            "reason": "批次尚未完整成功，保留已完成指标但不开放完整比较",
            "rows": comparison.get("rows", []),
        }
    views = (
        inspect_inference("result_views", records=records)
        if records
        else {"records": [], "statistics": []}
    )
    return {
        "items": items,
        "comparison": comparison,
        "reports": reports,
        **views,
        "batch": {"id": identity, "status": batch["status"]},
    }
