"""能力事件、阶段上下文与真实耗时；只发日志，由运行写入方连接文件。

常规 info 留给 application 阶段、批量摘要与稀疏进度。循环内原子能力
默认 debug，避免每个样本的读取/提交刷屏；失败仍记错误。
"""

import contextvars
import functools
import logging
import os
import threading
import time
from contextlib import contextmanager

LOGGER = logging.getLogger("ai4e_core.run")
SAMPLE = contextvars.ContextVar("ai4e_sample", default="")
PHASE = contextvars.ContextVar("ai4e_phase", default="")
INTERVAL = 10.0
ATOMIC_LEVEL = logging.DEBUG


class _EventContext(logging.Filter):
    def filter(self, record):
        record.recipe_phase = PHASE.get()
        name = getattr(record, "operation", "")
        state = getattr(record, "event_state", "")
        parts = [part for part in (record.recipe_phase, name, state) if part]
        if parts:
            record.msg = "[" + "/".join(parts) + "] " + record.getMessage()
            record.args = ()
        return True


LOGGER.addFilter(_EventContext())


@contextmanager
def sample_context(name: str, samples: list[dict]):
    """给操作附加准确样本身份；批次失败保留全部身份，退出恢复外层上下文。"""
    identity = [
        {
            "sample_id": item.get("sample_id", item.get("sample")),
            "index": item.get("index"),
            **{key: item[key] for key in ("partition", "source", "chunk", "offset") if key in item},
        }
        for item in samples
    ]
    if any(not item["sample_id"] for item in identity):
        raise ValueError("样本异常上下文需要真实样本身份")
    token = SAMPLE.set(str(identity))
    try:
        yield
    except Exception as exc:
        if not hasattr(exc, "dojo_context"):
            exc.dojo_context = {"stage": PHASE.get(), "operation": name, "samples": identity}
            exc.add_note(f"阶段={PHASE.get()}；操作={name}；样本={identity}")
            LOGGER.error(
                "样本=%s；原因=%s",
                identity,
                exc,
                extra={"operation": name, "event_state": "失败"},
            )
        raise
    finally:
        SAMPLE.reset(token)


@contextmanager
def phase(name: str):
    """由运行入口限定阶段上下文；嵌套调用和异常退出均恢复先前阶段。"""
    token = PHASE.set(name)
    try:
        yield
    finally:
        PHASE.reset(token)


def event(name: str, state: str, /, *, level: int = logging.INFO, **details) -> None:
    """记录小型事实字段，不接受数组和整个上下文作为日志载荷。

    Args:
        name: 能力或阶段名。
        state: 事件状态，如开始、结束、进度。
        level: 日志等级；循环原子传 ``ATOMIC_LEVEL``。
        **details: 小型可打印字段。
    """
    if SAMPLE.get():
        details = {"样本": SAMPLE.get(), **details}
    text = "；".join(f"{k}={v}" for k, v in details.items())
    LOGGER.log(level, text, extra={"operation": name, "event_state": state})


@contextmanager
def operation(name: str, /, *, level: int = logging.INFO, **details):
    """记录开始、结束、失败与耗时；不可分块计算报告运行中而非虚构百分比。

    ``level`` 低于 INFO 时不启动心跳，供循环内逐步调用使用。失败仍记
    错误。长任务心跳只在 INFO 级操作上每十秒发一次，不虚构百分比。
    """
    started = time.monotonic()
    event(name, "开始", level=level, **details)
    stopped = threading.Event()
    worker = None
    if level >= logging.INFO:

        def heartbeat():
            while not stopped.wait(INTERVAL):
                event(
                    name,
                    "运行中",
                    已耗时=f"{time.monotonic() - started:.2f}秒",
                    状态="底层计算尚未返回",
                )

        # 新线程不自动继承 ContextVar，捕获阶段与样本身份后显式传递。
        context = contextvars.copy_context()
        worker = threading.Thread(target=context.run, args=(heartbeat,), daemon=True)
        worker.start()
    try:
        yield
    except Exception as exc:
        LOGGER.error(
            "样本=%s；原因=%s；耗时=%.3f秒",
            SAMPLE.get(),
            exc,
            time.monotonic() - started,
            extra={"operation": name, "event_state": "失败"},
        )
        raise
    else:
        event(name, "结束", level=level, 耗时=f"{time.monotonic() - started:.3f}秒")
    finally:
        if worker is not None:
            stopped.set()
            worker.join()


def traced(name: str):
    """为独立公开能力提供 debug 埋点，不改变输入输出契约，不感知 recipe。"""

    def decorate(fn):
        @functools.wraps(fn)
        def call(*args, **kwargs):
            details = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float))}
            if args and isinstance(args[0], (str, os.PathLike)):
                details["来源"] = str(args[0])
            for index, value in enumerate(args):
                if hasattr(value, "shape"):
                    details[f"输入{index}形状"] = tuple(value.shape)
            with operation(name, level=ATOMIC_LEVEL, **details):
                result = fn(*args, **kwargs)
                if hasattr(result, "shape"):
                    event(
                        name,
                        "结果",
                        level=ATOMIC_LEVEL,
                        形状=tuple(result.shape),
                        类型=str(result.dtype),
                    )
                elif hasattr(result, "GetNumberOfPoints"):
                    event(
                        name,
                        "结果",
                        level=ATOMIC_LEVEL,
                        点数=result.GetNumberOfPoints(),
                        单元数=result.GetNumberOfCells(),
                    )
                return result

        return call

    return decorate
