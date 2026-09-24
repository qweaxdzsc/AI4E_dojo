"""任务内固定结果评价管理；只交接引用，数值与数据文件交给core。"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..projects.project import open_project
from ..storage.database import transaction
from ..storage.files import read_json, write_json
from ..storage.layout import inside, task_dir
from ..storage.records import fetch, get, listing, put, remember, replay
from ..storage.snapshots import digest
from .operation_sources import verify_source, with_operation
from .post_results import freeze_result_item, post_results
from .records import get_task

TERMINAL = {"succeeded", "partial", "failed", "canceled", "interrupted"}


def _folder(project, task, identity):
    return inside(task_dir(project, task) / ".dojo/post_metrics", identity)


def metric_catalog():
    """在检查子进程查询core指标目录，管理进程不加载算法栈。"""
    from ai4e_core.abilities.eval.catalog import metric_catalog as catalog

    return catalog()


def _writable(project, task_id):
    task = get_task(project, task_id)
    if task.get("archived") or open_project(project).get("archived"):
        raise ValueError("archived")
    return task


def submit_post_metrics(project, task_id, request):
    """固定结果、指标选择与修订，提交幂等后台评价。"""
    project = Path(project).resolve()
    task = _writable(project, task_id)
    if set(request) - {"results", "fields", "metrics", "idempotency_key"}:
        raise ValueError("未知评价参数")
    key = request.get("idempotency_key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("缺少评价请求身份")
    fingerprint = digest({"task": task_id, "request": request})
    with transaction(project) as db:
        prior = replay(db, key, fingerprint)
    if prior:
        return read_post_metrics(project, task_id, prior["id"])
    catalog = post_results(project, task_id)
    candidates = {v["id"]: v for v in catalog["items"]}
    inputs = []
    for ref in request.get("results", []):
        item = candidates.get(ref["id"])
        if item is None or not item["evaluable"]:
            raise ValueError("结果不存在或缺少评价证据")
        if item["revision"] != ref.get("revision"):
            raise ValueError("post_result_revision_conflict")
        if item["id"] in {v["id"] for v in inputs}:
            raise ValueError("结果选择重复")
        inputs.append(freeze_result_item(item))
    fields = {f["id"]: f for i in inputs for f in i["fields"]}
    chosen = request.get("fields", [])
    metrics = request.get("metrics", [])
    if (
        not inputs
        or not chosen
        or not metrics
        or len(metrics) != len(set(metrics))
        or set(metrics) - {m["id"] for m in metric_catalog()}
    ):
        raise ValueError("结果、物理量和指标必须有效且非空")
    if len(chosen) != len(set(chosen)) or set(chosen) - fields.keys():
        raise ValueError("物理量选择不存在或重复")
    identity, run_id = uuid4().hex, uuid4().hex
    root = task_dir(project, task_id)
    contexts = [item.get("operation_context") for item in inputs]
    if any(not context for context in contexts):
        raise ValueError("operation_unavailable: captured_application_source_missing")
    source = with_operation(contexts[0]["source"], "evaluate")
    if any(with_operation(context["source"], "evaluate") != source for context in contexts):
        raise ValueError("post_application_sources_differ")
    from ..storage.snapshots import snapshot

    verify_source(source, contexts[0]["recipe"])
    code = _folder(project, task_id, identity) / "code"
    now = datetime.now(UTC).isoformat()
    job = {
        "id": identity,
        "target": source["target"],
        "operation_context": {"source": source, "recipe": str(code)},
        "task_id": task_id,
        "version_id": task["version_id"],
        "run_id": run_id,
        "run_dir": str(root / "runs" / run_id),
        "data_dir": str(root / "data/post" / identity),
        "inputs": inputs,
        "request": {**request, "fields": [fields[f] for f in chosen]},
        "created_at": now,
        "status": "pending",
        "completed": 0,
        "failed": 0,
        "total": len(inputs) * len(chosen),
        "exports": [],
    }
    with transaction(project) as db:
        prior = replay(db, key, fingerprint)
        if prior:
            return prior
        try:
            snapshot(Path(contexts[0]["recipe"]), code)
            verify_source(source, code)
            write_json(_folder(project, task_id, identity) / "request.json", job)
        except BaseException:
            import shutil

            shutil.rmtree(code.parent, ignore_errors=True)
            raise
        put(db, "post_metric_job", job)
        put(
            db,
            "run",
            {
                "id": run_id,
                "task_id": task_id,
                "version_id": task["version_id"],
                "run_path": str(Path(job["run_dir"]).relative_to(project)),
                "data_path": str(Path(job["data_dir"]).relative_to(project)),
                "status": "pending",
                "stages": ["post"],
                "created_at": now,
                "metadata": {"purpose": "post_metrics"},
                "operation_mode": "execute",
            },
        )
        remember(db, key, fingerprint, "post_metric_job", identity)
    try:
        with (_folder(project, task_id, identity) / "worker.log").open("ab") as log:
            proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "ai4e_task.tasks.post_metrics_worker",
                    str(project),
                    task_id,
                    identity,
                ],
                cwd=code,
                stdout=log,
                stderr=log,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
        with transaction(project) as db:
            value = get(db, "post_metric_job", identity)
            put(db, "post_metric_job", {**value, "pid": proc.pid}, replace=True)
    except Exception as exc:  # noqa: BLE001 - 启动失败必须持久化，避免留下永久等待记录。
        update_post_metrics(project, identity, {"status": "failed", "error": str(exc)})
    return read_post_metrics(project, task_id, identity)


def update_post_metrics(project, identity, changes):
    """原子发布管理状态与运行状态，不写core运行报告。"""
    with transaction(project) as db:
        job = get(db, "post_metric_job", identity)
        job.update(changes)
        put(db, "post_metric_job", job, replace=True)
        if "status" in changes:
            run = get(db, "run", job["run_id"])
            put(db, "run", {**run, "status": changes["status"]}, replace=True)


def read_post_metrics(project, task_id, identity):
    """读取已提交行，并核对意外结束进程；不自动重新运行未知计算。"""
    get_task(project, task_id)
    job = fetch(project, "post_metric_job", identity)
    if job["task_id"] != task_id:
        raise ValueError("post_metric_task_mismatch")
    if job["status"] not in TERMINAL and job.get("pid"):
        process = subprocess.run(
            ["ps", "-p", str(job["pid"]), "-o", "args="],
            capture_output=True,
            text=True,
            check=False,
        )
        if identity not in process.stdout or "post_metrics_worker" not in process.stdout:
            update_post_metrics(
                project,
                identity,
                {"status": "interrupted", "error": "评价进程已中断；可显式重新计算"},
            )
            job = fetch(project, "post_metric_job", identity)
    path = Path(job["data_dir"]) / "metrics.json"
    result = read_json(path) if path.exists() else {"rows": []}
    journal = path.with_suffix(".jsonl")
    if not path.exists() and journal.exists():
        with journal.open(encoding="utf-8") as stream:
            for line in stream:
                if line.endswith("\n"):
                    result["rows"].extend(json.loads(line))
    return {**job, "rows": result["rows"]}


def list_post_metrics(project, task_id):
    """列出当前任务的评价记录。"""
    get_task(project, task_id)
    return [
        read_post_metrics(project, task_id, j["id"])
        for j in listing(project, "post_metric_job")
        if j["task_id"] == task_id
    ]


def cancel_post_metrics(project, task_id, identity):
    """请求在样本边界停止，不终止训练或推理进程。"""
    _writable(project, task_id)
    value = read_post_metrics(project, task_id, identity)
    if value["status"] not in TERMINAL:
        write_json(_folder(project, task_id, identity) / "cancel.json", {"requested": True})
    return value


def export_post_metrics(project, task_id, identity, request):
    """只向任务评价目录导出固定结果，拒绝任意输出路径。"""
    _writable(project, task_id)
    job = read_post_metrics(project, task_id, identity)
    if job["status"] not in TERMINAL:
        raise ValueError("请等待评价结束后导出")
    format = request.get("format", "csv")
    if format not in {"csv", "json", "xlsx"} or set(request) - {"format", "row_ids"}:
        raise ValueError("导出参数无效")
    name = "export-" + uuid4().hex + "." + format
    path = Path(job["data_dir"]) / name
    payload = {
        "operation_context": {
            **job["operation_context"],
            "source": with_operation(job["operation_context"]["source"], "export"),
        },
        "record": str(Path(job["data_dir"]) / "metrics.json"),
        "path": str(path),
        "format": format,
        "row_ids": request.get("row_ids"),
    }
    result = subprocess.run(
        [sys.executable, "-m", "ai4e_task.tasks.post_metrics_worker", "--export"],
        cwd=job["operation_context"]["recipe"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip().splitlines()[-1])
    with transaction(project) as db:
        current = get(db, "post_metric_job", identity)
        current["exports"].append({"name": name, "format": format})
        put(db, "post_metric_job", current, replace=True)
    return {"path": str(path), "name": name}
