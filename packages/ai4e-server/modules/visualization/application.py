"""受控资产和可取消操作；服务持久化只保存显示与辅助操作事实。"""

import hashlib
import json
import shutil
import subprocess
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ...infrastructure.content_access import resolve, revision

_LOCK = threading.RLock()
_CAPACITY = threading.Semaphore(1)
_PROCESSES: dict[str, subprocess.Popen] = {}
_ACTIVE: set[str] = set()
TERMINAL = {"succeeded", "failed", "canceled", "interrupted", "stale"}


def _reap(process):
    """终止并有界回收辅助子进程，避免孤儿和僵尸。"""
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)


def _cleanup_partial(service, identity):
    value = service.store.get("operation", identity)
    if value and value["status"] in {"canceled", "interrupted", "stale"}:
        shutil.rmtree(service.settings.root / "display" / identity, ignore_errors=True)


def shutdown_operations(service):
    """关闭本服务辅助操作；task 研究运行由其独立生命周期管理。"""
    pending = []
    with _LOCK:
        for value in service.store.list("operation"):
            identity = value["operation_id"]
            if value["status"] not in TERMINAL:
                value.update(status="interrupted", event_cursor=value["event_cursor"] + 1)
                service.store.put("operation", identity, value)
            process = _PROCESSES.pop(identity, None)
            if process:
                pending.append((identity, process))
    for identity, process in pending:
        _reap(process)
        _cleanup_partial(service, identity)


def digest(path):
    """复用公共内容修订，保持新旧预览接口的目录身份完全一致。"""
    return revision(path)


def register(service, project, root, relative, task_id=None):
    """将受控文件登记为固定修订的资产。"""
    path = resolve(service, project, root, relative, task_id)
    rev = digest(path)
    identity = hashlib.sha256(f"{project}:{path}:{rev}".encode()).hexdigest()
    ref = {"project_id": project, "asset_id": identity, "revision": rev, "task_id": task_id}
    service.store.put(
        "asset",
        identity,
        {
            "ref": ref,
            "path": str(path),
            "kind": "source",
            "locator": {"root": root, "relative": relative, "task_id": task_id},
        },
    )
    return ref


def asset(service, project, ref):
    """验证资产项目和当前内容，不让旧引用冒充修改后的文件。"""
    record = service.store.get("asset", ref["asset_id"])
    if record["ref"]["project_id"] != project or ref.get("project_id", project) != project:
        raise ValueError("asset_project_mismatch")
    path = Path(record["path"])
    if record["kind"] == "source":
        locator = record["locator"]
        current = resolve(
            service, project, locator["root"], locator["relative"], locator.get("task_id")
        )
        if current != path:
            raise ValueError("asset_source_path_changed")
    elif (
        not path.resolve().is_relative_to((service.settings.root / "display").resolve())
        or path.is_symlink()
    ):
        raise ValueError("asset_display_outside_root")
    if (
        ref.get("revision", record["ref"]["revision"]) != record["ref"]["revision"]
        or digest(path) != record["ref"]["revision"]
    ):
        raise ValueError("asset_revision_conflict")
    return path


def get_operation(service, project, identity):
    """读取项目范围内操作，运行结束状态不可逆。"""
    value = service.store.get("operation", identity)
    if value["project_id"] != project:
        raise KeyError(identity)
    return value


def _subscribe(service, project, value, idempotency_key):
    """登记独立消费订阅，操作事实不混入单个查看器身份。"""
    identity = uuid4().hex
    service.store.put(
        "operation_subscription",
        identity,
        {
            "subscription_id": identity,
            "operation_id": value["operation_id"],
            "project_id": project,
            "active": True,
            "idempotency_key": idempotency_key,
            "fingerprint": value["fingerprint"],
        },
    )
    return {**value, "subscription_id": identity}


