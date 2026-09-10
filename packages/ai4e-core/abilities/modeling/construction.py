"""模型构造与重建信息，参数语义由模型组件定义。"""

from copy import deepcopy

from ai4e_spec.components.model import ModelFactory


def construct(factory: ModelFactory, parameters: dict):
    """调用注入构造器，保留与调用者独立的生效参数。"""
    configured = deepcopy(parameters)
    return factory(**configured), configured
