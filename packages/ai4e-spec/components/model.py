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


class PreparedModelComponent(ModelComponent, Protocol):
    """物理数据接入模型的调用约定；字段语义由组件验证，数值类型保持不透明。"""

    def training_parameters(self, config: dict) -> dict:
        """从声明提取完整构造参数，框架不解释专属域布局。"""
        ...

    def prepare_sample(
        self,
        sample: dict,
        config: dict,
        normalization: Any,
        *,
        evaluation: bool = False,
        epoch: int = 0,
    ) -> dict:
        """将具名物理样本转成输入、目标和带身份的计算批次。"""
        ...

    def loss(self, model: Any, batch: dict, config: dict) -> dict:
        """返回可微 loss 与所声明归约所需累计量。"""
        ...

    def predict_sample(
        self, model: Any, sample: dict, config: dict, normalization: Any, *, preparation_id: str
    ) -> dict:
        """完整原点顺序的具名物理预测；不返回抽样训练点冒充全场。"""
        ...