def submit(service, project, body, *, kind="visualization"):
    """固定来源与转换指纹共享独立 viz 进程，每个消费者登记独立订阅。"""
    source = body["source"]
    path = asset(service, project, source)
    record = service.store.get("asset", source["asset_id"])
    body = {**body, "options": dict(body.get("options", {}))}
    if "coordinate_space" in body["options"]:
        raise ValueError("coordinate_space_source_declaration_required")
    if source.get("member") is not None and record["kind"] == "display":
        member = Path(source["member"])
        child = (path / member).resolve()
        if (
            member.is_absolute()
            or not path.is_dir()
            or not child.is_relative_to(path.resolve())
            or any(p.startswith(".") for p in member.parts)
            or not child.is_file()
        ):
            raise ValueError("asset_member_outside_root")
        path = child
    if record.get("geometry") and source.get("member") == record.get("geometry_member"):
        body["options"]["geometry"] = record["geometry"]
    elif "geometry" in body["options"]:
        raise ValueError("geometry_declaration_required")
    canonical = {
        "protocol_version": 1,
        "kind": kind,
        "source": {
            key: source[key]
            for key in (
                "project_id",
                "asset_id",
                "revision",
                "task_id",
                "run_id",
                "member",
                "block",
            )
            if key in source
        },
        "operation": body.get("operation", "transform"),
        "options": body["options"],
    }
    fingerprint = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    with _LOCK:
        if body.get("idempotency_key"):
            for subscription in service.store.list("operation_subscription"):
                if (
                    subscription["project_id"] == project
                    and subscription.get("idempotency_key") == body["idempotency_key"]
                ):
                    if subscription["fingerprint"] != fingerprint:
                        raise ValueError("idempotency_conflict")
                    previous = get_operation(service, project, subscription["operation_id"])
                    return {**previous, "subscription_id": subscription["subscription_id"]}
        for old in service.store.list("operation"):
            if (
                old["project_id"] == project
                and old.get("fingerprint") == fingerprint
                and old["status"] in {"queued", "running", "succeeded"}
            ):
                if old["status"] == "succeeded":
                    try:
                        for ref in old["result_refs"]:
                            asset(service, project, ref)
                    except (ValueError, KeyError, FileNotFoundError):
                        continue
                return _subscribe(service, project, old, body.get("idempotency_key"))
        identity = uuid4().hex
        value = {
            "operation_id": identity,
            "project_id": project,
            "kind": kind,
            "status": "queued",
            "phase": None,
            "progress": None,
            "result_refs": [],
            "error": None,
            "event_cursor": 0,
            "fingerprint": fingerprint,
            "idempotency_key": body.get("idempotency_key"),
        }
        service.store.put("operation", identity, value)
        _ACTIVE.add(identity)
        response = _subscribe(service, project, value, body.get("idempotency_key"))
    threading.Thread(
        target=_execute, args=(service, project, identity, path, body), daemon=True
    ).start()
    return response


def _execute(service, project, identity, path, body):
    try:
        with _CAPACITY:
            return _execute_worker(service, project, identity, path, body)
    finally:
        with _LOCK:
            _ACTIVE.discard(identity)


