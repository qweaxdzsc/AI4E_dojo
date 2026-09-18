"""Transolver 组件出口和参考案例默认值；不持有工作流循环。"""

from .inference import SurfaceInference
from .model import SOURCE, construct, describe, predict

__all__ = ["SOURCE", "SurfaceInference", "construct", "describe", "predict", "resolve"]


from ai4e_contrib.application.aero_cfd.transolver3 import resolve

from .preparation import loss, predict_sample, prepare_sample

__all__ += ["loss", "predict_sample", "prepare_sample", "training_parameters"]


def training_parameters(config):
    """返回模型完整构造参数，不要求调用方解释布局。"""
    return dict(config["model"]["parameters"])


# 当前参考优化和点场损失的真实限制，供平台按能力呈现。
TRAINING_CONSTRAINTS = {
    "batch_size": {"allowed": [1], "readOnly": True},
    "num_workers": {"allowed": [0], "readOnly": True},
    "accumulate": {"allowed": [1], "readOnly": True},
    "precision": {"allowed": ["fp32"], "readOnly": True},
    "evaluation_split": {"allowed": ["validation"], "readOnly": True},
    "scheduler_unit": {"allowed": ["epoch"], "readOnly": True},
    "optimizer": {"allowed": ["adamw"], "readOnly": True},
}
PLATFORM_LOSSES = {
    "configurable": False,
    "fixed": "mse",
    "reason": "参考点场等权标准化逐元素均方误差",
}
PLATFORM_SAMPLING = {
    "configurable": True,
    "constraints": {
        "stride": {
            "allowed": [4],
            "readOnly": True,
            "reason": "参考训练抽稀步长为 4",
        }
    },
}

# 仅描述推理执行能力；不会改变模型或训练契约。
INFERENCE_CAPABILITIES = {"query_chunk_size": True, "physical_fields": True}
