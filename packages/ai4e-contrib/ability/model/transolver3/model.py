"""Transolver 公开适配：具名输入输出，不向框架泄露列表式调用。"""

import torch

from .network import Model

SOURCE = "Transolver-3/Transolver_chunk_opt_matrix_mul"


def construct(**parameters):
    """按原参数顺序实例化模型，不额外消耗随机数。"""
    parameters = dict(parameters)
    checkpointing = parameters.pop("gradient_checkpointing", True)
    if parameters.get("space_dim", 0) < 1 or parameters.get("out_dim", 0) < 1:
        raise ValueError("输入和输出维度必须为正")
    if parameters.get("fun_dim", 0) != 0:
        raise ValueError("具名点场入口将全部特征拼入 space_dim，fun_dim 必须为零")
    model = Model(**parameters)
    model.dojo_parameters = parameters
    model.dojo_checkpointing = bool(checkpointing)
    return model


def describe(model):
    """返回稳定结构声明，不包含权重或运行时缓存。"""
    return {
        "source": SOURCE,
        "version": 1,
        "parameters": model.dojo_parameters,
        "inputs": ["features"],
        "outputs": ["fields"],
    }


def predict(model, inputs):
    """前向保持参考算子；仅训练时启用激活检查点。"""
    features = inputs["features"]
    width = model.dojo_parameters["space_dim"]
    if not isinstance(features, torch.Tensor) or features.ndim != 3 or features.shape[-1] != width:
        raise ValueError(f"features 必须为 [批次, 点, {width}] 张量")
    if not torch.isfinite(features).all():
        raise ValueError("模型输入含非有限值")
    return {
        "fields": model([features], use_checkpoint=model.training and model.dojo_checkpointing)[0]
    }


construct.describe = describe
