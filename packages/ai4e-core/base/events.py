"""能力事件、阶段上下文与真实耗时；只发日志，由运行写入方连接文件。"""

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


def event(name: str, state: str, /, **details) -> None:
    """记录小型事实字段，不接受数组和整个上下文作为日志载荷。"""
    if SAMPLE.get():
        details = {"样本": SAMPLE.get(), **details}
    text = "；".join(f"{k}={v}" for k, v in details.items())
    LOGGER.info(text, extra={"operation": name, "event_state": state})


@contextmanager
def operation(name: str, /, **details):
    """记录开始、结束、失败与耗时；不可分块计算报告运行中而非虚构百分比。"""
    started = time.monotonic()
    stopped = threading.Event()
    event(name, "开始", **details)

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
        event(name, "结束", 耗时=f"{time.monotonic() - started:.3f}秒")
    finally:
        stopped.set()
        worker.join()


def traced(name: str):
    """为独立公开能力提供埋点，不改变输入输出契约。"""

    def decorate(fn):
        @functools.wraps(fn)
        def call(*args, **kwargs):
            details = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float))}
            if args and isinstance(args[0], (str, os.PathLike)):
                details["来源"] = str(args[0])
            for index, value in enumerate(args):
                if hasattr(value, "shape"):
                    details[f"输入{index}形状"] = tuple(value.shape)
            with operation(name, **details):
                result = fn(*args, **kwargs)
                if hasattr(result, "shape"):
                    event(name, "结果", 形状=tuple(result.shape), 类型=str(result.dtype))
                elif hasattr(result, "GetNumberOfPoints"):
                    event(
                        name,
                        "结果",
                        点数=result.GetNumberOfPoints(),
                        单元数=result.GetNumberOfCells(),
                    )
                return result

        return call

    return decorate
