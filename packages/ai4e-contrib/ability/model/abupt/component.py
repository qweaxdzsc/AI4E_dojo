"""AB-UPT 组件公开出口；保留原构造器身份与数值行为。"""

from ai4e_contrib.application.aero_cfd.abupt import apply_resolved as resolve

from .batch import collate
from .inference import InferenceContext
from .model import SOURCE, construct, describe, predict
from .sampling import prepare_inputs

__all__ = [
    "SOURCE",
    "InferenceContext",
    "collate",
    "construct",
    "describe",
    "predict",
    "prepare_inputs",
    "resolve",
]


from .preparation import loss, predict_sample, prepare_sample

__all__ += ["loss", "predict_sample", "prepare_sample", "training_parameters"]


def training_parameters(config):
    """返回模型完整构造参数，不要求调用方解释布局。"""
    return {**config["model"]["parameters"], "data_specs": config["model"]["data_specs"]}


# 公开页面消费同一监督方法集合，不另造算法选项。
from ai4e_core.abilities.constraint.compare import METHODS

PLATFORM_LOSSES = {"configurable": True, "allowed": sorted(METHODS)}
PLATFORM_SAMPLING = {"configurable": True}

# 仅描述推理执行能力；不会改变模型或训练契约。
INFERENCE_CAPABILITIES = {"query_chunk_size": True, "physical_fields": True}
