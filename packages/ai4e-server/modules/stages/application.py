"""阶段用例：捕获配置、检查受控输入并编排 task 公开操作。"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from subprocess import TimeoutExpired
from uuid import uuid4

import ai4e_task as task

from ..visualization import asset, register, submit_model_inspection
from .domain import (
    ALLOWED_BINDINGS,
    CHECKPOINT_TAGS,
    MODEL_REPLACEMENT_SECTIONS,
    OperationCommand,
    execution_stages,
    field_matching_catalog,
    reject_statistics,
    required_inputs,
    selected_input_keys,
    split_catalog,
    validate_field_bindings,
    validate_split,
    validate_stage,
)


def _read_manifest(config):
    """读取已绑定物理清单 JSON，路径无效时退回配置声明。"""
    path = (config.get("train") or {}).get("manifest")
    if not isinstance(path, str) or not path:
        return None
    file = Path(path)
    if not file.is_file():
        return None
    try:
        return json.loads(file.read_text())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def configuration(project: str, identity: str, service, stage: str | None = None):
    """读取任务 YAML 中的用户配置，不建立第二份配置。"""
    value = task.read_configuration(service.project(project), identity)
    if stage:
        validate_stage(stage)
        try:
            described = task.inspect_task(
                service.project(project),
                identity,
                "describe_case",
                revision=value["revision"],
                output_dir=str(service.settings.root / "inspections" / uuid4().hex),
            )
        except (ValueError, OSError, TimeoutExpired) as exc:
            logging.getLogger(__name__).warning("任务能力检查失败 task=%s", identity, exc_info=True)
            described = {
                "capabilities": {
                    "unavailable_reason": (
                        "当前配置或数据输入尚未就绪，请核对数据绑定后重新检查。"
                        if any(
                            marker in str(exc)
                            for marker in ("TypeError", "AttributeError", "NoneType", "Traceback")
                        )
                        else str(exc).splitlines()[-1][:600]
                    ),
                    "status": "unavailable",
                }
            }
        full_config = described.get("configuration") or value["config"]
        capabilities = _capability_options(described)
        if stage == "trainprep":
            manifest = _read_manifest(full_config)
            capabilities["field_matching"] = field_matching_catalog(full_config, manifest)
            capabilities["split"] = split_catalog(manifest)
        return {
            "task_id": identity,
            "revision": value["revision"],
            "stage": stage,
            "values": full_config.get(stage, {}),
            "capabilities": capabilities,
            "readiness": {"status": "unchecked"},
        }
    return dict(task_id=identity, **value)


def save(
    project: str,
    identity: str,
    stage: str,
    values: dict,
    revision: str,
    service,
    bindings: dict | None = None,
    target_case_id: str | None = None,
    target_model: str | None = None,
    target_variant: str | None = None,
    target_preset: str | None = None,
):
    """核对修订保存阶段草稿；显式换模同时替换关联默认值并解除旧输入。"""
    validate_stage(stage)
    reject_statistics(values)
    from copy import deepcopy

    if stage == "trainprep":
        current = task.read_configuration(service.project(project), identity)
        merged = {**current["config"], "trainprep": values}
        manifest = _read_manifest(merged)
        matching = field_matching_catalog(merged, manifest)
        validate_field_bindings(values, matching["model_roles"], matching["dataset_fields"])
        validate_split(values, manifest)
    patch = {stage: deepcopy(values)}
    replacements = ()
    switching = any(item is not None for item in (target_case_id, target_model, target_preset))
    if switching:
        if stage != "model":
            raise ValueError("model_case_requires_model_stage")
        current = task.read_configuration(service.project(project), identity)
        if current["revision"] != revision:
            raise ValueError("configuration_revision_conflict")
        target = _switch_target(
            service, project, identity, current, target_case_id, target_model, target_variant, target_preset
        )
        train = deepcopy(target["train"])
        # 不把案例默认物理清单路径带入用户任务；即便未绑定也明确保持空引用。
        train["manifest"] = current["config"].get("train", {}).get("manifest")
        train.pop("preparation", None)
        train["resume"] = None
        patch.update(
            {
                "train": train,
                "trainprep": deepcopy(target["trainprep"]),
                "components": {"model": target["component"]},
                "post": {"checkpoint": "last"},
            }
        )
        patch["model"].pop("initial_weights", None)
        if "initial_weights" in target["model"]:
            patch["model"]["initial_weights"] = target["model"]["initial_weights"]
        replacements = MODEL_REPLACEMENT_SECTIONS
    for key, reference in (bindings or {}).items():
        if key not in ALLOWED_BINDINGS:
            raise ValueError("unsupported_stage_binding")
        if switching and key != "train.manifest":
            # 换模不能在同一命令中把刚解除的旧准备或权重重新写回。
            if reference is not None:
                raise ValueError("model_switch_requires_new_preparation")
            continue
        resolved = None if reference is None else str(asset(service, project, reference))
        section = patch
        parts = key.split(".")
        for part in parts[:-1]:
            section = section.setdefault(part, {})
            if not isinstance(section, dict):
                raise ValueError("invalid_stage_binding_structure: " + key)  # noqa: TRY004 - 统一配置业务错误
        section[parts[-1]] = resolved
    return task.save_configuration(
        service.project(project),
        identity,
        patch,
        revision=revision,
        replace_sections=replacements,
    )


def _switch_target(
    service,
    project,
    identity,
    current,
    target_case_id,
    target_model,
    target_variant,
    target_preset,
):
    """按官方模型、变体或用户预设解析换模目标。"""
    from ..capabilities import describe_model_case, describe_official_model, load_preset
    from ..capabilities.model_cases import dataset_id

    if target_preset:
        return load_preset(service, project, identity, target_preset, current)
    if target_model:
        return describe_official_model(
            service, project, identity, target_model, current, target_variant
        )
    if target_case_id:
        from ..capabilities.model_cases import CASES, resolve_case

        if target_case_id in CASES:
            return describe_model_case(service, project, identity, target_case_id, current)
        kind = dataset_id(current["config"])
        resolved = resolve_case(kind, target_case_id)
        if resolved:
            return describe_model_case(service, project, identity, resolved, current)
        raise ValueError("unknown_registered_case")
    raise ValueError("model_switch_target_required")


def capabilities(project: str, identity: str, service):
    """在 task 检查进程查询实际案例能力。"""
    value = task.read_configuration(service.project(project), identity)
    described = task.inspect_task(
        service.project(project),
        identity,
        "describe_case",
        revision=value["revision"],
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
    )

    described["capabilities"] = _capability_options(described)
    return described


def _capability_options(described):
    """把生产者声明的枚举范围适配为前端选项；未知范围不擅自扩大。"""
    capabilities = dict(described.get("capabilities", {}))
    options = {}
    for key, descriptor in capabilities.get("parameter_descriptors", {}).items():
        allowed = descriptor.get("allowed")
        if allowed is not None:
            options[key] = allowed
    for key, constraint in capabilities.get("training_constraints", {}).items():
        if "allowed" in constraint:
            options[key] = constraint["allowed"]
    train = described.get("configuration", {}).get("train", {})
    for key in (
        "optimizer",
        "precision",
        "device",
        "scheduler",
        "scheduler_unit",
        "parameter_group_policy",
        "evaluation_split",
    ):
        if key not in options and key in train:
            options[key] = [train[key]]
    capabilities["training_options"] = options
    return capabilities


def model_inspection(project: str, identity: str, body: OperationCommand, service):
    """跟踪任务真实模型；来源由后台解析，不回写任务绑定。"""
    captured = task.read_configuration(service.project(project), identity)
    if captured["revision"] != body.expected_revision:
        raise ValueError("configuration_revision_conflict")
    selection, inputs = _trace_selection(service, project, identity)
    return submit_model_inspection(
        service,
        project,
        identity,
        body.expected_revision,
        selection,
        inputs,
        body.idempotency_key,
    )


def _trace_selection(service, project, identity):
    """把最近可用物理来源登记为当次检查输入。"""
    from ...infrastructure.content_access import roots
    from ..capabilities.trace_source import latest_trace_source

    source = latest_trace_source(service, project, identity)
    bindings = {}
    inputs = []
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    for key, location in source.items():
        path = Path(location).resolve()
        root_id = next(
            (name for name, root in visible.items() if path.is_relative_to(root)),
            None,
        )
        if root_id is None:
            raise ValueError("请先完成原始处理后再生成真实模型结构")
        ref = register(service, project, root_id, str(path.relative_to(visible[root_id])), identity)
        bindings[key] = str(path)
        inputs.append(ref)
    return {"stage": "model", "bindings": bindings}, inputs


def _inspect(project, identity, body, service, operation):
    selection = _inspection_selection(service, project, body)
    return submit_model_inspection(
        service,
        project,
        identity,
        body.expected_revision,
        selection,
        body.inputs,
        body.idempotency_key,
        operation=operation,
    )


def _inspection_selection(service, project, body):
    selection = dict(body.selection)
    binding_paths = {}
    for key, source in selection.get("bindings", {}).items():
        if (
            key
            not in {
                "train.manifest",
                "train.preparation",
                "post.checkpoint",
                "trainprep.normalization.statistics",
            }
            or source not in body.inputs
        ):
            raise ValueError("invalid_inspection_binding")
        binding_paths[key] = str(asset(service, project, source))
    selection["bindings"] = binding_paths
    return selection


def operation(project: str, identity: str, stage: str, body: OperationCommand, service):
    """检查不创建运行；正式提交复用 task 捕获与幂等机制。"""
    validate_stage(stage)
    base = service.project(project)
    captured = task.read_configuration(base, identity)
    if captured["revision"] != body.expected_revision:
        raise ValueError("configuration_revision_conflict")
    if task.get_task(base, identity).get("archived") or task.open_project(base).get("archived"):
        raise ValueError("archived")
    for source in body.inputs:
        asset(service, project, source)
    if body.mode == "check":
        body.selection["stage"] = stage
        return _inspect(project, identity, body, service, "validate_configuration")
    stages = execution_stages(stage, body.mode, body.selection)
    overrides = ["pipeline.stages=" + json.dumps(stages)]
    # 固定所有配置值以免保存和提交竞争。阶段列表仅由服务决定。
    overrides += [
        key + "=" + json.dumps(value)
        for key, value in captured["config"].items()
        if key != "pipeline"
    ]
    bindings = body.selection.get("bindings", {})
    if set(bindings) - ALLOWED_BINDINGS:
        raise ValueError("unsupported_stage_binding")
    for key, source in bindings.items():
        if source not in body.inputs:
            raise ValueError("binding_requires_fixed_input")
        overrides.append(key + "=" + json.dumps(str(asset(service, project, source))))
    if "samples" in body.selection:
        overrides.append("dataset.samples=" + json.dumps(body.selection["samples"]))
    required_bindings = required_inputs(stage, stages)
    if stage == "post" and (
        "post.results" in bindings or captured["config"].get("post", {}).get("results")
    ):
        required_bindings = ["post.results"]
    for key in required_bindings:
        section, member = key.split(".")
        if key not in bindings and not captured["config"].get(section, {}).get(member):
            raise ValueError("stage_input_required: " + key)
    for source in body.inputs:
        asset(service, project, source)
    declared = task.get_task(base, identity).get("entry", {}).get("inputs", {})
    result = task.submit_run(
        base,
        identity,
        overrides=overrides,
        idempotency_key=body.idempotency_key,
        expected_revision=body.expected_revision,
        operation_mode=body.mode,
        input_keys=selected_input_keys(stages, declared),
    )
    service.store.put(
        "run_mode",
        result["id"],
        {
            "project_id": project,
            "run_id": result["id"],
            "mode": body.mode,
            "stage": stage,
            "revision": body.expected_revision,
            "inputs": body.inputs,
        },
    )
    return dict(**result, mode=body.mode, stage=stage)


def stage_inputs(project: str, identity: str, service):
    """列出正式产物与配置固定来源；失效来源保留位置，不泄露绝对路径。"""
    from pathlib import Path

    from omegaconf import OmegaConf
    from omegaconf.errors import OmegaConfBaseException

    from ...infrastructure.content_access import roots

    base = service.project(project)
    configuration = OmegaConf.create(task.read_configuration(base, identity)["config"])
    task_record = task.get_task(base, identity)
    recipe = Path(task_record["directory"]) / "recipe"
    config_dir = (recipe / task_record.get("entry", {}).get("config", "config.yaml")).parent
    declared = {}
    invalid = {}
    for binding in sorted(ALLOWED_BINDINGS):
        try:
            value = OmegaConf.select(configuration, binding)
            if value is None or value == "":
                continue
            if not isinstance(value, str):
                invalid[binding] = "invalid_binding_path"
                continue
            if binding in {"post.checkpoint", "infer.checkpoint"} and value in CHECKPOINT_TAGS:
                continue
            declared[binding] = (config_dir / Path(value).expanduser()).resolve()
        except (ValueError, TypeError, OmegaConfBaseException):
            invalid[binding] = "binding_resolution_failed"
    visible = {name: root.resolve() for name, root in roots(service, project, identity).items()}
    result = []
    found = set()
    covered = set()
    from ..datasets.application import as_stage_inputs, harvest

    harvest(service)
    for item in as_stage_inputs(service, project, identity):
        path = None
        if item.get("ref"):
            try:
                from ..visualization import asset as resolve_asset

                path = resolve_asset(service, project, item["ref"])
            except (ValueError, FileNotFoundError, KeyError):
                path = None
        selected = bool(path and declared.get("train.manifest") == Path(path).resolve())
        if selected:
            found.add("train.manifest")
        if item.get("ref"):
            covered.add(item["ref"]["asset_id"])
        result.append({**item, "selected": selected})
    for item in task.list_stage_artifacts(base, identity, visible):
        root_id = item.get("root", "project")
        root = visible.get(root_id, Path(base).resolve())
        ref = register(service, project, root_id, item["path"], identity)
        if item["binding"] == "train.manifest" and ref["asset_id"] in covered:
            if declared.get(item["binding"]) == (root / item["path"]).resolve():
                found.add(item["binding"])
            continue
        selected = declared.get(item["binding"]) == (root / item["path"]).resolve()
        if selected:
            found.add(item["binding"])
        if item["binding"] == "train.manifest":
            covered.add(ref["asset_id"])
        result.append(
            {
                "binding": item["binding"],
                "run_id": item["run_id"],
                "name": item["name"],
                "selected": selected,
                "origin": "run",
                "compatibility": {"status": "unchecked", "reason": "requires_configuration_check"},
                "ref": ref,
            }
        )
    for binding, path in declared.items():
        if binding in found:
            continue
        locations = [(name, root) for name, root in visible.items() if path.is_relative_to(root)]
        if not locations:
            if not path.is_file():
                continue
            invalid[binding] = "path_outside_root"
            continue
        if not path.is_file():
            invalid[binding] = "binding_file_missing"
            continue
        root_id, root = locations[0]
        try:
            ref = register(service, project, root_id, str(path.relative_to(root)), identity)
        except (ValueError, FileNotFoundError):
            invalid[binding] = "binding_source_unavailable"
            continue
        if binding == "train.manifest" and ref["asset_id"] in covered:
            found.add(binding)
            continue
        result.append(
            {
                "binding": binding,
                "run_id": None,
                "name": path.name,
                "selected": True,
                "origin": "configuration",
                "ref": ref,
                "compatibility": {"status": "unchecked", "reason": "requires_configuration_check"},
            }
        )
    for binding, reason in invalid.items():
        result.append(
            {
                "binding": binding,
                "run_id": None,
                "name": "已绑定来源不可用",
                "selected": False,
                "origin": "configuration",
                "ref": None,
                "compatibility": {"status": "invalid", "reason": reason, "location": binding},
            }
        )
    return result


def stage_summary(project: str, identity: str, service):
    """将研究事实与辅助检查关联；过期检查不改写历史操作终态。"""
    value = task.read_configuration(service.project(project), identity)
    result = task.get_stage_summary(service.project(project), identity)
    result.update(
        {stage: {"status": "unchecked", "operation_id": None} for stage in ("model", "training")}
    )
    for operation in sorted(
        service.store.list("operation"), key=lambda item: item.get("created_at", "")
    ):
        if operation.get("project_id") != project or operation.get("task_id") != identity:
            continue
        if operation.get("kind") not in {"trace_model", "validate_configuration"}:
            continue
        stage = operation.get("stage")
        if stage == "train":
            stage = "training"
        if stage not in result:
            continue
        status = operation["status"]
        reason = None
        if operation.get("revision") != value["revision"]:
            status, reason = "stale", "configuration_revision_changed"
        else:
            try:
                for ref in operation.get("inputs", []):
                    asset(service, project, ref)
            except (ValueError, KeyError, FileNotFoundError):
                status, reason = "stale", "input_revision_changed"
        check = {
            "status": status,
            "operation_id": operation["operation_id"],
            "reason": reason,
            "revision": operation.get("revision"),
        }
        if stage in {"model", "training"}:
            result[stage] = check
        else:
            result[stage]["check"] = check
    return {"task_id": identity, "revision": value["revision"], "stages": result}


def _stage_allowed(directory: Path, role: str):
    """阶段允许出现的路径；输入只取清单声明，准备和后处理按层过滤。"""
    if role == "inputs":
        manifest = directory / "manifest.json"
        content = json.loads(manifest.read_text())
        paths = [manifest]
        for sample in content.get("samples", []):
            sample_dir = Path(sample["path"])
            if not sample_dir.is_absolute():
                sample_dir = directory / sample_dir
            if not sample_dir.resolve().is_relative_to(directory.resolve()):
                raise ValueError("path_outside_root")
            for member in [
                *sample.get("filemap", {}).values(),
                *sample.get("assets", []),
                *sample.get("identity_assets", []),
            ]:
                path = sample_dir / member
                if not path.resolve().is_relative_to(sample_dir.resolve()):
                    raise ValueError("path_outside_root")
                paths.append(path)
        return paths
    return None


def _stage_row(path, directory, root, root_id, role, run_id, is_dir):
    stat = path.stat()
    return {
        "name": path.name,
        "path": "" if path == directory else str(path.relative_to(directory)),
        "root": root_id,
        "source_path": str(path.relative_to(root)),
        "directory": is_dir,
        "run_id": run_id,
        "role": role,
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
    }


def _hidden(path, directory):
    return path.is_symlink() or any(
        part.startswith(".") for part in path.relative_to(directory).parts
    )


def stage_files(
    project: str,
    identity: str,
    service,
    role: str,
    run_id: str | None = None,
    asset_id: str | None = None,
    revision: str | None = None,
    path: str = "",
    query: str = "",
):
    """按层列出指定正式运行交付范围；无选择返回空，不回退项目目录，不登记资产。"""
    from pathlib import Path

    from ...infrastructure.content_access import roots

    if role not in {"inputs", "preparation", "post"}:
        raise ValueError("unsupported_stage_file_role")
    base = service.project(project)
    task.get_task(base, identity)
    root = Path(base).resolve()
    if asset_id:
        if role not in {"inputs", "preparation"} or not revision:
            raise ValueError("fixed_stage_asset_required")
        source = asset(
            service, project, {"project_id": project, "asset_id": asset_id, "revision": revision}
        )
        expected = "manifest.json" if role == "inputs" else "preparation.json"
        if source.name != expected or not source.is_file():
            raise ValueError("stage_asset_kind_mismatch")
        directory = source.parent
    else:
        if not run_id:
            return []
        run = task.get_run(base, run_id)
        if run.get("task_id") != identity:
            raise ValueError("run_task_mismatch")
        if run.get("operation_mode", "execute") != "execute":
            raise ValueError("formal_run_required")
        if role == "inputs":
            directory = Path(run["data_dir"])
            if not (directory / "manifest.json").is_file():
                return []
        elif role == "preparation":
            directory = Path(run["run_dir"]) / "artifacts"
            if not (directory / "preparation.json").is_file():
                return []
        else:
            if "post" not in run.get("stages", []):
                return []
            directory = Path(run["run_dir"])
    root_id = "project"
    if not directory.resolve().is_relative_to(root):
        matches = [
            (name, location)
            for name, location in roots(service, project, identity).items()
            if directory.resolve().is_relative_to(location.resolve())
        ]
        if not matches:
            raise ValueError("path_outside_root")
        root_id, root = matches[0]
        root = root.resolve()
    current = (path or "").strip("/")
    current_dir = directory / current if current else directory
    if current and (
        not current_dir.resolve().is_relative_to(directory.resolve()) or current_dir.is_symlink()
    ):
        raise ValueError("path_outside_root")
    if current and current_dir.suffix == ".zarr":
        return []
    allowed = _stage_allowed(directory, role)
    result = {}
    query = (query or "").strip()

    def accept(target, is_dir):
        if _hidden(target, directory) or (
            any(part.endswith(".zarr") for part in target.relative_to(directory).parts[:-1])
        ):
            return
        if role == "preparation" and not is_dir and target.name != "preparation.json" and (
            "normaliz" not in target.name
        ):
            return
        if role == "post":
            parts = target.relative_to(directory).parts
            if parts and parts[0] not in {"artifacts", "predictions", "meshes", "post"}:
                return
        rel = "" if target == directory else str(target.relative_to(directory))
        if query:
            if is_dir or (
                query.casefold() not in target.name.casefold()
                and query.casefold() not in rel.casefold()
            ):
                return
        result[str(target)] = _stage_row(target, directory, root, root_id, role, run_id, is_dir)

    if allowed is not None:
        for target in sorted(set(allowed), key=lambda item: str(item)):
            if not target.exists():
                continue
            is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
            if query:
                if is_leaf:
                    accept(target, False)
                continue
            try:
                rest = target.relative_to(current_dir)
            except ValueError:
                continue
            parts = rest.parts
            if not parts:
                continue
            if len(parts) == 1:
                accept(target, not is_leaf)
            else:
                child = current_dir / parts[0]
                accept(child, child.is_dir() and child.suffix != ".zarr")
        return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))

    if query:
        for target in current_dir.rglob("*"):
            is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
            if is_leaf:
                accept(target, False)
        return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))
    if not current_dir.is_dir():
        return []
    for target in sorted(current_dir.iterdir(), key=lambda item: (not item.is_dir(), item.name)):
        is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
        accept(target, not is_leaf)
    return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))
