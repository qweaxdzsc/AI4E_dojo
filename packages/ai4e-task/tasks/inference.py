"""任务内推理批次；管理固定输入与运行引用，不实现模型或指标算法。"""

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ai4e_spec.artifacts import InferenceRequest

from ..projects.project import open_project
from ..storage.database import transaction
from ..storage.files import read_json, write_json
from ..storage.layout import inside, task_dir
from ..storage.records import all_records, get, put, remember, replay
from ..storage.snapshots import digest, snapshot
from .checkpoints import inference_samples, inspect_inference, list_inference_checkpoints
from .configuration import read_configuration
from .records import get_run, get_task, list_runs

TERMINAL = {"succeeded", "partial", "failed", "canceled", "interrupted"}


def _folder(project, task_id, identity):
    return inside(task_dir(project, task_id) / ".dojo/inference_batches", identity)


def inference_devices(project: str | Path) -> list[dict]:
    """列出实际可用设备及已知 Dojo 运行占用，不保证识别外部进程。"""
    devices = inspect_inference("devices")
    busy = set()
    for run in list_runs(project):
        if run["status"] not in {"running", "pending", "stopping"}:
            continue
        value = run.get("metadata", {}).get("device")
        cfg = Path(run["run_dir"]) / "inputs/config.yaml"
        if not value and cfg.is_file():
            from omegaconf import OmegaConf

            config = OmegaConf.load(cfg)
            value = (
                OmegaConf.select(config, "infer.device")
                if "infer" in run.get("stages", [])
                else OmegaConf.select(config, "train.device")
            )
        if value == "auto":
            busy.update(v for v in devices if v != "cpu")
        elif value:
            busy.add("cuda:0" if value == "cuda" else str(value))
    return [{"id": d, "label": d.upper(), "busy": d in busy} for d in devices]


def check_inference(project: str | Path, task_id: str, request: dict) -> dict:
    """预检完整批次并解析设备；不创建训练、推理运行或正式版本。"""
    value = InferenceRequest.from_dict(request)
    if get_task(project, task_id).get("archived") or open_project(project).get("archived"):
        raise ValueError("archived")
    if read_configuration(project, task_id)["revision"] != value.expected_revision:
        raise ValueError("configuration_revision_conflict")
    candidates = {c["id"]: c for c in list_inference_checkpoints(project, task_id)}
    chosen, seen = [], set()
    for ref in value.checkpoints:
        c = candidates.get(ref.id)
        if c is None:
            raise ValueError("checkpoint_not_found")
        if c["revision"] != ref.revision:
            raise ValueError("checkpoint_revision_conflict")
        if c["compatibility"]["status"] != "compatible":
            raise ValueError(c["compatibility"]["reason"])
        # 不把同一份字节的 latest/best 标签重复计算。
        if c["revision"] in seen:
            raise ValueError("duplicate_checkpoint_content: 请选择不同内容的检查点")
        seen.add(c["revision"])
        if chosen and (
            c["preparation"]["digest"] != chosen[0]["preparation"]["digest"]
            or c["contract"].get("component", c["contract"].get("model"))
            != chosen[0]["contract"].get("component", chosen[0]["contract"].get("model"))
        ):
            raise ValueError("incompatible_checkpoint_preparation_or_model")
        chosen.append(c)
    if (value.fields is not None or value.metrics is not None) and not (
        task_dir(project, task_id) / "recipe/infer.py"
    ).is_file():
        raise ValueError(
            "legacy_inference_selection_unavailable: 旧post模板不支持字段/指标选择，请使用独立infer模板；旧请求仍可执行"
        )
    sample_info = inference_samples(project, task_id, chosen[0]["id"])
    if sample_info.get("compatibility", {}).get("status") == "invalid":
        raise ValueError(sample_info["compatibility"]["reason"])
    groups = []
    refs = value.selections()
    partitions = sample_info.get("partitions", {})
    for split in dict.fromkeys(
        [s for s in ("train", "validation", "eval", "test") if any(r["split"] == s for r in refs)]
        + [r["split"] for r in refs]
    ):
        samples = [r["sample"] for r in refs if r["split"] == split]
        allowed = partitions.get(split)
        if allowed is None or not set(samples) <= set(allowed):
            raise ValueError("inference_samples_outside_preparation")
        groups.append({"split": split, "samples": [s for s in allowed if s in set(samples)]})
    if value.fields is not None and set(value.fields) - {
        f["id"] for f in sample_info.get("fields", [])
    }:
        raise ValueError("inference_fields_unavailable")
    if value.metrics is not None and set(value.metrics) - {
        m["id"] for m in sample_info.get("metrics", [])
    }:
        raise ValueError("inference_metrics_unavailable")
    devices = inference_devices(project)
    device = value.device
    if device == "auto":
        device = next((v["id"] for v in devices if v["id"] != "cpu" and not v["busy"]), "cpu")
    if device == "cuda":
        device = "cuda:0"
    if device not in [v["id"] for v in devices]:
        raise ValueError("inference_device_unavailable")
    return {
        "request": {**value.to_dict(), "device": device},
        "checkpoints": chosen,
        "preparation": chosen[0]["preparation"],
        "groups": groups,
        "total": len(chosen) * len(refs),
        "device_options": devices,
    }


