"""捕获任务代码、配置和输入，提交本地独立运行。"""

import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..projects.project import open_project
from ..storage.database import transaction
from ..storage.files import write_json
from ..storage.layout import inside, task_dir
from ..storage.records import all_records, fetch, get, put, remember, replay
from ..storage.snapshots import digest, inventory, snapshot
from ..templates.materialize import read_entry
from . import local
from .assets import asset_path, capture_inputs, validate_asset


def submit_run(
    project,
    task_id: str,
    *,
    overrides: list[str] | None = None,
    idempotency_key: str | None = None,
    resumed_from: str | None = None,
    _code: Path | None = None,
) -> dict:
    """捕获当前工作目录并提交；返回运行记录，不创建正式版本。"""
    from omegaconf import OmegaConf

    info = open_project(project)
    project = Path(project).resolve()
    identity = uuid4().hex
    folder = task_dir(project, task_id)
    execution = folder / ".dojo/executions" / identity
    stage = execution.with_name(identity + ".tmp")
    fingerprint = digest(
        {"task_id": task_id, "overrides": overrides or [], "resumed_from": resumed_from}
    )
    published = False
    try:
        with transaction(project) as db:
            prior = replay(db, idempotency_key, fingerprint)
            if prior:
                return prior
            task = get(db, "task", task_id)
            version = get(db, "version", task["version_id"])
            source = _code or folder / "recipe"
            entry = read_entry(source)
            if not entry:
                raise ValueError("entry_required: task-entry.json")
            for field in ("script", "config"):
                if not inside(source, entry[field]).is_file():
                    raise FileNotFoundError(entry[field])
            stage.mkdir(parents=True)
            captured = snapshot(source, stage / "code")
            cfgpath = stage / "code" / entry["config"]
            cfg = OmegaConf.load(cfgpath)
            if overrides:
                cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(overrides))
            # 数据及运行输出位置只允许绑定到本次任务位置，覆盖参数不能逃逸。
            run_dir = folder / "runs" / identity
            data_dir = folder / "data" / identity
            bindings = {"run_root": str(run_dir.parent), "data_dir": str(data_dir)}
            for key, pattern in entry["outputs"].items():
                value = pattern.format(**bindings)
                output = Path(value).resolve()
                if key != "run_root" and not output.is_relative_to(data_dir):
                    raise ValueError(f"output_binding_escape: {key}")
                if key == "run_root" and output != run_dir.parent:
                    raise ValueError("run_root_binding_mismatch")
                OmegaConf.update(cfg, key, value, force_add=True)
            if "run_root" not in entry["outputs"]:
                raise ValueError("run_root_binding_required")
            # 相对输入以工作目录为基准，不能因执行副本位置改变含义。
            for key in entry.get("inputs", {}):
                value = OmegaConf.select(cfg, key)
                if isinstance(value, str) and value not in {"official", "last", "best", "latest"}:
                    old = task.get("assets", {}).get(key)
                    candidate = Path(value).expanduser()
                    if not candidate.is_absolute():
                        candidate = (source / entry["config"]).parent / candidate
                    if old and candidate.resolve() == asset_path(project, old).resolve():
                        candidate = validate_asset(project, old)
                    OmegaConf.update(cfg, key, str(candidate.resolve()))
            OmegaConf.save(cfg, cfgpath)
            inputs = capture_inputs(
                stage / "code",
                entry,
                project=project,
                inherited=task.get("assets", {}),
                shared=all_records(db, "asset"),
            )
            request = {
                "schema_version": 1,
                "project_id": info["id"],
                "task_id": task_id,
                "version_id": task["version_id"],
                "run_id": identity,
                "run_dir": str(run_dir),
                "data_dir": str(data_dir),
                "code_dir": str(execution / "code"),
                "version": version,
                "assets": inputs,
                "resumed_from": resumed_from,
            }
            write_json(stage / "request.json", {"context": request, "entry": entry})
            value = {
                "id": identity,
                "task_id": task_id,
                "version_id": task["version_id"],
                "status": "pending",
                "created_at": datetime.now(UTC).isoformat(),
                "run_path": str(run_dir.relative_to(project)),
                "data_path": str(data_dir.relative_to(project)),
                "code_path": str((execution / "code").relative_to(project)),
                "request_path": str((execution / "request.json").relative_to(project)),
                "pid": None,
                "resumed_from": resumed_from,
                "source_snapshot": captured,
                "code_digest": digest(inventory(stage / "code")),
            }
            stage.rename(execution)
            published = True
            put(db, "run", value)
            remember(db, idempotency_key, fingerprint, "run", identity)
    except BaseException:
        if published:
            shutil.rmtree(execution)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    # 意图已持久化再启动。此处崩溃留下 pending，查询标待核对，不自动重复提交。
    try:
        pid = local.start(execution / "request.json")
    except Exception as exc:  # noqa: BLE001 - 外部执行边界保存可查询失败
        value.update(status="failed", error=f"launch_failed: {exc}")
    else:
        value.update(pid=pid, status="running")
    with transaction(project) as db:
        put(db, "run", value, replace=True)
    return value


def wait_run(
    project: str | Path, run_id: str, *, timeout: float = 60, interval: float = 0.1
) -> dict:
    """等待真实完成状态；超时返回当前状态，不把超时当失败。"""
    from .query import get_run

    deadline = time.monotonic() + timeout
    while True:
        value = get_run(project, run_id)
        if (
            value["status"] in {"succeeded", "failed", "stopped", "unknown"}
            or time.monotonic() >= deadline
        ):
            return value
        time.sleep(interval)


def stop_run(project: str | Path, run_id: str, *, timeout: float = 10) -> dict:
    """请求停止并等待确认；未确认保留 stopping 或 unknown。"""
    from .query import get_run

    value = get_run(project, run_id)
    if value["status"] in {"succeeded", "failed", "stopped"}:
        return value
    request = Path(project).resolve() / value["request_path"]
    if not local.alive(value.get("pid"), request):
        raise RuntimeError("process_identity_unconfirmed")
    write_json(request.parent / "stop.json", {"run_id": run_id})
    local.terminate(value["pid"], request)
    return wait_run(project, run_id, timeout=timeout)


def resume_run(
    project, run_id: str, *, checkpoint: str = "latest.pt", idempotency_key: str | None = None
) -> dict:
    """恢复固定运行的配置及代码，单独注入检查点；不增加正式版本。"""
    previous = fetch(project, "run", run_id)
    source = Path(project).resolve() / previous["code_path"]
    if digest(inventory(source)) != previous.get("code_digest"):
        raise ValueError("run_snapshot_changed")
    entry = read_entry(source)
    resume_key = entry.get("resume_key")
    if not resume_key:
        raise ValueError("entry_does_not_support_resume")
    path = inside(Path(project) / previous["run_path"] / "checkpoints", checkpoint)
    if not path.is_file():
        raise FileNotFoundError(path)
    return submit_run(
        project,
        previous["task_id"],
        overrides=[f"{resume_key}={path}"],
        resumed_from=run_id,
        idempotency_key=idempotency_key,
        _code=source,
    )
