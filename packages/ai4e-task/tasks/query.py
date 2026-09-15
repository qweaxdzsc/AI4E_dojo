"""任务和运行的查询、进程核对及离线导入。"""

from pathlib import Path

from ..storage.artifacts import read_run
from ..storage.database import transaction
from ..storage.files import read_json
from ..storage.records import fetch, get, listing, put
from ..storage.snapshots import digest, inventory
from .local import alive


def get_task(project: str | Path, task_id: str) -> dict:
    """读取任务身份及当前代码目录。"""
    result = fetch(project, "task", task_id)
    return {**result, "directory": str(Path(project).resolve() / "tasks" / task_id)}


def list_tasks(project: str | Path) -> list[dict]:
    """按创建顺序列出任务。"""
    return listing(project, "task")


def get_run(project: str | Path, run_id: str) -> dict:
    """核对持久化收据与 core 产物；未知状态不会自动重新启动。"""
    root = Path(project).resolve()
    value = fetch(root, "run", run_id)
    observed_status = value["status"]
    directory = Path(value.get("external_dir") or root / value["run_path"])
    artifacts = read_run(directory)
    if value.get("request_path"):
        request = root / value["request_path"]
        started = request.parent / "started.json"
        if started.exists():
            receipt = read_json(started)
            if receipt.get("run_id") != run_id:
                raise ValueError("run_receipt_mismatch")
            value["pid"] = receipt["pid"]
        finished = request.parent / "finished.json"
        if finished.exists():
            artifacts = read_run(directory)
            receipt = read_json(finished)
            if receipt["run_id"] != run_id:
                raise ValueError("run_receipt_mismatch")
            value.update(status=receipt["status"], error=receipt.get("error"))
            if value["status"] == "succeeded" and (
                artifacts.get("summary", {}).get("failed", True)
                or artifacts.get("lineage", {}).get("run_id") != run_id
            ):
                value.update(status="failed", error="missing_or_invalid_completion")
        elif value["status"] not in {"failed", "queued"} and not value.get("canceled_before_start"):
            if alive(value.get("pid"), request):
                value["status"] = (
                    "stopping" if (request.parent / "stop.json").exists() else "running"
                )
            else:
                value["status"] = "unknown"
        if value["status"] == "stopped" and alive(value.get("pid"), request):
            value["status"] = "stopping"
        with transaction(root) as db:
            latest = get(db, "run", run_id)
            if latest["status"] != observed_status and not finished.exists():
                # 读取收据期间发生了启动或排队取消，旧查询不得覆盖新意图。
                value = latest
            if value.get("pid") is None and latest.get("pid") is not None:
                value["pid"] = latest["pid"]
            put(db, "run", value, replace=True)
    return {
        **value,
        "run_dir": str(directory),
        "data_dir": str(root / value.get("data_path", ".")),
        **artifacts,
    }


def list_runs(project: str | Path, task_id: str | None = None) -> list[dict]:
    """列出某任务或项目的全部运行。"""
    return [
        get_run(project, r["id"])
        for r in listing(project, "run")
        if task_id is None or r["task_id"] == task_id
    ]


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
    """按正式运行事实汇总阶段；多阶段失败不推测每一步均成功。"""
    get_task(project, task_id)
    result = {
        stage: {"status": "not_run", "run_id": None}
        for stage in ("rawprep", "trainprep", "train", "infer", "post")
    }
    for run in list_runs(project, task_id):
        if run.get("operation_mode", "execute") != "execute":
            continue
        stages = run.get("stages", [])
        if run.get("metadata", {}).get("purpose") == "inference":
            stages = ["infer"]
        for stage in stages:
            if stage not in result:
                continue
            status = run["status"]
            # 多阶段失败的历史摘要不含逐阶段终态；不能由报告存在推测成功。
            if status != "succeeded" and len(stages) > 1:
                status = "unknown"
            result[stage] = {"status": status, "run_id": run["id"], "mode": "execute"}
    # 批次是推理完成的权威事实；一个成功分片不能掩盖其他分片失败。
    from .inference import list_inference_batches

    batches = list_inference_batches(project, task_id)
    if batches:
        batch = batches[0]
        children = batch.get("children", [])
        result["infer"] = {"status": batch["status"], "batch_id": batch["id"],
                           "run_id": children[-1].get("run_id") if children else None,
                           "mode": "execute", "completed": batch.get("completed", 0),
                           "total": batch.get("total", 0)}
    return result
