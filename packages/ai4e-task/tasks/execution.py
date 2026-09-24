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
    _application_source: dict | None = None,
    expected_revision: str | None = None,
    operation_mode: str = "execute",
    input_keys: list[str] | None = None,
    start: bool = True,
    metadata: dict | None = None,
    overwrite: bool = False,
) -> dict:
    """捕获当前工作目录并提交；返回运行记录，不创建正式版本。"""
    from omegaconf import OmegaConf

    if operation_mode not in {"execute", "trial"}:
        raise ValueError("invalid_operation_mode")
    info = open_project(project)
    project = Path(project).resolve()
    identity = uuid4().hex
    folder = task_dir(project, task_id)
    execution = folder / ".dojo/executions" / identity
    stage = execution.with_name(identity + ".tmp")
    fingerprint = digest(
        {
            "task_id": task_id,
            "overwrite": overwrite,
            "overrides": overrides or [],
            "resumed_from": resumed_from,
            "operation_mode": operation_mode,
            "expected_revision": expected_revision,
            "input_keys": input_keys,
            "application_source": _application_source,
            **({"start": start, "metadata": metadata} if not start or metadata is not None else {}),
        }
    )
    published = False
    try:
        with transaction(project) as db:
            prior = replay(db, idempotency_key, fingerprint)
            if prior:
                return prior
            task = get(db, "task", task_id)
            if task.get("archived") or info.get("archived"):
                raise ValueError("task_archived")
            version = get(db, "version", task["version_id"])
            shared_records = all_records(db, "asset")
        source = _code or folder / "recipe"
        entry = read_entry(source)
        if not entry:
            raise ValueError("configuration_unavailable: config.yaml")
        for field in ("script", "config"):
            if not inside(source, entry[field]).is_file():
                raise FileNotFoundError(entry[field])
        if expected_revision is not None:
            import hashlib

            if (
                hashlib.sha256(inside(source, entry["config"]).read_bytes()).hexdigest()
                != expected_revision
            ):
                raise ValueError("configuration_revision_conflict")
        stage.mkdir(parents=True)
        captured = snapshot(source, stage / "code")
        cfgpath = stage / "code" / entry["config"]
        cfg = OmegaConf.load(cfgpath)
        if overrides:
            cfg = OmegaConf.merge(cfg, OmegaConf.from_dotlist(overrides))
        from .descriptions import described_entry

        entry = described_entry(stage / "code", config=OmegaConf.to_container(cfg, resolve=False))
        if _application_source is not None:
            from .operation_sources import same_source, verify_source, with_operation

            expected_source = with_operation(_application_source, "inspect")
            verify_source(expected_source, stage / "code")
            actual_source = entry["task_description"].get("source")
            if (
                not actual_source
                or not same_source(expected_source, actual_source)
            ):
                raise ValueError("application_source_conflict")
            entry["task_description"]["source"] = expected_source
        from ai4e_core.base.config.conventions import input_bindings

        entry["inputs"] = {
            **dict.fromkeys(input_bindings(OmegaConf.to_container(cfg, resolve=False)), "other"),
            **entry["inputs"],
        }
        from .output_bindings import allocate_outputs, selected_inputs

        run_dir = folder / "runs" / identity
        data_dir = folder / "data" / identity
        _, shared_outputs = allocate_outputs(
            project,
            entry,
            cfg,
            run_dir,
            data_dir,
            operation_mode=operation_mode,
            overwrite=overwrite,
        )
        declared_inputs = selected_inputs(entry, list(cfg.pipeline.stages))
        if input_keys is None:
            input_keys = declared_inputs
        elif declared_inputs is not None:
            input_keys = sorted(set(input_keys) & set(declared_inputs))
        if shared_outputs:
            OmegaConf.update(cfg, "execution.overwrite", overwrite, force_add=True)
        # 相对输入以工作目录为基准，不能因执行副本位置改变含义。
        for key in entry.get("inputs", {}):
            if input_keys is not None and key not in input_keys:
                continue
            value = OmegaConf.select(cfg, key)
            if isinstance(value, str) and value not in {"official", "last", "best", "latest"}:
                old = task.get("assets", {}).get(key)
                candidate = Path(value).expanduser()
                if not candidate.is_absolute():
                    candidate = (source / entry["config"]).parent / candidate
                from ..storage.shared_datasets import resolve_reference

                current_shared = resolve_reference(project, candidate)
                if current_shared is not None:
                    old = current_shared
                if old and candidate.resolve() == asset_path(project, old).resolve():
                    candidate = validate_asset(project, old)
                OmegaConf.update(cfg, key, str(candidate.resolve()))
        OmegaConf.save(cfg, cfgpath)
        capture_entry = entry
        if input_keys is not None:
            if set(input_keys) - set(entry.get("inputs", {})):
                raise ValueError("unknown_stage_input_binding")
            capture_entry = {
                **entry,
                "inputs": {key: entry["inputs"][key] for key in input_keys},
            }
        inputs = capture_inputs(
            stage / "code",
            capture_entry,
            project=project,
            inherited=task.get("assets", {}),
            shared=shared_records,
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
            "stage_outputs": {
                plan["stage"]: str(project / plan["path"]) for plan in shared_outputs
            },
        }
        from ..storage.shared_datasets import reserve

        write_json(
            stage / "request.json",
            {
                "context": request,
                "entry": entry,
                "project": str(project),
                "shared_outputs": shared_outputs,
                "overwrite": overwrite,
            },
        )
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
            "operation_mode": operation_mode,
            "stages": list(OmegaConf.select(cfg, "pipeline.stages", default=[])),
            "source_snapshot": captured,
            "code_digest": digest(inventory(stage / "code")),
            "metadata": {
                **(entry["task_description"].get("description") or {}).get("resources", {}),
                **(metadata or {}),
            },
            "task_description": entry["task_description"],
            "shared_outputs": shared_outputs,
        }
        if not start:
            value["status"] = "queued"
        with transaction(project) as db:
            prior = replay(db, idempotency_key, fingerprint)
            if prior:
                return prior
            current = get(db, "task", task_id)
            if current != task:
                raise ValueError("task_changed_during_capture")
            if current.get("archived") or open_project(project).get("archived"):
                raise ValueError("task_archived")
            # 长文件摘要在事务外；提交前复核共享发布身份，不能捕获正在覆盖的内容。
            latest_assets = {a["id"]: a for a in all_records(db, "asset")}
            for asset in inputs.values():
                if asset.get("shared_dataset"):
                    from ..storage.shared_datasets import resolve_reference

                    latest = (
                        resolve_reference(project, asset_path(project, asset))
                        if asset.get("shared_project")
                        else latest_assets.get(asset["id"])
                    ) or {}
                    if (
                        latest.get("status") != "available"
                        or latest.get("digest") != asset["digest"]
                        or latest.get("source") != asset.get("source")
                    ):
                        raise ValueError("shared_dataset_changed_during_capture")
            reserve(db, project, shared_outputs, identity)
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
    if not start:
        return value
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


