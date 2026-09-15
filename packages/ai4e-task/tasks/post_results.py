"""任务范围的已交付结果目录；仅解析清单，不加载模型或场数组。"""

from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

from ..storage.files import read_json
from ..storage.snapshots import digest
from .checkpoints import file_digest
from .inference import read_inference_batch
from .query import get_run, get_task, list_runs

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
RECORD_NAMES = (
    "logs/run.log",
    "artifacts/inference-progress.json",
    "artifacts/post-progress.json",
    "artifacts/physical-predictions.json",
    "artifacts/inference-results.json",
    "summary.json",
)
LEGACY_FOLDERS = ("predictions", "meshes", "post")
SEARCH_LIMIT = 200


def _owned(path, run):
    """确认结果属于本次运行目录，不读文件内容。"""
    resolved = Path(path).resolve()
    roots = [Path(run[key]).resolve() for key in ("data_dir", "run_dir")]
    if not any(resolved.is_relative_to(root) for root in roots) or Path(path).is_symlink():
        raise ValueError("inference_result_outside_run")
    if not resolved.exists():
        raise ValueError("inference_result_missing: " + resolved.name)
    return resolved


def _mtime(path):
    return datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()


def _item_revision(manifest, members):
    """目录身份只累计清单字节和成员体积/时间，不读结果内容。"""
    return digest(
        {
            "manifest": file_digest(manifest),
            "members": [
                {
                    "name": path.name,
                    "size": path.stat().st_size,
                    "mtime": path.stat().st_mtime_ns,
                }
                for path in members
            ],
        }
    )


def _light_file(path, run, tree_path, **extra):
    resolved = _owned(path, run)
    leaf = resolved.is_file() or (resolved.is_dir() and resolved.suffix == ".zarr")
    if not leaf:
        raise ValueError("inference_result_missing: " + resolved.name)
    stat = resolved.stat()
    return {
        "id": digest([run["id"], tree_path, stat.st_mtime_ns, stat.st_size]),
        "name": resolved.name,
        "path": str(resolved),
        "size": stat.st_size,
        "tree_path": tree_path,
        "run_id": run["id"],
        "modified_at": _mtime(resolved),
        "visualizable": resolved.suffix.lower() in MESH_SUFFIXES,
        **extra,
    }


def freeze_result_item(item):
    """提交评价时才固定成员内容修订。"""
    files = [{**file, "revision": file_digest(Path(file["path"]))} for file in item["files"]]
    return {**item, "files": files}


@lru_cache(maxsize=32)
def _field_headers(references):
    """按固定修订缓存头部检查，管理进程不读数组。"""
    from .checkpoints import inspect_inference

    return inspect_inference("result_fields", manifests=[p for p, _ in references])


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
                (None, Path(p))
                for p in op.get("artifacts", [])
                if Path(p).name == "manifest.json"
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


def _branches(project, task_id):
    """收集批次/运行前缀，不读结果文件内容。"""
    from ..storage.records import listing

    batches, errors, owned, branches = [], [], set(), []
    for record in reversed(listing(project, "inference_batch")):
        if record["task_id"] != task_id:
            continue
        try:
            batches.append(read_inference_batch(project, task_id, record["id"]))
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"batch_id": record["id"], "error": str(exc)})
    for batch in batches:
        for child in batch["children"]:
            try:
                run = get_run(project, child["run_id"])
                if run["task_id"] != task_id:
                    raise ValueError("结果运行不属于当前任务")
                owned.add(run["id"])
                checkpoint = {
                    k: child["checkpoint"].get(k) for k in ("id", "name", "revision", "epoch")
                }
                prefix = (
                    f"{batch.get('name') or batch['id']} · {batch['id'][:8]}/"
                    f"{checkpoint['name']} · {run['id'][:8]}"
                )
                branches.append(
                    {
                        "batch_id": batch["id"],
                        "prefix": prefix,
                        "run": run,
                        "checkpoint": checkpoint,
                        "status": run["status"],
                    }
                )
            except (OSError, KeyError, ValueError, TypeError) as exc:
                errors.append({"batch_id": batch["id"], "error": str(exc)})
    for run in list_runs(project, task_id):
        if (
            run["id"] in owned
            or "post" not in run.get("stages", [])
            or run.get("metadata", {}).get("purpose") == "post_metrics"
        ):
            continue
        try:
            branches.append(
                {
                    "batch_id": "legacy:" + run["id"],
                    "prefix": "历史后处理/" + run["id"],
                    "run": run,
                    "checkpoint": {"name": "历史结果", "id": run["id"]},
                    "status": run["status"],
                }
            )
        except (OSError, KeyError, ValueError, TypeError) as exc:
            errors.append({"run_id": run["id"], "error": str(exc)})
    return (
        batches,
        branches,
        errors,
        [{k: b.get(k) for k in ("id", "name", "status", "created_at")} for b in batches],
    )