def _launch(project: Path, task_id: str, identity: str) -> None:
    folder = _folder(project, task_id, identity)
    with (folder / "worker.log").open("ab") as log:
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "ai4e_task.tasks.inference_worker",
                str(project),
                task_id,
                identity,
            ],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    write_json(folder / "launch.json", {"pid": proc.pid, "batch_id": identity})


def submit_inference(project: str | Path, task_id: str, request: dict) -> dict:
    """固定批次意图和代码后启动独立协调进程；请求重试不创建第二批。"""
    project = Path(project).resolve()
    value = InferenceRequest.from_dict(request)
    fingerprint = digest({"task": task_id, "request": value.to_dict()})
    with transaction(project) as db:
        prior = replay(db, value.idempotency_key, fingerprint)
        if prior:
            return read_json(_folder(project, task_id, prior["id"]) / "state.json")
    checked = check_inference(project, task_id, request)
    identity = uuid4().hex
    folder = _folder(project, task_id, identity)
    try:
        with transaction(project) as db:
            prior = replay(db, value.idempotency_key, fingerprint)
            if prior:
                return read_json(_folder(project, task_id, prior["id"]) / "state.json")
            task = get(db, "task", task_id)
            if task.get("archived"):
                raise ValueError("task_archived")
            folder.mkdir(parents=True)
            code = task_dir(project, task_id) / "recipe"
            captured = snapshot(code, folder / "code")
            import hashlib

            from ..templates.materialize import read_entry
            from .configuration import _path

            saved_config = folder / "code" / read_entry(folder / "code")["config"]
            if (
                hashlib.sha256(_path(project, task_id).read_bytes()).hexdigest()
                != value.expected_revision
                or hashlib.sha256(saved_config.read_bytes()).hexdigest() != value.expected_revision
            ):
                raise ValueError("configuration_revision_conflict")
            record = {
                "id": identity,
                "task_id": task_id,
                "created_at": datetime.now(UTC).isoformat(),
                "name": value.name,
                "status": "capturing",
                "device": checked["request"]["device"],
                "checkpoint_count": len(checked["checkpoints"]),
                "subrun_count": len(checked["checkpoints"]) * len(checked["groups"]),
                "total": checked["total"],
                "completed": 0,
                "children": [],
                "error": None,
            }
            write_json(
                folder / "request.json",
                {**checked, "task_id": task_id, "id": identity, "code_digest": captured["digest"]},
            )
            write_json(folder / "state.json", record)
            put(db, "inference_batch", record)
            remember(db, value.idempotency_key, fingerprint, "inference_batch", identity)
    except BaseException:
        import shutil

        shutil.rmtree(folder, ignore_errors=True)
        raise
    try:
        _launch(project, task_id, identity)
    except Exception as exc:  # noqa: BLE001 - 已提交批次必须可查询失败
        record.update(status="failed", error=str(exc))
        write_json(folder / "state.json", record)
    return record


def _coordinator_alive(folder: Path) -> bool:
    # 恢复启动的新进程可能尚未提交 coordinator；两类收据均核验精确身份。
    for name in ("coordinator.json", "launch.json"):
        receipt = folder / name
        if not receipt.is_file():
            continue
        info = read_json(receipt)
        proc = subprocess.run(
            ["ps", "-p", str(info["pid"]), "-o", "stat=", "-o", "args="],
            capture_output=True,
            text=True,
            check=False,
        )
        if (
            proc.returncode == 0
            and not proc.stdout.lstrip().startswith("Z")
            and "ai4e_task.tasks.inference_worker" in proc.stdout
            and info["batch_id"] in proc.stdout
        ):
            return True
    return False


def read_inference_batch(project: str | Path, task_id: str, identity: str) -> dict:
    """读取持久化批次；协调器失联只报告中断，不自动重复执行。"""
    get_task(project, task_id)
    folder = _folder(project, task_id, identity)
    path = folder / "state.json"
    if not path.is_file():
        raise ValueError("inference_batch_not_found: 推理批次不存在或已被清理")
    value = read_json(path)
    if value["task_id"] != task_id:
        raise ValueError("inference_task_mismatch")
    age = (datetime.now(UTC) - datetime.fromisoformat(value["created_at"])).total_seconds()
    if value["status"] not in TERMINAL and age > 10 and not _coordinator_alive(folder):
        value = {**value, "status": "interrupted", "error": "推理协调进程已退出，可恢复核对或重试"}
    return value


def list_inference_batches(project: str | Path, task_id: str) -> list[dict]:
    """按任务列出批次，不依赖浏览器内存。"""
    get_task(project, task_id)
    with transaction(project) as db:
        ids = [r["id"] for r in all_records(db, "inference_batch") if r["task_id"] == task_id]
    rows = []
    for identity in reversed(ids):
        try:
            rows.append(read_inference_batch(project, task_id, identity))
        except ValueError as exc:
            if str(exc).startswith("inference_batch_not_found"):
                continue
            raise
    return rows