def start_captured_run(project: str | Path, run_id: str) -> dict:
    """启动已冻结的排队运行；事务内改变启动意图，重复调用不重启进程。"""
    project = Path(project).resolve()
    with transaction(project) as db:
        value = get(db, "run", run_id)
        if value["status"] != "queued":
            return value
        if get(db, "task", value["task_id"]).get("archived"):
            raise ValueError("task_archived")
        code = project / value["code_path"]
        if digest(inventory(code)) != value["code_digest"]:
            raise ValueError("run_snapshot_changed")
        # 启动与登记 PID 共用事务，取消请求不能落入无 PID 的启动缝隙。
        request = project / value["request_path"]
        try:
            pid = local.start(request)
        except Exception as exc:  # noqa: BLE001 - 保存启动失败事实
            value.update(status="failed", error=f"launch_failed: {exc}")
        else:
            value.update(pid=pid, status="running")
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
    if value["status"] == "queued":
        with transaction(project) as db:
            current = get(db, "run", run_id)
            if current["status"] == "queued":
                current["status"] = "stopped"
                current["canceled_before_start"] = True
                put(db, "run", current, replace=True)
                return current
        return stop_run(project, run_id, timeout=timeout)
    request = Path(project).resolve() / value["request_path"]
    if not local.alive(value.get("pid"), request):
        raise RuntimeError("process_identity_unconfirmed")
    write_json(request.parent / "stop.json", {"run_id": run_id})
    child = local.terminate(value["pid"], request)
    if child is not None:
        import signal
        import subprocess

        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return get_run(project, run_id)
        # 模块导入时信号处理器尚未安装，worker无法写收据。只有持有真实
        # Popen并确认SIGTERM退出时才记录停止；裸PID消失依然是unknown。
        if code == -signal.SIGTERM and not (request.parent / "finished.json").exists():
            write_json(
                request.parent / "finished.json",
                {
                    "run_id": run_id,
                    "status": "stopped",
                    "error": "terminated_before_worker_receipt",
                    "exit_code": code,
                },
            )
    return wait_run(project, run_id, timeout=timeout)


def resume_run(
    project, run_id: str, *, checkpoint: str = "latest.pt", idempotency_key: str | None = None
) -> dict:
    """恢复固定运行的配置及代码，单独注入检查点；不增加正式版本。"""
    previous = fetch(project, "run", run_id)
    source = Path(project).resolve() / previous["code_path"]
    if digest(inventory(source)) != previous.get("code_digest"):
        raise ValueError("run_snapshot_changed")
    declaration = previous.get("task_description", {}).get("description") or {}
    if declaration and not previous.get("task_description", {}).get("source"):
        raise ValueError("operation_unavailable: captured_application_source_missing")
    resume_inputs = declaration.get("resume_inputs", [])
    if len(resume_inputs) != 1:
        raise ValueError("entry_does_not_support_resume")
    resume_key = resume_inputs[0]
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
        _application_source=previous.get("task_description", {}).get("source"),
    )
