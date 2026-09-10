"""最小模型组件协议；只声明调用要求，不引入统一张量格式。"""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ModelRequirements:
    """跨包声明必需输入名称与支持的最大批次数。"""

    input_names: tuple[str, ...]
    max_batch_size: int | None
    optional_input_names: tuple[str, ...] = ()


class ModelFactory(Protocol):
    """用户构造器协议，不要求继承框架基类。"""

    def __call__(self, **parameters: Any) -> Any:
        """用模型自身参数构造网络。"""
        ...


class ModelComponent(Protocol):
    """模型组件公开结构声明和具名预测，不要求继承或统一网络实现。"""

    def construct(self, **parameters: Any) -> Any:
        """只消费模型自身参数。"""
        ...

    def describe(self, model: Any) -> dict[str, Any]:
        """返回稳定的输入输出及结构声明，不暴露内部属性。"""
        ...

    def predict(self, model: Any, inputs: dict[str, Any]) -> dict[str, Any]:
        """消费具名输入并返回具名预测。"""
        ...


def describe_model(factory: Any, model: Any) -> dict[str, Any]:
    """读取构造器提供的描述回调；禁止框架猜测具体网络属性。"""
    callback = getattr(factory, "describe", None)
    if not callable(callback):
        raise TypeError("模型构造器必须通过 describe 回调提供结构契约")
    return callback(model)
