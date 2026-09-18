"""训练内部共享推进；预算与实际更新分离，不解释模型或领域。"""

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UpdateEvent:
    """一次工作单元完成的事实；index 是本次调用的零基工作序号。"""

    index: int
    result: Any
    advanced: bool
    updates: int


def execute(
    work: Iterable,
    advance: Callable,
    *,
    start: int = 0,
    updates: int | None = None,
    before: Callable | None = None,
) -> Iterator[UpdateEvent]:
    """按真实更新预算推进；调用方在 yield 边界执行原有观察和持久化。

    before 在取下一个工作单元前执行；预算完成不额外取数。
    有限数据源耗尽不伪造剩余更新；轮次生命周期由调用方保留。
    """
    if start < 0 or (updates is not None and updates < start):
        raise ValueError("有效更新预算非法")
    completed, index = start, 0
    iterator = iter(work)
    while updates is None or completed < updates:
        if before is not None:
            before(completed)
        try:
            value = next(iterator)
        except StopIteration:
            return
        result, advanced = advance(index, value)
        if type(advanced) is not bool:
            raise TypeError("更新函数须返回布尔有效更新标记")
        completed += int(advanced)
        yield UpdateEvent(index, result, advanced, completed)
        index += 1
