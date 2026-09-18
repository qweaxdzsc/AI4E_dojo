"""调用任务公开门面，校验完整文件选择并使用既有覆盖参数运行。"""

import json
from copy import deepcopy
from pathlib import Path

import ai4e_task as task

_SAMPLE_CATALOG = {}

from ...infrastructure.content_access import resolve, revision, roots
from ..capabilities.aero_cfd import require_profile
from ..tasks import read_binding


def preflight(service, project, identity, body, *, mode="execute"):
    """在执行前固定样本和内容摘要；不自动补齐选择。"""
    require_profile(service, project, identity)
    binding = read_binding(service, project, identity)
    if binding["status"] != "valid":
        raise ValueError("dataset_binding_" + binding["status"])
    base = service.project(project)
    cfg = task.read_configuration(base, identity)
    if body.revision != cfg["revision"]:
        raise ValueError("configuration_revision_conflict")
    if task.get_task(base, identity).get("archived"):
        raise ValueError("task_archived")
    if task.open_project(base).get("archived"):
        raise ValueError("project_archived")
    resolved = task.describe_rawprep(base, identity)
    task.validate_rawprep_configuration(base, identity, resolved["rawprep"], revision=body.revision)
    name = (cfg["config"].get("dataset") or {}).get("processed_name")
    if mode == "execute":
        from ..datasets.application import check_name, claim_config

        overwrite = bool(getattr(body, "overwrite_processed_name", False))
        check_name(
            service,
            name,
            claim_config(cfg["config"], resolved["rawprep"]),
            overwrite=overwrite,
            project=project,
        )
    if body.sample_scope is not None:
        return _sample_preflight(service, project, identity, body)

    return _generic_preflight(service, project, identity, body)


def submit(service, project, identity, body, *, mode="execute"):
    """原样执行 pipeline.py，只覆盖原数据处理阶段和选择。"""
    request_identity = body.model_dump(mode="json")
    retry = bool(body.idempotency_key) and any(
        run.get("operation_mode") == mode
        and run.get("metadata", {}).get("rawprep_request") == request_identity
        for run in task.list_runs(service.project(project), identity)
    )
    # 只有同一请求重放跳过名称预检；最终仍由 Task 核验完整幂等指纹。
    info = preflight(service, project, identity, body, mode="submission" if retry else mode)
    fixed = task.read_configuration(service.project(project), identity)
    if fixed["revision"] != info["revision"]:
        raise ValueError("configuration_revision_conflict")
    # 已审定旧加载入口没有 manifest 默认展开；提交同一修订下页面已展示的有效参数。
    resolved = task.describe_rawprep(service.project(project), identity)
    if resolved["revision"] != info["revision"]:
        raise ValueError("configuration_revision_conflict")
    fixed["config"]["rawprep"] = resolved["rawprep"]
    overrides = [
        "pipeline.stages=[rawprep]",
        "inputs.rawprep.source=" + json.dumps(info["root"]),
    ]
    # 固定本次核对的配置值，保存操作不会改变正在提交的原始处理设置。
    overrides += [
        key + "=" + json.dumps(value)
        for key, value in fixed["config"].items()
        if key not in {"pipeline", "dataset"}
    ]
    overrides += dataset_run_overrides(
        info.get("dataset_id"),
        body.sample_scope,
        info,
        fixed["config"].get("dataset") or {},
    )
    for name, digest in info["digests"].items():
        if revision(_selected_path(service, project, identity, body.root, name)) != digest:
            raise ValueError("file_changed_before_submission: " + name)
    metadata = {"rawprep_request": request_identity}
    if getattr(body, "overwrite_processed_name", False):
        metadata["overwrite_processed_name"] = True
    result = task.submit_run(
        service.project(project),
        identity,
        overrides=overrides,
        idempotency_key=body.idempotency_key,
        expected_revision=body.revision,
        operation_mode=mode,
        metadata=metadata,
        overwrite=bool(getattr(body, "overwrite_processed_name", False)),
        input_keys=[
            key
            for key in task.recipe_entry(service.project(project), identity).get("inputs", {})
            if key.startswith("inputs.rawprep.")
        ],
    )
    return result


