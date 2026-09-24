"""任务范围的已交付结果目录；列举训练运行、平台数据集与推理结果，不加载模型或场数组。"""

from datetime import UTC, datetime
from pathlib import Path

from ..storage.snapshots import digest
from .checkpoints import file_digest
from .inference import read_inference_batch
from .records import get_run, get_task, list_runs

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
RESULT_DATA_FOLDERS = ("infer", "post", "predictions", "meshes", "analysis", "exports")
SEARCH_LIMIT = 200
WALK_BUDGET = 64
SAMPLE_TREE_SEP = "／"


def _sample_tree_key(sample_id):
    """树路径一段对应一个 sample_id，避免 param1/<设计号> 被拆成两层。"""
    return str(sample_id).replace("/", SAMPLE_TREE_SEP)


def _sample_tree_dir(prefix, sample_id):
    return prefix + "/" + _sample_tree_key(sample_id)


def _same_sample_dir(directory, prefix, sample_id):
    encoded = _sample_tree_dir(prefix, sample_id)
    legacy = prefix + "/" + sample_id
    return directory in {encoded, legacy} or directory.startswith((encoded + "/", legacy + "/"))


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


def _fields(record, counts=None):
    return record.get("fields", [])


def _manifests(run):
    catalog = run.get("result_description")
    if catalog is None:
        raise ValueError(
            run.get("result_description_error")
            or "operation_unavailable: captured_result_description_missing"
        )
    return [(row["sample"], Path(row["manifest"])) for row in catalog["results"]], catalog["report"]


def _description(run, manifest):
    return next(
        row for row in run["result_description"]["results"] if row["manifest"] == str(manifest)
    )


def _describe_run(project, task_id, run):
    from .checkpoints import inspect_inference
    from .operation_sources import operation_context

    try:
        context = operation_context(project, task_id, run=run)
        result = inspect_inference("post_catalog", context=context, run=run)
        valid = []
        for row in result["results"]:
            try:
                _owned(row["manifest"], run)
                for member in row["members"]:
                    _owned(member, run)
                valid.append(row)
            except (ValueError, OSError) as exc:
                result.setdefault("errors", []).append(
                    {"sample": row.get("sample"), "error": str(exc)}
                )
        return {
            **run,
            "result_description": {**result, "results": valid},
            "operation_context": context,
        }
    except (ValueError, OSError) as exc:
        return {**run, "result_description_error": str(exc)}


def _visible_entries(path):
    """当前层可见成员；跳过隐藏项和符号链接，不读内容。"""
    if not path.is_dir():
        return []
    entries = sorted(path.iterdir(), key=lambda candidate: (not candidate.is_dir(), candidate.name))
    return [item for item in entries if not item.name.startswith(".") and not item.is_symlink()]


def _has_visible_file(path, *, budget=WALK_BUDGET):
    """在受控结果目录内确认存在可列文件；遇首个文件即停，不整树扫描。"""
    resolved = Path(path)
    if not resolved.exists() or resolved.is_symlink():
        return False
    if resolved.is_file() or (resolved.is_dir() and resolved.suffix == ".zarr"):
        return True
    if not resolved.is_dir():
        return False
    stack = [resolved]
    seen = 0
    while stack and seen < budget:
        current = stack.pop()
        for child in _visible_entries(current):
            seen += 1
            if child.is_file() or (child.is_dir() and child.suffix == ".zarr"):
                return True
            if child.is_dir():
                stack.append(child)
    return False


def _result_data_folders(run):
    """训练/独立推理写在 data_dir 的可浏览结果目录，不含准备副本或检查点。"""
    root = Path(run["data_dir"])
    return [name for name in RESULT_DATA_FOLDERS if _has_visible_file(root / name)]


def _safe_manifests(run):
    try:
        return _manifests(run)
    except (ValueError, OSError, KeyError, TypeError):
        return [], None


def _source_kind(run):
    """判断运行是否可能提供结果文件；原始处理与数据准备不进入此树。"""
    if run.get("metadata", {}).get("purpose") == "post_metrics":
        return None
    stages = set(run.get("stages") or [])
    purpose = run.get("metadata", {}).get("purpose")
    if purpose == "inference" or "infer" in stages:
        return "infer"
    if "train" in stages:
        return "train"
    if "post" in stages:
        return "legacy"
    return None


def _has_result_payload(run):
    manifests, _ = _safe_manifests(run)
    return bool(manifests) or bool(_result_data_folders(run))


def _vtk_skip_note(record, members):
    return record.get("vtk_note")


