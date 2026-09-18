"""独立推理批次协调器；计算始终由现有冻结运行执行。"""

import fcntl
import json
import sys
import time
from pathlib import Path

from ..storage.files import read_json, write_json
from ..storage.layout import task_dir
from ..templates.materialize import read_entry
from .checkpoints import file_digest, freeze_checkpoint
from .execution import start_captured_run, stop_run, submit_run
from .inference import TERMINAL, _folder, list_inference_batches
from .records import get_run, list_runs


def _progress(run: dict) -> dict:
    """读取 writer 已提交账本，新旧推理均不从日志估算样本数。"""
    root = Path(run["run_dir"]) / "artifacts"
    for name in ("inference-progress.json", "infer-progress.json", "post-progress.json"):
        path = root / name
        if path.is_file():
            return read_json(path)
    return {}


def _completed(progress: dict) -> int:
    if "completed" in progress:
        return int(progress["completed"])
    ops = progress.get("operations", {})
    # 保存后才交付；无保存分支时按实际预测完成计数。
    record = next(
        (
            ops[k]
            for k in ("save", "evaluation", "predictions", "prediction")
            if k in ops and ops[k].get("status") != "skipped"
        ),
        {},
    )
    return int(record.get("completed", 0))


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

    groups = request.get("groups") or [
        {"split": selection.get("split", "test"), "samples": selection.get("samples", [])}
    ]
    work = request.get("retry_children") or [
        {"checkpoint_id": cp["id"], **group} for cp in request["checkpoints"] for group in groups
    ]

    def publish():
        value["completed"] = sum(_completed(c.get("progress", {})) for c in value["children"])
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
            stage = "infer"
            entry = read_entry(code)
            declared = entry.get("inputs", {})
            for index, unit in enumerate(work):
                checkpoint = next(
                    c for c in request["checkpoints"] if c["id"] == unit["checkpoint_id"]
                )
                if any(c["id"] == str(index) for c in value["children"]):
                    continue
                params = {
                    **selection["options"],
                    "samples": unit["samples"],
                    "split": unit["split"],
                    **{k: selection[k] for k in ("fields", "metrics") if k in selection},
                }
                overrides = ["pipeline.stages=" + json.dumps([stage])]
                overrides += [stage + "." + k + "=" + json.dumps(v) for k, v in params.items()]
                overrides += [
                    "inputs.infer.preparation=" + json.dumps(checkpoint["preparation"]["path"]),
                    "inputs.infer.checkpoint=" + json.dumps(checkpoint["fixed"]["path"]),
                    "infer.device=" + json.dumps(selection["device"]),
                ]
                keys = sorted(
                    set(declared)
                    & {
                        "inputs.infer.preparation",
                        "inputs.infer.checkpoint",
                    }
                )
                run = submit_run(
                    project,
                    task_id,
                    overrides=overrides,
                    _code=code,
                    idempotency_key="inference:" + identity + ":" + str(index),
                    start=False,
                    input_keys=keys,
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
                        "id": str(index),
                        "checkpoint": checkpoint,
                        "split": unit["split"],
                        "samples": unit["samples"],
                        "run_id": run["id"],
                        "status": "queued",
                        "progress": {},
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
