"""任务和运行的查询、进程核对及离线导入。"""

from pathlib import Path

from ..storage.artifacts import read_run
from ..storage.database import transaction
from ..storage.records import get, put
from ..storage.snapshots import digest, inventory


def read_log(project: str | Path, run_id: str) -> str:
    """读取 core 日志，尚未创建时返回空文本。"""
    value = get_run(project, run_id)
    path = Path(value["run_dir"]) / "logs/run.log"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def import_run(project: str | Path, directory, *, task_id: str | None = None) -> dict:
    """只读导入；相同 ID 内容冲突拒绝覆盖，旧产物不猜测版本。"""
    directory = Path(directory).resolve()
    artifacts = read_run(directory)
    if "summary" not in artifacts:
        raise ValueError("incomplete_run")
    lineage = artifacts.get("lineage", {})
    identity = lineage.get("run_id") or digest(str(directory))
    version = lineage.get("version_id")
    owner = lineage.get("task_id") or task_id
    if task_id and lineage.get("task_id") and task_id != lineage["task_id"]:
        raise ValueError("run_task_mismatch")
    content = digest(inventory(directory))
    with transaction(project) as db:
        if owner:
            try:
                task = get(db, "task", owner)
            except KeyError:
                task = None
            if task and version and task["version_id"] != version:
                raise ValueError("run_version_conflict")
        if version:
            try:
                existing = get(db, "version", version)
            except KeyError:
                existing = None
            if existing and existing != lineage.get("version"):
                raise ValueError("version_content_conflict")
        try:
            old = get(db, "run", identity)
        except KeyError:
            old = None
        if old:
            old_dir = Path(old.get("external_dir") or Path(project) / old["run_path"])
            if (old.get("content_digest") or digest(inventory(old_dir))) != content:
                raise ValueError("run_content_conflict")
            return old
        value = {
            "id": identity,
            "task_id": owner,
            "version_id": version,
            "status": "failed" if artifacts["summary"].get("failed", True) else "succeeded",
            "external_dir": str(directory),
            "run_path": "",
            "data_path": "",
            "content_digest": content,
            "origin": "imported" if version else "unknown",
        }
        put(db, "run", value)
    return value


def get_stage_summary(project: str | Path, task_id: str) -> dict:
    """按正式运行事实汇总阶段；已成功不被后来的 unknown 读盘盖成未运行。"""
    get_task(project, task_id)
    from ..templates.materialize import recipe_entry

    entry = recipe_entry(project, task_id)
    result = {stage: {"status": "not_run", "run_id": None} for stage in entry.get("stages", [])}
    runs = sorted(
        (
            run
            for run in list_runs(project, task_id)
            if run.get("operation_mode", "execute") == "execute"
        ),
        key=lambda item: item.get("created_at") or "",
    )
    for run in runs:
        stages = run.get("stages", [])
        if run.get("metadata", {}).get("purpose") == "inference":
            stages = ["infer"]
        for stage in stages:
            result.setdefault(stage, {"status": "not_run", "run_id": None})
            status = run["status"]
            summary = run.get("summary", {})
            if summary.get("dry_run") or summary.get("research_status") == "unavailable":
                continue
            events = [item for item in summary.get("stage_events", []) if item["stage"] == stage]
            if events:
                status = (
                    "failed"
                    if any(item["status"] == "failed" for item in events)
                    else events[-1]["status"]
                )
            elif summary.get("research_status") in {"completed", "incomplete", "failed"}:
                status = "unknown"
            # 多阶段失败的历史摘要不含逐阶段终态；不能由报告存在推测成功。
            if not events and status != "succeeded" and len(stages) > 1:
                status = "unknown"
            previous = result[stage]
            if status == "unknown" and previous.get("status") == "succeeded":
                continue
            result[stage] = {"status": status, "run_id": run["id"], "mode": "execute"}
    # 批次是推理完成的权威事实；一个成功分片不能掩盖其他分片失败。
    from .inference import list_inference_batches

    batches = list_inference_batches(project, task_id)
    if batches:
        batch = batches[0]
        previous = result.get("infer", {})
        if not (batch.get("status") == "unknown" and previous.get("status") == "succeeded"):
            children = batch.get("children", [])
            result["infer"] = {
                "status": batch["status"],
                "batch_id": batch["id"],
                "run_id": children[-1].get("run_id") if children else None,
                "mode": "execute",
                "completed": batch.get("completed", 0),
                "total": batch.get("total", 0),
            }
    from omegaconf import OmegaConf

    from ..storage.shared_datasets import resolve_reference
    from .configuration import read_configuration

    config = OmegaConf.create(read_configuration(project, task_id)["config"])
    for declaration in entry.get("shared_outputs", {}).values():
        selected = OmegaConf.select(config, declaration["consumer_binding"])
        match = resolve_reference(project, Path(selected)) if selected else None
        if match:
            result.setdefault(declaration["stage"], {"status": "not_run", "run_id": None})[
                "shared_input"
            ] = {"name": match["name"], "status": match["status"], "asset_id": match["id"]}
    return result


from .records import get_run, get_task, list_runs, list_tasks

__all__ = [
    "get_run",
    "get_stage_summary",
    "get_task",
    "import_run",
    "list_runs",
    "list_tasks",
    "read_log",
]
