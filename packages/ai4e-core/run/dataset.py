"""按需 Dataset 的通用执行器：样本隔离、可选并行、失败传播与轻量汇总。"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from copy import deepcopy

from ai4e_core.applications.base import Stage, StageError
from ai4e_core.base.events import LOGGER, SAMPLE, event, operation

from .execute import BatchExecutionError


def _workers(settings) -> int:
    """只读取执行线程数；不解释物理字段。缺省 1，范围 1–64。"""
    raw = settings.get("rawprep") if isinstance(settings, dict) else None
    source = raw if isinstance(raw, dict) else settings if isinstance(settings, dict) else {}
    value = source.get("workers", 1)
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 64:
        raise ValueError("rawprep.workers: 需要 1 到 64 的整数")
    return value


def execute(data, *, save, output, settings=None) -> dict:
    """执行数据视图；settings 交给保存策略，workers 只控制并行样本数。"""
    from .session import CURRENT

    session = CURRENT.get()
    flags = (
        session["flags"]
        if session
        else {"dry_run": False, "overwrite": False, "continue_on_error": False}
    )
    settings = (
        deepcopy(settings) if settings is not None else (session["config"] if session else {})
    )
    output = dict(output)
    workers = _workers(settings)
    if hasattr(save, "preflight"):
        with operation("输出预检"):
            save.preflight(data, output, flags=flags, settings=settings)
    summary = {
        "dataset": data,
        "output": output,
        **flags,
        "total": len(data.samples),
        "attempted": 0,
        "success": 0,
        "failed": 0,
        "unexecuted": len(data.samples),
        "results": [],
        "failures": [],
    }
    if session is not None:
        session["batch"] = summary
    if session is not None:
        session["writer"].write_operation_sources(data.metadata.get("extensions", []))
        session.setdefault("reports", {})["dataset"] = {
            "manifest": data.metadata.get("manifest_path"),
            "definition": deepcopy(data.metadata),
            "partitions": {k: list(v) for k, v in data.partitions.items()},
        }
    if hasattr(save, "begin"):
        save.begin(data, output, flags=flags)
    partitions = {s: k for k, values in data.partitions.items() for s in values}
    last_progress = time.monotonic()
    lock = threading.Lock()

    def emit_progress(*, force=False):
        nonlocal last_progress
        if not force and time.monotonic() - last_progress < 10 and summary["unexecuted"] != 0:
            return
        event(
            "批量前处理",
            "进度",
            完成=summary["success"],
            总数=summary["total"],
            失败=summary["failed"],
            未执行=summary["unexecuted"],
        )
        last_progress = time.monotonic()

    def record(sample, result=None, exc=None):
        token = SAMPLE.set(sample)
        try:
            summary["attempted"] += 1
            summary["unexecuted"] -= 1
            if exc is None:
                summary["results"].append(result)
                summary["success"] += 1
                emit_progress(force=summary["unexecuted"] == 0)
                return
            cause = exc.cause if isinstance(exc, StageError) else exc
            LOGGER.exception("样本失败：%s", cause)
            summary["failed"] += 1
            summary["failures"].append(
                {
                    "sample": sample,
                    "step": getattr(exc, "step_name", "保存"),
                    "error": str(cause),
                }
            )
            emit_progress(force=summary["unexecuted"] == 0 or not flags["continue_on_error"])
        finally:
            SAMPLE.reset(token)

    with operation("批量前处理", 样本数=len(data.samples)):
        if workers == 1:
            for sample in data.samples:
                try:
                    record(
                        sample,
                        result=_one(data, sample, partitions[sample], save, output, flags),
                    )
                except Exception as exc:
                    record(sample, exc=exc)
                    if not flags["continue_on_error"]:
                        raise BatchExecutionError(summary) from exc
            return summary
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_one, data, sample, partitions[sample], save, output, flags): sample
                for sample in data.samples
            }
            error = None
            seen = set()
            for future in as_completed(futures):
                sample = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    with lock:
                        seen.add(future)
                        record(sample, exc=exc)
                    if not flags["continue_on_error"]:
                        error = exc
                        for other in futures:
                            other.cancel()
                        break
                else:
                    with lock:
                        seen.add(future)
                        record(sample, result=result)
            if error is not None:
                pending = [item for item in futures if item not in seen]
                wait(pending)
                for future in pending:
                    if future.cancelled() or not future.done():
                        continue
                    sample = futures[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        with lock:
                            record(sample, exc=exc)
                    else:
                        with lock:
                            record(sample, result=result)
                raise BatchExecutionError(summary) from error
    return summary


def _one(data, sample, partition, save, output, flags):
    """单样本栈帧结束后释放所有网格/数组；只返回保存策略的轻量结果。"""
    token = SAMPLE.set(sample)
    try:
        ctx = {
            "config": deepcopy(data.options["config"]),
            "sample": sample,
            "partition": partition,
            **flags,
        }
        steps = []
        for name, fn in data.steps:

            def call(current, fn=fn, name=name):
                with operation("样本" + name):
                    return fn(current)

            call.__name__ = name
            steps.append(call)
        ctx = Stage("pre", steps).run(ctx)
        with operation("样本提交", 分片=partition):
            return save(ctx, output=output)
    finally:
        SAMPLE.reset(token)