def _run_prefix(kind, run):
    """训练用 run 短号，与推理批次名称区分；不把时间写进路径以免时区漂移。"""
    short = run["id"][:8]
    if kind == "legacy":
        return (
            "legacy:" + run["id"],
            "历史后处理/" + run["id"],
            {"name": "历史结果", "id": run["id"]},
        )
    if kind == "train":
        return "train:" + run["id"], "训练运行 · " + short, {"name": "训练结果", "id": run["id"]}
    return "infer:" + run["id"], "推理运行 · " + short, {"name": "推理结果", "id": run["id"]}


def _train_empty_name(run):
    """无写出时的明确空态；失败开训不冒充已有预测或网格。"""
    status = run.get("status")
    if status == "failed":
        return "没有预测或网格（开训失败）"
    if status in {"queued", "running", "stopping"}:
        return "训练尚未写出预测或网格"
    return "没有写出预测或网格"


def _folder_children(run, root, tree_base, current, extra):
    """按层列出 data_dir 结果目录，不哈希、不读文件内容。"""
    root = Path(root)
    if not root.is_dir():
        return []
    if current and not (
        tree_base == current
        or tree_base.startswith(current + "/")
        or current.startswith(tree_base + "/")
    ):
        return []
    target = root
    if current.startswith(tree_base + "/"):
        target = root / current[len(tree_base) + 1 :]
    if not target.exists() or target.is_file():
        return []
    rows = []
    for path in _visible_entries(target):
        rel = str(path.relative_to(root))
        tree_path = f"{tree_base}/{rel}"
        if path.is_dir() and path.suffix != ".zarr":
            rows.append(_dir_node(tree_path, **extra))
        else:
            rows.append(_light_file(path, run, tree_path, **extra))
    return rows


def _search_folder(run, root, tree_base, extra):
    """仅在已知结果目录内按路径搜索，达到上限即停。"""
    root = Path(root)
    if not root.is_dir():
        return []
    rows = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts) or path.is_symlink():
            continue
        if not path.is_file() and not (path.is_dir() and path.suffix == ".zarr"):
            continue
        rows.append(_light_file(path, run, f"{tree_base}/{relative}", **extra))
        if len(rows) >= SEARCH_LIMIT:
            break
    return rows


def _members(manifest, record):
    return [Path(path) for path in record["members"]]


def _branches(project, task_id):
    """收集批次/运行前缀，不读结果文件内容。"""
    from ..storage.records import listing

    batches, errors, owned, branches = [], [], set(), []
    for record in reversed(listing(project, "inference_batch")):
        if record["task_id"] != task_id:
            continue
        for child in record.get("children") or []:
            if child.get("run_id"):
                owned.add(child["run_id"])
        try:
            batches.append(read_inference_batch(project, task_id, record["id"]))
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"batch_id": record["id"], "error": str(exc)})
    for batch in batches:
        for child in batch["children"]:
            try:
                run = _describe_run(project, task_id, get_run(project, child["run_id"]))
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
                        "kind": "batch",
                    }
                )
            except (OSError, KeyError, ValueError, TypeError) as exc:
                errors.append({"batch_id": batch["id"], "error": str(exc)})
    extras, extra_branches = [], []
    for run in list_runs(project, task_id):
        if run["id"] in owned:
            continue
        run = _describe_run(project, task_id, run)
        kind = _source_kind(run)
        if kind is None:
            continue
        has_payload = _has_result_payload(run)
        if kind != "train" and not has_payload:
            continue
        try:
            batch_id, prefix, checkpoint = _run_prefix(kind, run)
            extra_branches.append(
                {
                    "batch_id": batch_id,
                    "prefix": prefix,
                    "run": run,
                    "checkpoint": checkpoint,
                    "status": run["status"],
                    "kind": kind,
                }
            )
            if kind in {"train", "infer"} and has_payload:
                extras.append(
                    {
                        "id": batch_id,
                        "name": prefix,
                        "status": run["status"],
                        "created_at": run.get("created_at"),
                    }
                )
        except (OSError, KeyError, ValueError, TypeError) as exc:
            errors.append({"run_id": run["id"], "error": str(exc)})
    trains = [item for item in extra_branches if item["kind"] == "train"]
    others = [item for item in extra_branches if item["kind"] != "train"]
    trains.sort(key=lambda item: item["run"].get("created_at") or "", reverse=True)
    branches = trains + branches + others
    public = [{k: b.get(k) for k in ("id", "name", "status", "created_at")} for b in batches]
    public.extend(extras)
    return batches, branches, errors, public