def cancel_inference(project: str | Path, task_id: str, identity: str) -> dict:
    """写入取消意图，由协调器停止自身子运行；不向训练进程发送信号。"""
    value = read_inference_batch(project, task_id, identity)
    if value["status"] in TERMINAL - {"interrupted"}:
        return value
    folder = _folder(project, task_id, identity)
    write_json(folder / "cancel.json", {"id": identity})
    if value["status"] == "interrupted":
        from .execution import stop_run

        for child in value["children"]:
            if child.get("run_id"):
                run = get_run(project, child["run_id"])
                if run["status"] in {"queued", "running", "stopping"}:
                    stop_run(project, child["run_id"])
        value["status"] = "canceled"
        write_json(folder / "state.json", value)
    return value


def recover_inference(project: str | Path, task_id: str, identity: str) -> dict:
    """显式恢复协调，子运行按已有收据核对，不重新捕获变化的输入。"""
    value = read_inference_batch(project, task_id, identity)
    if value["status"] == "interrupted":
        if get_task(project, task_id).get("archived") or open_project(project).get("archived"):
            raise ValueError("archived")
        _launch(Path(project).resolve(), task_id, identity)
        return {**value, "status": "queued", "error": None}
    return value


def retry_inference(
    project: str | Path, task_id: str, identity: str, *, idempotency_key: str | None = None
) -> dict:
    """重试失败检查点，沿用固定输入；同一请求键不会生成第二个批次。"""
    import shutil

    from .checkpoints import file_digest

    project = Path(project).resolve()
    fingerprint = digest({"retry_inference": identity, "task": task_id})
    with transaction(project) as db:
        prior = replay(db, idempotency_key, fingerprint)
        if prior:
            return read_json(_folder(project, task_id, prior["id"]) / "state.json")
    if get_task(project, task_id).get("archived") or open_project(project).get("archived"):
        raise ValueError("archived")
    previous = read_inference_batch(project, task_id, identity)
    if previous["status"] not in TERMINAL:
        raise ValueError("inference_batch_still_active")
    source = _folder(project, task_id, identity)
    request = read_json(source / "request.json")
    failed = [c for c in previous["children"] if c["status"] != "succeeded"]
    if not failed or any(not c.get("checkpoint", {}).get("fixed") for c in failed):
        raise ValueError("no_frozen_failed_checkpoints_to_retry")
    for child in failed:
        cp = child["checkpoint"]
        if file_digest(Path(cp["fixed"]["path"])) != cp["revision"]:
            raise ValueError("frozen_checkpoint_changed")
        if file_digest(Path(cp["preparation"]["path"])) != cp["preparation"]["revision"]:
            raise ValueError("preparation_revision_conflict")
        if child.get("run_id") and get_run(project, child["run_id"])["status"] in {
            "running",
            "pending",
            "stopping",
        }:
            raise ValueError("inference_child_still_active")
    new_id = uuid4().hex
    target = _folder(project, task_id, new_id)
    committed = False
    try:
        with transaction(project) as db:
            prior = replay(db, idempotency_key, fingerprint)
            if prior:
                return read_json(_folder(project, task_id, prior["id"]) / "state.json")
            if get(db, "task", task_id).get("archived"):
                raise ValueError("task_archived")
            target.mkdir(parents=True)
            captured = snapshot(source / "code", target / "code")
            if captured["digest"] != request["code_digest"]:
                raise ValueError("inference_code_changed")
            checked = {
                **request,
                "id": new_id,
                "checkpoints": list(
                    {c["checkpoint"]["id"]: c["checkpoint"] for c in failed}.values()
                ),
                "retry_children": [
                    {
                        "checkpoint_id": c["checkpoint"]["id"],
                        "split": c.get("split", request["request"].get("split", "test")),
                        "samples": c.get("samples", request["request"].get("samples", [])),
                    }
                    for c in failed
                ],
                "inherited_children": [
                    c for c in previous["children"] if c["status"] == "succeeded"
                ]
                + request.get("inherited_children", []),
                "retry_of": identity,
                "total": sum(
                    len(c.get("samples", request["request"].get("samples", []))) for c in failed
                ),
            }
            value = {
                **previous,
                "id": new_id,
                "status": "capturing",
                "children": [],
                "completed": 0,
                "total": checked["total"],
                "checkpoint_count": len(checked["checkpoints"]),
                "subrun_count": len(failed),
                "inherited_children": checked["inherited_children"],
                "inherited_samples": sum(
                    len(c.get("samples", [])) for c in checked["inherited_children"]
                ),
                "error": None,
                "retry_of": identity,
                "created_at": datetime.now(UTC).isoformat(),
            }
            write_json(target / "request.json", checked)
            write_json(target / "state.json", value)
            put(db, "inference_batch", value)
            remember(db, idempotency_key, fingerprint, "inference_batch", new_id)
        committed = True
        try:
            _launch(project, task_id, new_id)
        except Exception as exc:  # noqa: BLE001 - 已提交重试必须保留可查询失败
            value.update(status="failed", error=str(exc))
            write_json(target / "state.json", value)
        return value
    finally:
        if not committed:
            shutil.rmtree(target, ignore_errors=True)
