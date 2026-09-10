"""阶段盒子：按顺序执行内部步骤。"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial
from typing import Any


class StageError(RuntimeError):
    """阶段内某一步失败。"""

    def __init__(self, stage: str, step_name: str, index: int, cause: BaseException) -> None:
        super().__init__(f"阶段 {stage} 的步骤 {step_name} 失败")
        self.stage = stage
        self.step_name = step_name
        self.index = index
        self.cause = cause


class Stage:
    """一条业务阶段的盒子，执行时只做 ``ctx = step(ctx)``。"""

    def __init__(self, name: str, steps: Sequence[Callable[[Any], Any]]) -> None:
        if not name:
            raise ValueError("阶段名不能为空")
        self.name = name
        self.steps = list(steps)

    def run(self, ctx: Any) -> Any:
        """按顺序调用步骤；一步失败则停止。

        Args:
            ctx: 作业上下文，通常是映射。

        Returns:
            最后一步返回的上下文。

        Raises:
            StageError: 某一步抛错。
        """
        current = ctx
        for index, step in enumerate(self.steps):
            named = step.func if isinstance(step, partial) else step
            step_name = getattr(named, "__name__", type(named).__name__)
            try:
                current = step(current)
            except StageError as exc:
                if not hasattr(exc, "context"):
                    exc.context = current
                raise
            except Exception as exc:
                error = StageError(self.name, step_name, index, exc)
                error.context = current
                raise error from exc
        return current
