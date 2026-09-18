"""独立操作的执行外围；不解释领域字段或模型输入输出。"""

import logging
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, TypeVar

from .writer import RunWriter

Item = TypeVar("Item")
Result = TypeVar("Result")


class OperationRun:
    """为任务子运行提供日志、取消、样本执行和产物写入。"""

    def __init__(
        self,
        writer: RunWriter,
        logger: logging.Logger,
        publish: Callable[[dict], None],
        canceled: Callable[[], bool],
    ) -> None:
        self.writer = writer
        self.logger = logger
        self.publish = publish
        self.canceled = canceled

    def execute_samples(
        self, samples: Iterable[Item], process: Callable[[Item], Result]
    ) -> Iterator[Result]:
        """按输入顺序执行普通函数；返回值保持原样，在样本边界响应取消。"""
        for sample in samples:
            if self.canceled():
                break
            yield process(sample)

    def artifact(self, name: str, value: dict) -> Path:
        """由唯一 writer 原子提交运行产物。"""
        return self.writer.write_artifact(name, value)


def execute_operation(
    job: dict,
    operation: Callable[..., dict[str, Any]],
    *,
    publish: Callable[[dict], None],
    canceled: Callable[[], bool],
) -> dict[str, Any]:
    """建立独立运行后调用领域操作；领域返回状态，运行器负责收尾。"""
    directory = Path(job["run_dir"])
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "inputs").mkdir()
    (directory / "logs").mkdir()
    writer = RunWriter(directory)
    writer.write_inputs(None, job["request"])
    writer.write_provenance({k: job[k] for k in ("run_id", "task_id", "version_id")})
    logger = logging.getLogger("dojo.operation." + job["id"])
    handler = writer.attach_log(logger)
    runtime = OperationRun(writer, logger, publish, canceled)
    try:
        result = operation(job, runtime=runtime)
        status = result["status"]
        writer.write_summary(
            {
                "failed": status != "succeeded",
                "reports": {job.get("stage", "post"): {"status": status}},
                "run_dir": str(directory),
            }
        )
        return result
    except BaseException as exc:
        writer.write_summary({"failed": True, "error": str(exc), "reports": {}})
        raise
    finally:
        logger.removeHandler(handler)
        handler.close()
