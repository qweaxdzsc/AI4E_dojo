"""推理时参数适配，独立于普通无参数更新的采样。"""

import torch

from ai4e_contrib.ability.constraint.safediffcon.objective import safety
from ai4e_contrib.ability.transform.safediffcon.preparation import physical

from .control import sample


def adaptation_loss(
    model: torch.nn.Module,
    states: torch.Tensor,
    targets: torch.Tensor,
    *,
    case: str,
    q: float,
    weight: float,
    guide,
) -> torch.Tensor:
    """保留原末步反传和案例损失；Burgers 平方铰链，Tokamak 线性铰链。"""
    predicted = sample(
        model, states, targets, case=case, q=q, weight=weight, adapt=True, guide=guide
    )
    s = safety(physical(predicted, case=case), case=case)
    violation = s + q - 0.8**2 if case == "burgers" else 4.98 - s + q
    penalty = torch.maximum(violation, torch.zeros_like(s))
    return penalty.square().mean() if case == "burgers" else penalty.mean()