def _execute_worker(service, project, identity, path, body):
    output = service.settings.root / "display" / identity
    output.mkdir(parents=True)
    request = {
        "protocol_version": 1,
        "request_id": identity,
        "operation": body.get("operation", "transform"),
        "source": {
            "path": str(path),
            "revision": body["source"]["revision"],
            "asset_ref": body["source"],
        },
        "options": body.get("options", {}),
        "output_dir": str(output),
    }
    timer = None
    timed_out = threading.Event()
    try:
        asset(service, project, body["source"])
        with _LOCK:
            value = get_operation(service, project, identity)
            if value["status"] in TERMINAL:
                return
            process = subprocess.Popen(
                [sys.executable, "-m", "ai4e_viz"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            _PROCESSES[identity] = process
            value.update(status="running", event_cursor=value["event_cursor"] + 1)
            service.store.put("operation", identity, value)

        def timeout():
            timed_out.set()
            if process.poll() is None:
                process.kill()

        timer = threading.Timer(120, timeout)
        timer.daemon = True
        timer.start()
        process.stdin.write(json.dumps(request))
        process.stdin.close()
        result = None
        for line in process.stdout:
            event = json.loads(line)
            with _LOCK:
                value = get_operation(service, project, identity)
                if value["status"] in TERMINAL:
                    return
                if event["type"] == "error":
                    raise ValueError(event["error"].get("message", "viz_failed"))
                if event["type"] == "result":
                    result = event["result"]
                value.update(
                    phase=event.get("phase", value["phase"]), event_cursor=value["event_cursor"] + 1
                )
                service.store.put("operation", identity, value)
        if timed_out.is_set():
            raise ValueError("viz_timeout")
        if process.wait(timeout=10) or result is None:
            raise ValueError("viz_process_failed")
        asset(service, project, body["source"])
        with _LOCK:
            value = get_operation(service, project, identity)
            if value["status"] in TERMINAL:
                return
            ref = {"project_id": project, "asset_id": identity, "revision": digest(output)}
            service.store.put(
                "asset", identity, {"ref": ref, "path": str(output), "kind": "display"}
            )
            value.update(
                status="succeeded",
                result_refs=[ref],
                result=result,
                event_cursor=value["event_cursor"] + 1,
            )
            service.store.put("operation", identity, value)
    except Exception as exc:  # noqa: BLE001 - 独立外部进程失败必须持久化供查询
        with _LOCK:
            value = get_operation(service, project, identity)
            if value["status"] not in TERMINAL:
                value.update(
                    status="failed",
                    error={"code": "operation_failed", "message": str(exc)},
                    event_cursor=value["event_cursor"] + 1,
                )
                service.store.put("operation", identity, value)
    finally:
        if timer:
            timer.cancel()
        with _LOCK:
            process = _PROCESSES.pop(identity, None)
        _reap(process)
        _cleanup_partial(service, identity)


def cancel(service, project, identity, subscription_id=None):
    """终止并回收操作进程，迟到结果不能覆盖取消状态。"""
    process = None
    with _LOCK:
        value = get_operation(service, project, identity)
        if subscription_id is not None:
            subscription = service.store.get("operation_subscription", subscription_id)
            if subscription["project_id"] != project or subscription["operation_id"] != identity:
                raise ValueError("operation_subscription_scope")
            subscription["active"] = False
            service.store.put("operation_subscription", subscription_id, subscription)
            if any(
                item["operation_id"] == identity and item["active"]
                for item in service.store.list("operation_subscription")
            ):
                return value
        if value["status"] not in TERMINAL:
            value.update(status="canceled", event_cursor=value["event_cursor"] + 1)
            service.store.put("operation", identity, value)
            process = _PROCESSES.pop(identity, None)
    _reap(process)
    _cleanup_partial(service, identity)
    return value


def recover_operations(service):
    """服务重启时标记失去监督的操作，不重放研究或显示计算。"""
    with _LOCK:
        for value in service.store.list("operation"):
            if value["status"] not in TERMINAL and value["operation_id"] not in _ACTIVE:
                value.update(
                    status="interrupted",
                    error={
                        "code": "service_restarted",
                        "message": "服务重启，操作未完成，请重新提交",
                    },
                    event_cursor=value["event_cursor"] + 1,
                )
                service.store.put("operation", value["operation_id"], value)


def submit_model_inspection(
    service,
    project,
    task_id,
    revision,
    selection,
    inputs,
    idempotency_key=None,
    operation="trace_model",
):
    """异步调用 task 检查门面，结构资产固定配置和输入来源。"""
    identity = uuid4().hex
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "task_id": task_id,
                "revision": revision,
                "selection": selection,
                "inputs": inputs,
                "operation": operation,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    with _LOCK:
        if idempotency_key:
            for old in service.store.list("operation"):
                if old["project_id"] == project and old.get("idempotency_key") == idempotency_key:
                    if old["fingerprint"] != fingerprint:
                        raise ValueError("idempotency_conflict")
                    return old
        value = {
            "operation_id": identity,
            "project_id": project,
            "kind": operation,
            "task_id": task_id,
            "created_at": datetime.now(UTC).isoformat(),
            "revision": revision,
            "stage": selection.get("stage", "model" if operation == "trace_model" else None),
            "inputs": inputs,
            "status": "queued",
            "phase": None,
            "progress": None,
            "result_refs": [],
            "error": None,
            "event_cursor": 0,
            "fingerprint": fingerprint,
            "idempotency_key": idempotency_key,
        }
        service.store.put("operation", identity, value)
        _ACTIVE.add(identity)

    def execute():
        import ai4e_task as task

        output = service.settings.root / "display" / identity
        try:
            with _CAPACITY:
                with _LOCK:
                    state = get_operation(service, project, identity)
                    if state["status"] in TERMINAL:
                        return
                    state.update(
                        status="running",
                        phase=operation,
                        event_cursor=state["event_cursor"] + 1,
                    )
                    service.store.put("operation", identity, state)
                for ref in inputs:
                    asset(service, project, ref)
                output.mkdir(parents=True)

                def started(process):
                    with _LOCK:
                        if get_operation(service, project, identity)["status"] in TERMINAL:
                            process.terminate()
                        _PROCESSES[identity] = process

                result = task.inspect_task(
                    service.project(project),
                    task_id,
                    operation,
                    revision=revision,
                    selection=selection,
                    output_dir=str(output),
                    on_process_started=started,
                )
                for ref in inputs:
                    asset(service, project, ref)
                with _LOCK:
                    state = get_operation(service, project, identity)
                    if state["status"] in TERMINAL:
                        return
                    ref = {
                        "project_id": project,
                        "asset_id": identity,
                        "revision": digest(output),
                        "task_id": task_id,
                    }
                    asset_record = {"ref": ref, "path": str(output), "kind": "display"}
                    if operation == "compare_fields":
                        metadata = json.loads((output / "difference.json").read_text())
                        asset_record["geometry_member"] = "difference.pt"
                        asset_record["geometry"] = {
                            "kind": "tensor_points",
                            "coordinates": "coordinates",
                            "field": "values",
                            "ids": "ids",
                            "association": metadata["association"],
                            "unit": metadata["unit"],
                            "entity_set": metadata["entity_set"],
                        }
                        if metadata.get("coordinate_space") is not None:
                            asset_record["geometry"]["coordinate_space"] = metadata[
                                "coordinate_space"
                            ]
                        ref["member"] = "difference.pt"
                    service.store.put("asset", identity, asset_record)
                    if operation == "compare_fields":
                        result["member"] = "difference.pt"
                        result["metadata_member"] = "difference.json"
                        result.pop("metadata_path", None)
                    result.pop("path", None)
                    if operation == "trace_model":
                        result["member"] = "model.html"
                    result["configuration_revision"] = revision
                    state.update(
                        status="succeeded",
                        result=result,
                        result_refs=[ref] if any(output.iterdir()) else [],
                        event_cursor=state["event_cursor"] + 1,
                    )
                    service.store.put("operation", identity, state)
        except Exception as exc:  # noqa: BLE001 - 辅助进程失败必须保存
            with _LOCK:
                state = get_operation(service, project, identity)
                if state["status"] not in TERMINAL:
                    state.update(
                        status="failed",
                        error={"code": "model_inspection_failed", "message": str(exc)},
                        event_cursor=state["event_cursor"] + 1,
                    )
                    service.store.put("operation", identity, state)
        finally:
            with _LOCK:
                _ACTIVE.discard(identity)
                process = _PROCESSES.pop(identity, None)
            _reap(process)
            _cleanup_partial(service, identity)

    threading.Thread(target=execute, daemon=True).start()
    return value


def archive_asset(service, project, ref):
    """按固定修订打包目录资产，保留隐藏元数据；拒绝链接并原子发布缓存。"""
    import os
    import stat
    import zipfile

    root = asset(service, project, ref)
    if not root.is_dir():
        raise ValueError("directory_required")
    output = service.settings.root / "downloads"
    output.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(
        json.dumps({"project": project, "ref": ref}, sort_keys=True).encode()
    ).hexdigest()
    target = output / (key + ".zip")
    if not target.exists():
        temporary = output / (uuid4().hex + ".tmp")
        try:
            with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(root.rglob("*")):
                    if path.is_symlink() or not path.resolve().is_relative_to(root):
                        raise ValueError("asset_symlink_forbidden")
                    relative = path.relative_to(root).as_posix()
                    if path.is_dir():
                        archive.writestr(relative + "/", b"")
                    elif path.is_file():
                        # 不跟随读取期间被替换的链接，目录内容发布前再次核验修订。
                        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                        with os.fdopen(descriptor, "rb") as source:
                            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                                raise ValueError("asset_regular_file_required")
                            with archive.open(relative, "w") as destination:
                                shutil.copyfileobj(source, destination)
            asset(service, project, ref)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    asset(service, project, ref)
    return target, root.name + ".zip"
