"""可复制的推理扩展：逐实体误差，不访问框架运行状态。"""

import torch


def absolute_error(prediction: torch.Tensor, truth: torch.Tensor) -> torch.Tensor:
    """同单位物理场的逐实体绝对误差，向量返回误差模长。"""
    if prediction.shape != truth.shape:
        raise ValueError("预测和真值的实体与分量必须一致")
    difference = prediction - truth
    return torch.linalg.vector_norm(difference, dim=-1, keepdim=True)