def dataset_catalog(service, project, identity, body, *, public=False):
    """由案例描述生产样本身份；服务仅解析授权路径并过滤传输内容。"""
    from uuid import uuid4

    from ..visualization.application import register

    binding = read_binding(service, project, identity)
    if binding["status"] != "valid":
        raise ValueError("dataset_binding_" + binding["status"])
    config = task.read_configuration(service.project(project), identity)
    if body.revision != config["revision"]:
        raise ValueError("configuration_revision_conflict")
    if body.sample_scope is not None:
        return _sample_catalog(service, project, identity, body, public=public)
    is_nasa = binding["binding_mode"] == "files"
    reference = binding["sources"]["train_h5" if is_nasa else "root"]
    root = resolve(service, project, reference["root"], reference["path"])
    if is_nasa:
        root = root.parent
        samples = "all"
    else:
        selected = [_selected_path(service, project, identity, body.root, f) for f in body.files]
        if any(not path.is_relative_to(root) for path in selected):
            raise ValueError("dataset_selection_outside_binding")
        samples = body.samples or sorted({str(path.parent.relative_to(root)) for path in selected})

    result = task.inspect_task(
        service.project(project),
        identity,
        "inspect_dataset",
        revision=body.revision,
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
        selection={"root": str(root), "samples": samples},
    )
    for source in result["sources"]:
        path = Path(source["path"]).resolve()
        from ..tasks import controlled_reference

        if not is_nasa and not path.is_relative_to(root):
            raise ValueError("dataset_dependency_outside_selected_root")
        ref = controlled_reference(service, project, path)
        if not is_nasa:
            # 文件列表使用选择的数据根，样本身份使用已绑定数据集目录。
            base = roots(service, project)[body.root]
            if not path.is_relative_to(base):
                raise ValueError("dataset_dependency_outside_selected_root")
            ref = {"root": body.root, "path": str(path.relative_to(base))}
        source["relative_path"] = ref["root"] + "::" + ref["path"] if is_nasa else ref["path"]
        if not public:
            source["asset_ref"] = register(service, project, ref["root"], ref["path"], identity)
        if public:
            source.pop("path", None)
    result["dependencies"] = result["sources"]
    return result


def _generic_preflight(service, project, identity, body):
    """按数据集给出的完整依赖校验，不假定一文件对应一个样本。"""
    descriptor = dataset_catalog(service, project, identity, body)
    selected_files = sorted(set(body.files))
    if not body.all_selected:
        if body.count is None or body.count < 1 or body.count > len(selected_files):
            raise ValueError("invalid_file_count")
        selected_files = selected_files[: body.count]
    if descriptor["dataset_id"] == "nasa_crm":
        from ..tasks import controlled_reference

        normalized = []
        for name in selected_files:
            ref = controlled_reference(
                service, project, _selected_path(service, project, identity, body.root, name)
            )
            normalized.append(ref["root"] + "::" + ref["path"])
        selected_files = normalized
    selected = set(selected_files)
    source_by_id = {source["source_id"]: source for source in descriptor["sources"]}
    wanted = [
        sample
        for sample in descriptor["samples"]
        if body.samples is None
        or sample["sample_id"] in body.samples
        or sample["partition"] + "::" + str(sample["sample_id"]) in body.samples
    ]
    if not wanted:
        raise ValueError("dataset.samples: 请选择真实样本")
    required = {
        source_by_id[key]["relative_path"] for sample in wanted for key in sample["dependencies"]
    }
    if required - selected:
        raise ValueError("缺少配套文件: " + ", ".join(sorted(required - selected)))
    digests = {
        name: revision(_selected_path(service, project, identity, body.root, name))
        for name in sorted(required)
    }
    return {
        "samples": [sample["sample_id"] for sample in wanted],
        "sample_selection": (
            {
                split: [sample["sample_id"] for sample in wanted if sample["partition"] == split]
                for split in {sample["partition"] for sample in wanted}
            }
            if descriptor["dataset_id"] == "nasa_crm"
            else [sample["sample_id"] for sample in wanted]
        ),
        "dataset_id": descriptor["dataset_id"],
        "files": sorted(required),
        "file_count": len(required),
        "sample_count": len(wanted),
        "root": str(_bound_root(service, project, identity)),
        "revision": body.revision,
        "digests": digests,
    }


def _selected_path(service, project, identity, default_root, name):
    """兼容单根文件列表；跨根文件用显式受控根身份区分。"""
    root, relative = name.split("::", 1) if "::" in name else (default_root, name)
    if not root.startswith("data"):
        raise ValueError("registered_data_root_required")
    return resolve(service, project, root, relative, identity)


def _bound_root(service, project, identity):
    binding = read_binding(service, project, identity)
    key = binding["binding_schema"]["root_key"]
    ref = binding["sources"][key]
    path = resolve(service, project, ref["root"], ref["path"])
    return path.parent if binding["binding_mode"] == "files" else path


