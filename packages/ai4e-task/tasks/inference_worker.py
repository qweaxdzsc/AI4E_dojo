"""独立推理批次协调器；计算始终由现有冻结运行执行。"""

import fcntl
import sys
import time
from pathlib import Path

from ..storage.files import read_json, write_json
from ..storage.layout import task_dir
from .checkpoints import file_digest, freeze_checkpoint
from .execution import start_captured_run, stop_run, submit_run
from .inference import TERMINAL, _folder, list_inference_batches
from .records import get_run, list_runs


def _progress(run: dict) -> dict:
    """只读取应用交付的通用管理进度，不解释科学分支。"""
    path = Path(run["run_dir"]) / "artifacts/task-progress.json"
    return read_json(path) if path.is_file() else {"completed": None}


def _completed(progress: dict):
    value = progress.get("completed")
    if value is not None and (type(value) is not int or value < 0):
        raise ValueError("invalid_execution_progress")
    return value


def coordinate(project: Path, task_id: str, identity: str) -> None:
    """恢复或推进已有批次；未知子运行不自动重启。"""
    folder = _folder(project, task_id, identity)
    lock = (folder / "worker.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        return
    import os

    write_json(folder / "coordinator.json", {"pid": os.getpid(), "batch_id": identity})
    value = read_json(folder / "state.json")
    request = read_json(folder / "request.json")
    selection = request["request"]

    from .checkpoints import inspect_inference
    from .operation_sources import operation_context, verify_source

    work = request.get("execution_plan", [])

    def publish():
        counts = [_completed(c.get("progress", {})) for c in value["children"]]
        value["completed"] = sum(counts) if all(n is not None for n in counts) else None
        value["finished_subruns"] = sum(c["status"] == "succeeded" for c in value["children"])
        value["finished_checkpoints"] = sum(
            all(
                c["status"] == "succeeded"
                for c in value["children"]
                if c["checkpoint"]["id"] == cp["id"]
            )
            and sum(c["checkpoint"]["id"] == cp["id"] for c in value["children"])
            == sum(w["checkpoint_id"] == cp["id"] for w in work)
            for cp in request["checkpoints"]
        )
        write_json(folder / "state.json", value)

    def canceled():
        return (folder / "cancel.json").exists()

    task_lock = None
    try:
        from ai4e_spec.artifacts.task_operations import validate_execution_plan

        context = operation_context(project, task_id, batch_id=identity)
        verify_source(context["source"], context["recipe"])
        if not work:
            work = validate_execution_plan(
                inspect_inference("plan_execution", context=context, request=request)
            )
        if len(value["children"]) < len(work):
            for checkpoint in request["checkpoints"]:
                if canceled():
                    value["status"] = "canceled"
                    publish()
                    return
                if not checkpoint.get("fixed"):
                    checkpoint["fixed"] = freeze_checkpoint(
                        project, task_id, checkpoint["id"], checkpoint["revision"]
                    )
                if file_digest(Path(checkpoint["fixed"]["path"])) != checkpoint["revision"]:
                    raise ValueError("frozen_checkpoint_changed")
                prep = checkpoint["preparation"]
                if file_digest(Path(prep["path"])) != prep["revision"]:
                    raise ValueError("preparation_revision_conflict")
                value["captured_checkpoints"] = request["checkpoints"].index(checkpoint) + 1
                write_json(folder / "request.json", request)
                publish()
            code = folder / "code"
            work = validate_execution_plan(
                inspect_inference("plan_execution", context=context, request=request)
            )
            request["execution_plan"] = work
            write_json(folder / "request.json", request)
            for unit in work:
                checkpoint = next(
                    c for c in request["checkpoints"] if c["id"] == unit["checkpoint_id"]
                )
                if any(c["id"] == unit["id"] for c in value["children"]):
                    continue
                run = submit_run(
                    project,
                    task_id,
                    overrides=unit["overrides"],
                    _code=code,
                    _application_source=context["source"],
                    idempotency_key="inference:" + identity + ":" + unit["id"],
                    start=False,
                    input_keys=unit["input_keys"],
                    metadata={
                        "purpose": "inference",
                        "split": unit["split"],
                        "batch_id": identity,
                        "device": selection["device"],
                        "checkpoint_revision": checkpoint["revision"],
                        "execution_mode": "native",
                    },
                )
                value["children"].append(
                    {
                        "id": unit["id"],
                        "checkpoint": checkpoint,
                        "split": unit["split"],
                        "samples": unit["samples"],
                        "run_id": run["id"],
                        "status": "queued",
                        "progress": {"completed": 0},
                        "error": None,
                    }
                )
                publish()
        # 一个任务的多个批次使用同一把进程锁；等待时仍响应取消。
        task_lock = (task_dir(project, task_id) / ".dojo/inference.lock").open("a")
        value["status"] = "queued"
        queued_at = time.monotonic()
        publish()
        while True:
            if canceled():
                break
            # 保持提交顺序，并阻止失联协调器遗留的子进程与新批次重叠。
            earlier = any(
                b["id"] != identity
                and b["created_at"] < value["created_at"]
                and b["status"] not in TERMINAL
                for b in list_inference_batches(project, task_id)
            )
            orphan_active = any(
                r.get("metadata", {}).get("purpose") == "inference"
                and r.get("metadata", {}).get("batch_id") != identity
                and r["status"] in {"pending", "running", "stopping"}
                for r in list_runs(project, task_id)
            )
            if earlier or orphan_active:
                time.sleep(0.25)
                continue
            try:
                fcntl.flock(task_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                time.sleep(0.25)
                continue
            break
        value["status"] = "running"
        value.setdefault("timings", {})["queue_seconds"] = time.monotonic() - queued_at
        publish()
        for child in value["children"]:
            run = get_run(project, child["run_id"])
            if canceled():
                if run["status"] in {"queued", "running", "stopping"}:
                    run = stop_run(project, run["id"])
                child["status"] = "succeeded" if run["status"] == "succeeded" else "canceled"
                publish()
                continue
            if run["status"] == "queued":
                if (
                    file_digest(Path(child["checkpoint"]["fixed"]["path"]))
                    != child["checkpoint"]["revision"]
                ):
                    raise ValueError("frozen_checkpoint_changed")
                prep = child["checkpoint"]["preparation"]
                if file_digest(Path(prep["path"])) != prep["revision"]:
                    raise ValueError("preparation_revision_conflict")
                start_captured_run(project, run["id"])
                run = get_run(project, run["id"])
            while run["status"] in {"running", "pending", "stopping"}:
                child.update(status=run["status"], progress=_progress(run))
                publish()
                if canceled():
                    run = stop_run(project, run["id"])
                else:
                    time.sleep(0.3)
                    run = get_run(project, run["id"])
            child.update(status=run["status"], error=run.get("error"), progress=_progress(run))
            if run["status"] == "unknown":
                child["status"] = "interrupted"
            publish()
        statuses = [c["status"] for c in value["children"]]
        value["status"] = (
            "canceled"
            if canceled()
            else "succeeded"
            if all(s == "succeeded" for s in statuses)
            else "partial"
            if "succeeded" in statuses or value["completed"]
            else "failed"
        )
        publish()
    except BaseException as exc:  # noqa: BLE001 - 批次失败保留已有运行和文件
        for child in value["children"]:
            run = get_run(project, child["run_id"])
            if run["status"] in {"queued", "running", "stopping"}:
                try:
                    stop_run(project, run["id"])
                except RuntimeError:
                    pass
                run = get_run(project, run["id"])
            child.update(status=run["status"], progress=_progress(run), error=run.get("error"))
        value.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        publish()
    finally:
        if task_lock is not None:
            task_lock.close()
        lock.close()


if __name__ == "__main__":
    coordinate(Path(sys.argv[1]), sys.argv[2], sys.argv[3])
