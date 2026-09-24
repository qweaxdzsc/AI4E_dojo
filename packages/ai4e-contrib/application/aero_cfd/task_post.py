"""外流后处理的清单、字段与平台样本描述；不依赖任务存储。"""

import json
from pathlib import Path

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


def read_json(path):
    return json.loads(Path(path).read_text())


def _owned(path, run):
    return Path(path)


def _fields(record, counts=None):
    result = []
    for domain_name, domain in record.get("domains", {}).items():
        for name, key in domain.get("targets", {}).items():
            components = [
                k[len(key) + 1 :] for k in record.get("metrics", {}) if k.startswith(key + "/")
            ]
            if counts is not None:
                count = counts.get(key, 0)
                components = (
                    ["scalar"]
                    if count == 1
                    else (["magnitude", *map(str, range(count))] if count else [])
                )
            if key + ".truth" not in record.get("filemap", {}):
                components = []
            for component in components:
                result.append(
                    {
                        "id": f"{domain_name}:{name}:{component}",
                        "domain": domain_name,
                        "field": name,
                        "component": component,
                        "association": domain.get("association", "point"),
                        "unit": domain.get("units", {}).get(name),
                        "label": f"{domain_name} / {name}"
                        + (
                            " · 模长"
                            if component == "magnitude"
                            else ""
                            if component == "scalar"
                            else f" · 分量{component}"
                        ),
                        "default": component in {"scalar", "magnitude"},
                    }
                )
    return result


def _manifests(run):
    root = Path(run["run_dir"])
    report_path = next(
        (
            root / "artifacts" / n
            for n in ("inference-results.json", "physical-predictions.json")
            if (root / "artifacts" / n).is_file()
        ),
        None,
    )
    if report_path:
        _owned(report_path, run)
        report = read_json(report_path)
        return [
            (r.get("sample", r.get("sample_id")), Path(r["manifest"]))
            for r in report.get("results", [])
            if r.get("manifest")
        ], report_path
    found = []
    progress = root / "artifacts/inference-progress.json"
    if progress.is_file():
        for op in read_json(progress).get("operations", {}).values():
            found.extend(
                (None, Path(p)) for p in op.get("artifacts", []) if Path(p).name == "manifest.json"
            )
    return found, None


def _members(manifest, record):
    members = [manifest]
    for value in record.get("filemap", {}).values():
        if Path(value).name != value:
            raise ValueError("结果成员路径越界")
        members.append(manifest.parent / value)
    members.extend(manifest.parent / m["path"] for m in record.get("meshes", {}).values())
    return list(dict.fromkeys(members))


def _vtk_skip_note(record, members):
    """历史或缺网格时给用户看的原因，不能只靠缺文件。"""
    if any(Path(path).suffix.lower() in MESH_SUFFIXES for path in members):
        return None
    status = record.get("vtk") if isinstance(record.get("vtk"), dict) else {}
    if status.get("exported"):
        return None
    reason = status.get("reason") or "该次推理未导出网格"
    return "未写出VTK：" + reason


def _dataset_samples(item):
    """用清单里的 sample 编号对齐原数据与推理 VTK，不另起一套 ID。"""
    record = read_json(item["manifest_path"])
    rows = []
    for entry in record.get("samples") or []:
        sample = entry.get("sample") or entry.get("sample_id")
        path = entry.get("path")
        if not sample or not path:
            continue
        rows.append(
            {
                "sample_id": str(sample),
                "path": Path(path),
                "split": entry.get("partition") or entry.get("split"),
            }
        )
    if rows:
        return rows
    root = Path(item["manifest_path"]).parent
    for split, names in (record.get("partitions") or {}).items():
        for name in names:
            candidate = root / split / name
            if candidate.is_dir():
                rows.append({"sample_id": str(name), "path": candidate, "split": split})
    return rows


def describe_run(run):
    """读取固定运行报告，返回可评价字段和成员；不扫描残留猜测成功。"""
    from ai4e_core.applications.aero_cfd.post import describe_result_fields

    manifests, report = _manifests(run)
    results, errors = [], []
    for sample, manifest in manifests:
        try:
            record = read_json(manifest)
            members = _members(manifest, record)
            fields = _fields(record)
            error = None
            if not fields:
                header = describe_result_fields([str(manifest)])[str(manifest)]
                fields = _fields(record, header.get("components", {}))
                error = header.get("error")
            results.append(
                {
                    "manifest": str(manifest),
                    "sample": sample or record.get("identity", {}).get("sample"),
                    "identity": record.get("identity", {}),
                    "fields": fields,
                    "metrics": record.get("metrics", {}),
                    "members": [str(p) for p in members],
                    "vtk_note": _vtk_skip_note(record, members),
                    "evaluation_error": error,
                }
            )
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"sample": sample, "error": str(exc)})
    return {"results": results, "report": str(report) if report else None, "errors": errors}


def run_metrics(run):
    """将外流报告解释为页面已有的评价和进度描述，统计口径不变。"""
    root = Path(run["run_dir"]) / "artifacts"
    result = {}
    physical = next(
        (
            root / name
            for name in ("inference-results.json", "physical-predictions.json")
            if (root / name).is_file()
        ),
        None,
    )
    if physical:
        record = read_json(physical)
        result["evaluation"] = {
            "metrics": record.get("metrics", {}),
            "status": record.get("status"),
            "samples": [
                {
                    "sample": row.get("sample", row.get("sample_id")),
                    "metrics": row.get("metrics", {}),
                }
                for row in record.get("results", [])
            ],
        }
    for key, name in (("post", "post-progress.json"), ("infer", "inference-progress.json")):
        if (root / name).is_file():
            result[key] = read_json(root / name)
    return result


def describe_samples(item):
    """返回清单中的样本身份及文件位置，路径控制归消费方。"""
    return [{**row, "path": str(row["path"])} for row in _dataset_samples(item)]
