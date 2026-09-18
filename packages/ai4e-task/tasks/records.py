"""任务记录与运行收据投影；不依赖阶段查询或推理业务。"""

from pathlib import Path

from ..storage.artifacts import read_run
from ..storage.database import transaction
from ..storage.files import read_json
from ..storage.records import fetch, get, listing, put
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
    publication_error = value.get("error")
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
            if str(publication_error).startswith("shared_dataset_publish_failed:"):
                value.update(status="failed", error=publication_error)
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
            if latest.get("shared_publications"):
                value["shared_publications"] = latest["shared_publications"]
            if value.get("pid") is None and latest.get("pid") is not None:
                value["pid"] = latest["pid"]
            put(db, "run", value, replace=True)
    plans = value.get("shared_outputs", [])
    if plans and value["status"] in {"failed", "stopped", "succeeded"}:
        from ..storage.shared_datasets import finish

        try:
            finish(root, plans, run_id, succeeded=value["status"] == "succeeded")
            receipts = fetch(root, "run", run_id).get("shared_publications")
            if receipts:
                value["shared_publications"] = receipts
        except (OSError, ValueError, KeyError) as exc:
            value.update(status="failed", error=f"shared_dataset_publish_failed: {exc}")
            finish(root, plans, run_id, succeeded=False)
            with transaction(root) as db:
                put(db, "run", value, replace=True)
    return {
        **value,
        "research_status": artifacts.get("summary", {}).get("research_status", "unavailable"),
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