def _publish_sources(service, project, identity, result, *, public, register_files):
    """公开目录只解析受控相对路径；提交前才登记并哈希来源。"""
    from ..tasks import controlled_reference
    from ..visualization.application import register

    for source in result["sources"]:
        path = Path(source["path"]).resolve()
        if source.get("exists", True):
            ref = controlled_reference(service, project, path)
            source["relative_path"] = ref["root"] + "::" + ref["path"]
            if register_files:
                source["asset_ref"] = register(service, project, ref["root"], ref["path"], identity)
        if public:
            source.pop("path", None)
    return result


def _sample_catalog(service, project, identity, body, *, public=False, full=False):
    """新样本入口只传范围；打开页面不给全部来源做内容摘要。"""
    from uuid import uuid4

    key = (
        str(service.project(project)),
        identity,
        body.revision,
        json.dumps(body.sample_scope, sort_keys=True, ensure_ascii=False),
        public,
        full,
    )
    cached = _SAMPLE_CATALOG.get(key)
    if cached is not None:
        return deepcopy(cached)

    result = task.inspect_task(
        service.project(project),
        identity,
        "inspect_dataset",
        revision=body.revision,
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
        selection={
            "sample_scope": body.sample_scope,
            "inspection_scope": "all" if full else "representatives",
        },
    )
    _publish_sources(service, project, identity, result, public=public, register_files=full)
    if not full:
        _SAMPLE_CATALOG[key] = deepcopy(result)
        while len(_SAMPLE_CATALOG) > 8:
            _SAMPLE_CATALOG.pop(next(iter(_SAMPLE_CATALOG)))
    return result


def _sample_preflight(service, project, identity, body):
    """执行前逐样本核字段并固定来源修订；缺件不补造也不缩小范围。"""
    result = _sample_catalog(service, project, identity, body, full=True)
    if body.catalog_revision and result["revision"] != body.catalog_revision:
        raise ValueError("dataset_catalog_stale: 来源已改变，请重新检查")
    if result.get("errors"):
        raise ValueError(
            "原始数据检查失败: " + json.dumps(result["errors"][:10], ensure_ascii=False)
        )
    if not result["samples"]:
        raise ValueError("dataset.samples: 请选择真实样本")
    required = {key for sample in result["samples"] for key in sample["dependencies"]}
    files = sorted(
        {source["relative_path"] for source in result["sources"] if source["source_id"] in required}
    )
    return {
        "samples": [sample["sample_id"] for sample in result["samples"]],
        "sample_selection": result["selection"],
        "dataset_id": result["dataset_id"],
        "sample_count": len(result["samples"]),
        "files": files,
        "file_count": len(files),
        "root": str(_bound_root(service, project, identity)),
        "revision": body.revision,
        "catalog_revision": result["revision"],
        "digests": {
            name: revision(_selected_path(service, project, identity, body.root, name))
            for name in files
        },
    }


def dataset_run_overrides(dataset_id, sample_scope, info, task_dataset):
    """本次运行覆盖：读绑定数据集样本宇宙，不把官方切分写进平台原始处理产物。"""
    overrides = []
    skip = {"root", "samples", "partitions", "partition"}
    for key, value in (task_dataset or {}).items():
        if key not in skip:
            overrides.append("dataset." + key + "=" + json.dumps(value))
    if dataset_id != "nasa_crm":
        overrides.append("dataset.partitions=" + json.dumps("unsplit"))
    mode = (sample_scope or {}).get("mode")
    if mode == "all":
        overrides.append("dataset.samples=" + json.dumps("all"))
        return overrides
    selection = info.get("sample_selection", info["samples"])
    overrides.append("dataset.samples=" + json.dumps(selection))
    return overrides


def save_configuration(service, project: str, identity: str, body):
    """合成完整配置后校验原始处理，按同一修订原子保存。"""
    from ..stages import compose_configuration

    require_profile(service, project, identity)
    base = service.project(project)
    captured = task.read_configuration(base, identity)
    if captured["revision"] != body.revision:
        raise ValueError("configuration_revision_conflict")
    config = compose_configuration(
        captured["config"],
        "rawprep",
        body.rawprep,
        edited_paths=body.edited_paths,
        removed_paths=body.removed_paths,
    )
    task.validate_rawprep_configuration(base, identity, config["rawprep"], revision=body.revision)
    original_dataset = captured["config"].get("dataset") or {}
    dataset = config.setdefault("dataset", {})
    if "partitions" in original_dataset:
        dataset["partitions"] = deepcopy(original_dataset["partitions"])
    else:
        dataset.pop("partitions", None)
    dataset.pop("partition", None)
    if body.processed_name is not None:
        task.validate_processed_name(body.processed_name)
        dataset["processed_name"] = body.processed_name
    return task.replace_configuration(base, identity, config, revision=body.revision)
