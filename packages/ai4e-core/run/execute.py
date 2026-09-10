"""顺序批量执行机制，只认识样本引用、Stage 和轻量结果。"""

from collections.abc import Callable, Sequence

from ai4e_core.applications.base import Stage, StageError


class BatchExecutionError(RuntimeError):
    """首错停止，并携带已经完成的批量摘要。"""

    def __init__(self, summary):
        self.summary = summary
        super().__init__(f"样本执行失败: {summary['failures'][-1]}")


def execute_many(
    items: Sequence, stage: Stage, *, context: dict, continue_on_error: bool = False
) -> dict:
    """逐样本运行并丢弃数组上下文；失败保留样本和原业务步骤。"""
    summary = {
        "total": len(items),
        "attempted": 0,
        "success": 0,
        "failed": 0,
        "unexecuted": len(items),
        "failures": [],
        "results": [],
        "names": [],
    }
    context["batch"] = summary
    for item in items:
        summary["attempted"] += 1
        summary["unexecuted"] -= 1
        sample_ctx = {k: v for k, v in context.items() if k not in ("batch", "items", "reports")}
        sample_ctx["sample"] = item
        try:
            result = stage.run(sample_ctx)["result"]
        except Exception as exc:
            cause = exc.cause if isinstance(exc, StageError) else exc
            failure = {
                "sample": str(item),
                "error": str(cause),
                "step": exc.step_name if isinstance(exc, StageError) else "result",
                "stage": exc.stage if isinstance(exc, StageError) else stage.name,
            }
            if hasattr(cause, "report"):
                failure["validation"] = cause.report
            summary["failures"].append(failure)
            summary["failed"] += 1
            if not continue_on_error:
                raise BatchExecutionError(summary) from exc
        else:
            summary["results"].append(result)
            summary["success"] += 1
            summary["names"] = sorted(set(summary["names"]) | set(result.get("names", [])))
    return summary


def for_each(stage: Stage) -> Callable[[dict], dict]:
    """将单样本 Stage 包成作业 Stage 的一步，不引入第二种执行容器。"""

    def execute_samples(ctx):
        execute_many(
            ctx["items"], stage, context=ctx, continue_on_error=ctx.get("continue_on_error", False)
        )
        return ctx

    return execute_samples