def _sample_item(branch, sample, manifest, record, members):
    prefix = branch["prefix"]
    run = branch["run"]
    entries = [
        _light_file(
            path,
            run,
            f"{_sample_tree_dir(prefix + '/结果', sample)}/{path.relative_to(manifest.parent)}",
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
        "operation_context": run.get("operation_context"),
        "evaluation_error": record.get("evaluation_error"),
    }


def post_results(project, task_id):
    """统一批次、独立推理与历史运行的评价目录；训练无清单时不进入评价项。"""
    get_task(project, task_id)
    _batches, branches, errors, public_batches = _branches(project, task_id)
    items, unknown = [], []
    for branch in branches:
        errors.extend(
            {"run_id": branch["run"]["id"], **error}
            for error in branch["run"].get("result_description", {}).get("errors", [])
        )
        try:
            manifests, _ = _manifests(branch["run"])
        except (ValueError, OSError, KeyError, TypeError) as exc:
            errors.append({"batch_id": branch["batch_id"], "error": str(exc)})
            continue
        for sample, manifest in {str(p): (s, p) for s, p in manifests}.values():
            try:
                _owned(manifest, branch["run"])
                record = _description(branch["run"], manifest)
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
    return {
        "items": items,
        "files": [],
        "batches": public_batches + _dataset_batches(project, task_id),
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
            key,
            **{
                k: payload.get(k)
                for k in ("batch_id", "run_id", "sample", "split", "status", "kind")
            },
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
    return not (split and branch["run"].get("metadata", {}).get("split") != split)


def _legacy_children(run, prefix, folder, current):
    root = Path(run["run_dir"]) / folder
    if not root.is_dir():
        return []
    base = prefix + "/" + folder
    if current and not (
        base == current or base.startswith(current + "/") or current.startswith(base + "/")
    ):
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


def _dataset_prefix(item):
    return "平台数据集 · " + item["name"]


def _task_platform_datasets(project, task_id):
    """本任务发布或当前绑定的平台数据集，不含其他任务的共享登记。"""
    from omegaconf import OmegaConf

    from ..projects.datasets import list_shared_datasets
    from ..storage.layout import task_dir
    from ..storage.shared_datasets import resolve_reference
    from ..templates.materialize import recipe_entry
    from .configuration import read_configuration

    config = read_configuration(project, task_id).get("config", {})
    entry = recipe_entry(project, task_id)
    cfg = OmegaConf.create(config)
    recipe = task_dir(project, task_id) / "recipe"
    bound = []
    for key, kind in entry.get("inputs", {}).items():
        selected = OmegaConf.select(cfg, key)
        if kind == "dataset" and isinstance(selected, str):
            path = Path(selected).expanduser()
            path = path if path.is_absolute() else recipe / path
            bound.append(path.resolve())
    available = list_shared_datasets(project)
    selected_records = {}
    for path in bound:
        resolved = resolve_reference(project, path)
        if resolved is None:
            resolved = next(
                (
                    item
                    for item in available
                    if Path(item.get("manifest_path") or "").resolve() == path
                ),
                None,
            )
        if resolved and resolved.get("status") == "available":
            selected_records[resolved["name"]] = resolved
    if selected_records:
        return sorted(selected_records.values(), key=lambda item: item["name"])
    # 本任务已发布的结果可独立浏览；不从科学配置猜共享输出名称。
    return sorted(
        [
            item
            for item in available
            if item.get("source", {}).get("task_id") == task_id
            and item.get("status") == "available"
        ],
        key=lambda item: item["name"],
    )


def _dataset_samples(item, project, task_id):
    from .checkpoints import inspect_inference
    from .operation_sources import operation_context

    context = operation_context(project, task_id)
    rows = inspect_inference("dataset_samples", context=context, item=item)
    return [{**row, "path": Path(row["path"])} for row in rows]


def _project_light_file(path, project, tree_path, **extra):
    """共享平台数据在项目目录内，不挂到某次训练/推理 run。"""
    resolved = Path(path).resolve()
    root = Path(project).resolve()
    if not resolved.is_relative_to(root) or Path(path).is_symlink():
        raise ValueError("inference_result_outside_run")
    if not resolved.exists():
        raise ValueError("inference_result_missing: " + resolved.name)
    leaf = resolved.is_file() or (resolved.is_dir() and resolved.suffix == ".zarr")
    if not leaf:
        raise ValueError("inference_result_missing: " + resolved.name)
    stat = resolved.stat()
    return {
        "id": digest(["dataset", tree_path, stat.st_mtime_ns, stat.st_size]),
        "name": resolved.name,
        "path": str(resolved),
        "size": stat.st_size,
        "tree_path": tree_path,
        "modified_at": _mtime(resolved),
        "visualizable": resolved.suffix.lower() in MESH_SUFFIXES,
        **extra,
    }


def _dataset_batches(project, task_id):
    return [
        {
            "id": "dataset:" + item["name"],
            "name": _dataset_prefix(item),
            "status": "succeeded",
            "created_at": item.get("updated_at") or item.get("created_at"),
        }
        for item in _task_platform_datasets(project, task_id)
    ]


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
    """按层列出训练运行、平台数据集与推理结果；无写出的训练 run 仍保留文件夹。"""
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
        if not query:
            return True
        blob = " ".join(str(file.get(key) or "") for key in ("tree_path", "name", "sample"))
        return query.casefold() in blob.casefold()

    pinned = bool(sample and not directory)

    def add_file(file):
        if not keep(file):
            return
        if query or pinned:
            matched.append(file)
        else:
            _emit_level(directory, file["tree_path"], file, buckets)

    for branch in branches:
        if not _match(
            branch, batch=batch, run_id=run_id, sample=sample, split=split, status=status
        ):
            continue
        prefix = branch["prefix"]
        run = branch["run"]
        extra = {
            "batch_id": branch["batch_id"],
            "run_id": run["id"],
            "status": branch["status"],
            "kind": branch.get("kind", "batch"),
        }
        if run.get("created_at"):
            extra["modified_at"] = run["created_at"]
        kind = branch.get("kind", "batch")
        if (
            query
            and kind == "train"
            and (query.casefold() in prefix.casefold() or query.casefold() in run["id"].casefold())
        ):
            add_file(_dir_node(prefix, **extra))
            if not _has_result_payload(run):
                note = prefix + "/" + _train_empty_name(run)
                add_file(_dir_node(note, empty=True, **extra))
        if not query and not _inside(directory, prefix) and not _inside(prefix, directory):
            continue
        if not query:
            _emit_level(directory, prefix, _dir_node(prefix, **extra), buckets)
        manifests, _ = _safe_manifests(run)
        data_folders = _result_data_folders(run) if kind in {"train", "infer"} else []
        inspect_samples = bool(
            query
            or sample
            or directory == prefix + "/结果"
            or directory.startswith(prefix + "/结果/")
        )
        inspect_records = kind not in {"train", "infer"} and bool(
            query or directory.startswith(prefix + "/运行记录")
        )
        if not query and (directory == prefix or directory.startswith(prefix + "/")):
            if manifests:
                _emit_level(
                    directory, prefix + "/结果", _dir_node(prefix + "/结果", **extra), buckets
                )
            if kind not in {"train", "infer"} and any(
                (Path(run["run_dir"]) / name).is_file() for name in RECORD_NAMES
            ):
                _emit_level(
                    directory,
                    prefix + "/运行记录",
                    _dir_node(prefix + "/运行记录", **extra),
                    buckets,
                )
            if "infer" not in run.get("stages", []):
                for folder in LEGACY_FOLDERS:
                    for row in _legacy_children(run, prefix, folder, directory):
                        _emit_level(directory, row["tree_path"], row, buckets)
            if data_folders and not manifests:
                for folder in data_folders:
                    tree_base = prefix + "/" + folder
                    _emit_level(directory, tree_base, _dir_node(tree_base, **extra), buckets)
                    for row in _folder_children(
                        run, Path(run["data_dir"]) / folder, tree_base, directory, extra
                    ):
                        _emit_level(directory, row["tree_path"], row, buckets)
            if kind == "train" and not manifests and not data_folders:
                note = prefix + "/" + _train_empty_name(run)
                _emit_level(directory, note, _dir_node(note, empty=True, **extra), buckets)
        if query and data_folders and not manifests:
            for folder in data_folders:
                for row in _search_folder(
                    run, Path(run["data_dir"]) / folder, prefix + "/" + folder, extra
                ):
                    add_file(row)
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
                    if not path.is_file() or any(
                        p.startswith(".") for p in path.relative_to(root).parts
                    ):
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
                record = _description(branch["run"], manifest)
                current = (
                    raw_sample or record.get("identity", {}).get("sample") or manifest.parent.name
                )
                if sample and current != sample:
                    continue
                sample_dir = _sample_tree_dir(prefix + "/结果", current)
                if not query and directory == prefix + "/结果":
                    buckets[sample_dir] = _dir_node(
                        sample_dir, sample=current, name=current, **extra
                    )
                    continue
                if (
                    not query
                    and not _inside(directory, sample_dir)
                    and not _same_sample_dir(directory, prefix + "/结果", current)
                ):
                    continue
                members = _members(manifest, record)
                for path in members:
                    add_file(
                        _light_file(
                            path,
                            run,
                            f"{sample_dir}/{path.relative_to(manifest.parent)}",
                            sample=current,
                            split=run.get("metadata", {}).get(
                                "split", record.get("identity", {}).get("split")
                            ),
                            **extra,
                        )
                    )
                note = _vtk_skip_note(record, members)
                if note:
                    add_file(
                        _dir_node(
                            f"{sample_dir}/{note}",
                            empty=True,
                            sample=current,
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

    hide_datasets = bool(run_id or (batch and not str(batch).startswith("dataset:")))
    if not hide_datasets:
        for item in _task_platform_datasets(project, task_id):
            extra = {
                "batch_id": "dataset:" + item["name"],
                "kind": "dataset",
                "status": "succeeded",
            }
            if batch and batch != extra["batch_id"]:
                continue
            prefix = _dataset_prefix(item)
            try:
                samples = _dataset_samples(item, project, task_id)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                errors.append({"batch_id": extra["batch_id"], "error": str(exc)})
                continue
            if query:
                hit_name = (
                    query.casefold() in prefix.casefold()
                    or query.casefold() in item["name"].casefold()
                )
                if hit_name:
                    add_file(_dir_node(prefix, **extra))
                for row in samples:
                    if sample and row["sample_id"] != sample:
                        continue
                    sample_dir = _sample_tree_dir(prefix, row["sample_id"])
                    extra_s = {**extra, "sample": row["sample_id"], "split": row.get("split")}
                    if (
                        query.casefold() in row["sample_id"].casefold()
                        or query.casefold() in prefix.casefold()
                    ):
                        add_file(_dir_node(sample_dir, name=row["sample_id"], **extra_s))
                    if row["path"].is_dir():
                        for path in row["path"].rglob("*"):
                            if path.is_symlink() or any(
                                part.startswith(".") for part in path.relative_to(row["path"]).parts
                            ):
                                continue
                            if not path.is_file() and not (
                                path.is_dir() and path.suffix == ".zarr"
                            ):
                                continue
                            tree = sample_dir + "/" + str(path.relative_to(row["path"]))
                            if query.casefold() in tree.casefold():
                                add_file(_project_light_file(path, project, tree, **extra_s))
                continue
            if not _inside(directory, prefix) and not _inside(prefix, directory):
                continue
            if not directory:
                _emit_level(directory, prefix, _dir_node(prefix, **extra), buckets)
                continue
            if directory == prefix:
                if not samples:
                    note = prefix + "/没有可对照的样本"
                    _emit_level(directory, note, _dir_node(note, empty=True, **extra), buckets)
                for row in samples:
                    if sample and row["sample_id"] != sample:
                        continue
                    sample_dir = _sample_tree_dir(prefix, row["sample_id"])
                    buckets[sample_dir] = _dir_node(
                        sample_dir,
                        sample=row["sample_id"],
                        split=row.get("split"),
                        name=row["sample_id"],
                        **extra,
                    )
                continue
            for row in samples:
                sample_dir = _sample_tree_dir(prefix, row["sample_id"])
                extra_s = {**extra, "sample": row["sample_id"], "split": row.get("split")}
                if not _same_sample_dir(directory, prefix, row["sample_id"]):
                    continue
                rel = ""
                if directory.startswith(sample_dir + "/"):
                    rel = directory[len(sample_dir) + 1 :]
                elif directory.startswith(prefix + "/" + row["sample_id"] + "/"):
                    rel = directory[len(prefix + "/" + row["sample_id"]) + 1 :]
                target = row["path"] / rel if rel else row["path"]
                if not target.exists() or target.is_file():
                    continue
                for path in _visible_entries(target):
                    tree = sample_dir + "/" + str(path.relative_to(row["path"]))
                    if path.is_dir() and path.suffix != ".zarr":
                        _emit_level(directory, tree, _dir_node(tree, **extra_s), buckets)
                    else:
                        add_file(_project_light_file(path, project, tree, **extra_s))

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

    def _rank(row):
        path = row.get("tree_path") or ""
        if path.startswith("平台数据集"):
            return 0
        if path.startswith("训练运行"):
            return 1
        if path.startswith("指标"):
            return 3
        return 2

    files.sort(
        key=lambda row: (
            _rank(row),
            not row.get("directory"),
            row.get("tree_path", ""),
        )
    )
    return {"files": files, "errors": errors, "total": len(files)}
