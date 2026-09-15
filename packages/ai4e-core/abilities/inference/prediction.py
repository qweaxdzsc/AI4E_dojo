"""单次预测原语，不认识案例配置、数据集和输出目录。"""

from collections.abc import Callable
from typing import Any

from .execution import inference_execution


def predict(
    model, inputs: Any, *args: Any, operation: Callable, preserve_rng: bool = True, **kwargs
) -> Any:
    """调用注入的预测函数，禁止梯度并恢复模式；不改写函数的输出语义。"""
    with inference_execution(model, preserve_rng=preserve_rng):
        return operation(model, inputs, *args, **kwargs)
