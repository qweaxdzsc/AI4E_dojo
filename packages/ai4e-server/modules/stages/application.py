"""阶段用例：捕获配置、检查受控输入并编排 task 公开操作。"""

import json
from subprocess import TimeoutExpired
from uuid import uuid4

import ai4e_task as task

from ..visualization import asset, register, submit_model_inspection
from .domain import (
    ALLOWED_BINDINGS,
    OperationCommand,
    execution_stages,
    reject_statistics,
    required_inputs,
    selected_input_keys,
    validate_stage,
)


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
            described = {"capabilities": {"unavailable_reason": str(exc).splitlines()[-1][:600]}}
        return {
            "task_id": identity,
            "revision": value["revision"],
            "stage": stage,
            "values": described.get("configuration", value["config"]).get(stage, {}),
            "capabilities": described.get("capabilities", {}),
            "readiness": {"status": "unchecked"},
        }
    return dict(task_id=identity, **value)


def save(project: str, identity: str, stage: str, values: dict, revision: str, service):
    """核对修订保存单段配置，统计量不能通过服务写入。"""
    validate_stage(stage)
    reject_statistics(values)
    return task.save_configuration(
        service.project(project),
        identity,
        {stage: values},
        revision=revision,
    )


def capabilities(project: str, identity: str, service):
    """在 task 检查进程查询实际案例能力。"""
    value = task.read_configuration(service.project(project), identity)
    return task.inspect_task(
        service.project(project),
        identity,
        "describe_case",
        revision=value["revision"],
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
    )


def model_inspection(project: str, identity: str, body: OperationCommand, service):
    """跟踪任务真实模型；结果保留配置修订。"""
    captured = task.read_configuration(service.project(project), identity)
    if captured["revision"] != body.expected_revision:
        raise ValueError("configuration_revision_conflict")
    selection = _inspection_selection(service, project, body)
    return submit_model_inspection(
        service,
        project,
        identity,
        body.expected_revision,
        selection,
        body.inputs,
        body.idempotency_key,
    )


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
    """查询正式运行的固定交接资产；试跑不进入候选列表。"""
    return [
        {
            "binding": item["binding"],
            "run_id": item["run_id"],
            "name": item["name"],
            "ref": register(service, project, "project", item["path"], identity),
        }
        for item in task.list_stage_artifacts(service.project(project), identity)
    ]
