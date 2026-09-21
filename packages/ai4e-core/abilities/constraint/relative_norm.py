"""逐样本相对范数；显式保留样本轴和零真值行为。"""

import torch


def relative_norm(prediction, target, *, p=2, reduction="mean"):
    """计算各样本展平后的误差范数/目标范数，零分母明确失败。"""
    if prediction.shape != target.shape or prediction.ndim < 2:
        raise ValueError("预测/目标须为相同的 [B,...]")
    denominator = torch.linalg.vector_norm(target.flatten(1), ord=p, dim=1)
    if torch.any(denominator == 0):
        raise ValueError("零目标的相对范数未定义")
    result = torch.linalg.vector_norm((prediction - target).flatten(1), ord=p, dim=1) / denominator
    if reduction == "none":
        return result
    if reduction == "mean":
        return result.mean()
    if reduction == "sum":
        return result.sum()
    raise ValueError("未知归约")


def supervised_objective(model, item, *, input_names, decode, target_name, loss):
    """具名监督连接；损失、解码和目标身份均由局部调用方明确选择。"""
    raw = model(**{name: item[name] for name in input_names})
    return loss(decode(raw, item), item[target_name])
