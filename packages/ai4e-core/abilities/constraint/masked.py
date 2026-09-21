"""带显式布尔 mask 的监督比较。"""

from __future__ import annotations

import torch


def masked_mse(
    prediction: torch.Tensor,
    target: torch.Tensor,
    mask: torch.Tensor,
    *,
    feature_reduction: str = "mean",
) -> torch.Tensor:
    """仅在 mask 为真的元素上计算平方误差，空 mask 明确失败。

    ``feature_reduction`` 控制最后一维先求均值还是求和；其余被 mask 选中的
    实体始终等权平均。
    """
    if prediction.shape != target.shape:
        raise ValueError("预测和目标形状必须一致")
    if mask.shape != prediction.shape and mask.shape != prediction.shape[:-1]:
        raise ValueError("mask 必须匹配完整张量或节点轴")
    if feature_reduction not in {"mean", "sum"}:
        raise ValueError("feature_reduction 必须是 mean 或 sum")
    selected = (prediction - target).square()
    mask = mask.to(dtype=torch.bool, device=prediction.device)
    if mask.ndim == prediction.ndim - 1:
        if not bool(mask.any()):
            raise ValueError("mask 不能为空")
        per_entity = selected.sum(dim=-1) if feature_reduction == "sum" else selected.mean(dim=-1)
        return per_entity.masked_select(mask).mean()
    count = mask.sum()
    if int(count) == 0:
        raise ValueError("mask 不能为空")
    return selected.masked_select(mask).mean()
