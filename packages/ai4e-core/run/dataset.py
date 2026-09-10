"""按需 Dataset 的通用顺序执行器：样本隔离、失败传播与轻量汇总。"""

import time
from copy import deepcopy

from ai4e_core.applications.base import Stage, StageError
from ai4e_core.base.events import LOGGER, SAMPLE, event, operation

from .execute import BatchExecutionError


def execute(data, *, save, output, settings=None) -> dict:
    """执行数据视图；settings 为调用方交给保存策略的参数，执行器不解释业务字段。"""
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
        session.setdefault("reports", {})["dataset"] = {
            "manifest": data.metadata.get("manifest_path"),
            "definition": deepcopy(data.metadata),
            "partitions": {k: list(v) for k, v in data.partitions.items()},
        }
    if hasattr(save, "begin"):
        save.begin(data, output, flags=flags)
    partitions = {s: k for k, values in data.partitions.items() for s in values}
    last_progress = time.monotonic()
    with operation("批量前处理", 样本数=len(data.samples)):
        for sample in data.samples:
            summary["attempted"] += 1
            summary["unexecuted"] -= 1
            token = SAMPLE.set(sample)
            try:
                result = _one(data, sample, partitions[sample], save, output, flags)
                summary["results"].append(result)
                summary["success"] += 1
            except Exception as exc:
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
                if not flags["continue_on_error"]:
                    raise BatchExecutionError(summary) from exc
                del cause
            finally:
                SAMPLE.reset(token)
            if time.monotonic() - last_progress >= 10 or summary["unexecuted"] == 0:
                event(
                    "批量前处理",
                    "进度",
                    完成=summary["success"],
                    总数=summary["total"],
                    失败=summary["failed"],
                    未执行=summary["unexecuted"],
                )
                last_progress = time.monotonic()
    return summary


def _one(data, sample, partition, save, output, flags):
    """单样本栈帧结束后释放所有网格/数组；只返回保存策略的轻量结果。"""
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
