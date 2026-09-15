"""调用任务公开门面，校验完整文件选择并使用既有覆盖参数运行。"""

import json
from pathlib import Path

import ai4e_task as task

from ...infrastructure.content_access import resolve, revision, roots
from ..capabilities.aero_cfd import require_profile
from ..tasks import read_binding
from .domain import validate


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
        from ..datasets.application import check_name

        check_name(service, name, {**cfg["config"], "rawprep": resolved["rawprep"]})
    if body.sample_scope is not None:
        return _sample_preflight(service, project, identity, body)

    return _generic_preflight(service, project, identity, body)


def submit(service, project, identity, body, *, mode="execute"):
    """原样执行 pipeline.py，只覆盖原数据处理阶段和选择。"""
    info = preflight(service, project, identity, body, mode=mode)
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
        "dataset.root=" + json.dumps(info["root"]),
        "dataset.samples=" + json.dumps(info.get("sample_selection", info["samples"])),
    ]
    # 固定本次核对的配置值，保存操作不会改变正在提交的原始处理设置。
    overrides += [
        key + "=" + json.dumps(value)
        for key, value in fixed["config"].items()
        if key not in {"pipeline", "dataset"}
    ]
    for key, value in fixed["config"].get("dataset", {}).items():
        if key not in {"root", "samples"}:
            overrides.append("dataset." + key + "=" + json.dumps(value))
    for name, digest in info["digests"].items():
        if revision(_selected_path(service, project, identity, body.root, name)) != digest:
            raise ValueError("file_changed_before_submission: " + name)
    result = task.submit_run(
        service.project(project),
        identity,
        overrides=overrides,
        idempotency_key=body.idempotency_key,
        expected_revision=body.revision,
        operation_mode=mode,
        input_keys=[
            key
            for key in task.get_task(service.project(project), identity)
            .get("entry", {})
            .get("inputs", {})
            if key.startswith("dataset.")
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


def _sample_catalog(service, project, identity, body, *, public=False, full=False):
    """新样本入口只传范围；组件交付完整依赖，服务限定受控访问。"""
    from uuid import uuid4
    from ..tasks import controlled_reference
    from ..visualization.application import register

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
    for source in result["sources"]:
        path = Path(source["path"]).resolve()
        if source.get("exists", True):
            ref = controlled_reference(service, project, path)
            source["relative_path"] = ref["root"] + "::" + ref["path"]
            source["asset_ref"] = register(service, project, ref["root"], ref["path"], identity)
        if public:
            source.pop("path", None)
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
