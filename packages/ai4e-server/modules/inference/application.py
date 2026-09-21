"""推理用例：任务授权、公开批次操作和受控结果引用。"""

from pathlib import Path

import ai4e_task as task

from ..stages.application import _migrate_legacy_slices, _migrate_official_scripts
from ..visualization import register
from . import domain


def checkpoints(service, project: str, identity: str) -> dict:
    """列出任务训练检查点，同字节标签合并为一个候选。"""
    base = service.project(project)
    current = task.read_configuration(base, identity)
    unique = {}
    for candidate in task.list_inference_checkpoints(base, identity):
        key = candidate["revision"]
        if key in unique:
            unique[key].setdefault("aliases", []).append(candidate["name"])
        else:
            unique[key] = domain.checkpoint(candidate)
    return {
        "items": list(unique.values()),
        "device_options": task.inference_devices(base),
        "revision": current["revision"],
    }


def samples(service, project: str, identity: str, checkpoint_id: str) -> dict:
    """仅使用检查点对应准备中声明的分片样本。"""
    try:
        value = task.inference_samples(service.project(project), identity, checkpoint_id)
    except FileNotFoundError as exc:
        raise ValueError(
            "inference_preparation_missing: 检查点关联的准备或样本文件不存在，请确认数据准备仍可用"
        ) from exc
    result = {
        "partitions": value.get("partitions", {}),
        "selection_supported": value.get("selection_supported", True),
        "fields": value.get("fields", []),
        "metrics": value.get("metrics", []),
        "compatibility": value.get("compatibility"),
        "preparation": {k: (value.get("preparation") or {}).get(k) for k in ("digest", "revision")},
    }
    if "vtk_exports" in value:
        result["vtk_exports"] = value["vtk_exports"]
    return result


def check(service, project: str, identity: str, request: dict) -> dict:
    """预检不提交运行，也不修改任务版本。"""
    from ..capabilities.aero_cfd import require_profile

    require_profile(service, project, identity)
    _migrate_official_scripts(service, service.project(project), identity)
    captured = _migrate_legacy_slices(service, service.project(project), identity)
    request = {**request, "expected_revision": captured["revision"]}
    value = task.check_inference(service.project(project), identity, request)
    return {
        "request": value["request"],
        "total": value["total"],
        "checkpoints": [domain.checkpoint(c) for c in value["checkpoints"]],
        "device_options": value["device_options"],
    }


def submit(service, project: str, identity: str, request: dict) -> dict:
    """提交原生或已核验兼容脚本，未知脚本不通过页面猜测其含义。"""
    from ..capabilities.aero_cfd import require_profile

    require_profile(service, project, identity)
    _migrate_official_scripts(service, service.project(project), identity)
    captured = _migrate_legacy_slices(service, service.project(project), identity)
    request = {**request, "expected_revision": captured["revision"]}
    return domain.batch(task.submit_inference(service.project(project), identity, request))


def batches(service, project: str, identity: str) -> dict:
    """读取可跨刷新恢复的任务批次列表。"""
    return {
        "items": [
            domain.batch(v) for v in task.list_inference_batches(service.project(project), identity)
        ]
    }


def get_batch(service, project: str, identity: str, batch_id: str) -> dict:
    """读取指定批次进度。"""
    return domain.batch(task.read_inference_batch(service.project(project), identity, batch_id))


def action(
    service, project: str, identity: str, batch_id: str, operation: str, key: str | None = None
) -> dict:
    """显式取消、恢复或重试；操作对象始终属于当前任务。"""
    handlers = {
        "cancel": task.cancel_inference,
        "recover": task.recover_inference,
        "retry": task.retry_inference,
    }
    if operation not in handlers:
        raise ValueError("unsupported_inference_action")
    args = {"idempotency_key": key} if operation == "retry" else {}
    return domain.batch(handlers[operation](service.project(project), identity, batch_id, **args))


def results(service, project: str, identity: str, batch_id: str) -> dict:
    """把已提交文件登记为固定资产，供下载和同一 Trame 工作台消费。"""
    base = Path(service.project(project)).resolve()
    value = task.inference_results(base, identity, batch_id)
    items = []
    for row in value["items"]:
        files = []
        for source in row["files"]:
            path = Path(source["path"]).resolve()
            if not path.is_relative_to(base):
                raise ValueError("inference_result_outside_project")
            relative = str(path.relative_to(base))
            ref = register(service, project, "project", relative, identity)
            files.append(
                {
                    "name": source["name"],
                    "size": source["size"],
                    "root": "project",
                    "path": relative,
                    "task_id": identity,
                    "ref": ref,
                }
            )
        items.append({**row, "files": files})
    return {
        "items": items,
        "comparison": value["comparison"],
        "records": value.get("records", []),
        "statistics": value.get("statistics", []),
        "batch": value.get("batch"),
    }


def export(service, project: str, identity: str, batch_id: str, request: dict) -> dict:
    """导出固定指标并登记为受控文件，不运行模型。"""
    base = Path(service.project(project)).resolve()
    value = task.export_inference(base, identity, batch_id, request)
    path = Path(value["path"]).resolve()
    if not path.is_relative_to(base):
        raise ValueError("inference_result_outside_project")
    relative = str(path.relative_to(base))
    return {
        "name": value["name"],
        "root": "project",
        "path": relative,
        "task_id": identity,
        "ref": register(service, project, "project", relative, identity),
    }