def _sample_item(branch, sample, manifest, record, members):
    prefix = branch["prefix"]
    run = branch["run"]
    entries = [
        _light_file(
            path,
            run,
            f"{prefix}/结果/{sample}/{path.relative_to(manifest.parent)}",
            batch_id=branch["batch_id"],
            sample=sample,
        )
        for path in members
    ]
    return {
        "id": digest([branch["batch_id"], run["id"], sample, str(manifest)]),
        "batch_id": branch["batch_id"],
        "run_id": run["id"],
        "checkpoint": branch["checkpoint"],
        "sample": sample,
        "split": run.get("metadata", {}).get("split", record.get("identity", {}).get("split")),
        "manifest": str(manifest),
        "tree_prefix": prefix,
        "fields": _fields(record),
        "files": entries,
        "status": run["status"],
        "metrics": record.get("metrics", {}),
        "evaluable": bool(_fields(record)),
        "revision": _item_revision(manifest, members),
    }


def post_results(project, task_id):
    """统一批次与历史运行的评价目录；不给结果文件做内容摘要。"""
    get_task(project, task_id)
    _batches, branches, errors, public_batches = _branches(project, task_id)
    items, unknown = [], []
    for branch in branches:
        try:
            manifests, _ = _manifests(branch["run"])
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"batch_id": branch["batch_id"], "error": str(exc)})
            continue
        for sample, manifest in {str(p): (s, p) for s, p in manifests}.values():
            try:
                _owned(manifest, branch["run"])
                record = read_json(manifest)
                sample = sample or record.get("identity", {}).get("sample") or manifest.parent.name
                members = _members(manifest, record)
                for path in members:
                    _owned(path, branch["run"])
                item = _sample_item(branch, sample, manifest, record, members)
                items.append(item)
                if not item["fields"]:
                    unknown.append((item, record))
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append(
                    {
                        "batch_id": branch["batch_id"],
                        "run_id": branch["run"]["id"],
                        "sample": sample,
                        "error": str(exc),
                    }
                )
    if unknown:
        try:
            headers = _field_headers(tuple((i["manifest"], i["revision"]) for i, _ in unknown))
            for item, record in unknown:
                header = headers[item["manifest"]]
                item["fields"] = _fields(record, header.get("components", {}))
                item["evaluable"] = bool(item["fields"])
                if header.get("error"):
                    item["evaluation_error"] = header["error"]
        except (ValueError, OSError, RuntimeError) as exc:
            for item, _ in unknown:
                item["evaluation_error"] = str(exc)
    return {
        "items": items,
        "files": [],
        "batches": public_batches,
        "errors": errors,
    }


def _dir_node(tree_path, **extra):
    name = tree_path.rsplit("/", 1)[-1]
    return {
        "id": "dir:" + tree_path,
        "name": name,
        "tree_path": tree_path,
        "directory": True,
        "path": "",
        **extra,
    }


def _emit_level(directory, tree_path, payload, buckets):
    directory = directory.strip("/")
    if directory and tree_path == directory:
        return
    if directory and not tree_path.startswith(directory + "/"):
        return
    rest = tree_path[len(directory) + 1 :] if directory else tree_path
    first, sep, _ = rest.partition("/")
    key = (directory + "/" + first) if directory else first
    if sep:
        buckets[key] = buckets.get(key) or _dir_node(
            key, **{k: payload.get(k) for k in ("batch_id", "run_id", "sample", "split", "status")}
        )
    else:
        buckets[key] = payload


def _match(branch, *, batch, run_id, sample, split, status):
    if batch and branch["batch_id"] != batch:
        return False
    if run_id and branch["run"]["id"] != run_id:
        return False
    if status and branch["status"] != status:
        return False
    if split and branch["run"].get("metadata", {}).get("split") != split:
        return False
    return True


def _legacy_children(run, prefix, folder, current):
    root = Path(run["run_dir"]) / folder
    if not root.is_dir():
        return []
    base = prefix + "/" + folder
    if current and not (base == current or base.startswith(current + "/") or current.startswith(base + "/")):
        return []
    target = root
    if current.startswith(base + "/"):
        target = root / current[len(base) + 1 :]
    if not target.exists() or target.is_file():
        return []
    rows = []
    for path in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name)):
        if path.name.startswith(".") or path.is_symlink():
            continue
        rel = str(path.relative_to(Path(run["run_dir"])))
        tree_path = prefix + "/" + rel
        if path.is_dir() and path.suffix != ".zarr":
            rows.append(_dir_node(tree_path, batch_id="legacy:" + run["id"], run_id=run["id"]))
        else:
            rows.append(_light_file(path, run, tree_path, batch_id="legacy:" + run["id"]))
    return rows


def _inside(directory, tree_path):
    directory = (directory or "").strip("/")
    return not directory or tree_path == directory or tree_path.startswith(directory + "/")


def list_post_result_files(
    project,
    task_id,
    *,
    directory="",
    query="",
    batch=None,
    run_id=None,
    sample=None,
    split=None,
    status=None,
):
    """按层列出结果树；搜索才遍历清单成员，列举不读文件内容。"""
    get_task(project, task_id)
    from ..storage.records import listing

    _, branches, errors, _ = _branches(project, task_id)
    directory = (directory or "").strip("/")
    query = (query or "").strip()
    buckets = {}
    matched = []

    def keep(file):
        if sample and file.get("sample") not in (None, sample):
            return False
        if query and query.casefold() not in file["tree_path"].casefold():
            return False
        return True

    pinned = bool(sample and not directory)

    def add_file(file):
        if not keep(file):
            return
        if query or pinned:
            matched.append(file)
        else:
            _emit_level(directory, file["tree_path"], file, buckets)

    for branch in branches:
        if not _match(branch, batch=batch, run_id=run_id, sample=sample, split=split, status=status):
            continue
        prefix = branch["prefix"]
        run = branch["run"]
        extra = {"batch_id": branch["batch_id"], "run_id": run["id"], "status": branch["status"]}
        if not query and not _inside(directory, prefix) and not _inside(prefix, directory):
            continue
        if not query:
            _emit_level(directory, prefix, _dir_node(prefix, **extra), buckets)
        inspect_samples = bool(
            query
            or sample
            or directory == prefix + "/结果"
            or directory.startswith(prefix + "/结果/")
        )
        inspect_records = bool(query or directory.startswith(prefix + "/运行记录"))
        if not query and (directory == prefix or directory.startswith(prefix + "/")):
            _emit_level(directory, prefix + "/结果", _dir_node(prefix + "/结果", **extra), buckets)
            if any((Path(run["run_dir"]) / name).is_file() for name in RECORD_NAMES):
                _emit_level(
                    directory, prefix + "/运行记录", _dir_node(prefix + "/运行记录", **extra), buckets
                )
            if "infer" not in run.get("stages", []):
                for folder in LEGACY_FOLDERS:
                    for row in _legacy_children(run, prefix, folder, directory):
                        _emit_level(directory, row["tree_path"], row, buckets)
        if inspect_records:
            for name in RECORD_NAMES:
                path = Path(run["run_dir"]) / name
                if path.is_file():
                    add_file(_light_file(path, run, prefix + "/运行记录/" + name, **extra))
        if not inspect_samples:
            continue
        try:
            manifests, _ = _manifests(run)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"batch_id": branch["batch_id"], "error": str(exc)})
            continue
        if not manifests and "infer" not in run.get("stages", []) and query:
            for folder in LEGACY_FOLDERS:
                root = Path(run["run_dir"]) / folder
                if not root.is_dir():
                    continue
                for path in root.rglob("*"):
                    if not path.is_file() or any(p.startswith(".") for p in path.relative_to(root).parts):
                        continue
                    add_file(
                        _light_file(
                            path,
                            run,
                            prefix + "/" + str(path.relative_to(Path(run["run_dir"]))),
                            **extra,
                        )
                    )
        for raw_sample, manifest in {str(p): (s, p) for s, p in manifests}.values():
            try:
                record = read_json(manifest)
                current = (
                    raw_sample or record.get("identity", {}).get("sample") or manifest.parent.name
                )
                if sample and current != sample:
                    continue
                sample_dir = f"{prefix}/结果/{current}"
                if not query and directory == prefix + "/结果":
                    buckets[sample_dir] = _dir_node(sample_dir, sample=current, **extra)
                    continue
                if not query and not _inside(directory, sample_dir):
                    continue
                for path in _members(manifest, record):
                    add_file(
                        _light_file(
                            path,
                            run,
                            f"{sample_dir}/{path.relative_to(manifest.parent)}",
                            sample=current,
                            split=run.get(
                                "metadata", {}
                            ).get("split", record.get("identity", {}).get("split")),
                            **extra,
                        )
                    )
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append(
                    {
                        "batch_id": branch["batch_id"],
                        "run_id": run["id"],
                        "sample": raw_sample,
                        "error": str(exc),
                    }
                )

    for job in listing(project, "post_metric_job"):
        if job["task_id"] != task_id or (batch and batch != "metrics"):
            continue
        run = get_run(project, job["run_id"])
        for name in ["metrics.json", *[e["name"] for e in job.get("exports", [])]]:
            path = Path(job["data_dir"]) / name
            if path.is_file():
                add_file(
                    _light_file(
                        path,
                        run,
                        "指标计算/" + job["id"][:8] + "/" + name,
                        batch_id="metrics",
                    )
                )

    files = matched if query or pinned else list(buckets.values())
    if query:
        files = files[:SEARCH_LIMIT]
    files.sort(key=lambda row: (not row.get("directory"), row.get("tree_path", "")))
    return {"files": files, "errors": errors, "total": len(files)}
