"""原版加权分数次序统计量；不替换成另一种加权分位数算法。"""

import math

import torch

from ai4e_contrib.ability.inference.safediffcon.control import sample
from ai4e_contrib.ability.transform.safediffcon.preparation import physical

from .objective import cost, safety


def calibrate(
    model,
    states,
    targets,
    *,
    case,
    q,
    weight,
    alpha,
    batch_size=16,
    previous_q=None,
    previous_weight=None,
):
    """固定校准样本逐批采样；分数归一化跨整个校准集。"""
    if not 0 < alpha < 1 or len(states) == 0:
        raise ValueError("校准集与置信度非法")
    scores = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(states), batch_size):
            state, target = states[start : start + batch_size], targets[start : start + batch_size]
            predicted = sample(model, state, target, case=case, calibration=True)
            scores.append(
                (
                    safety(physical(predicted, case=case), case=case, calibration=True)
                    - safety(physical(state, case=case), case=case, calibration=True)
                ).abs()
            )
        weights = torch.exp(
            -cost(physical(states, case=case), targets, case=case, q=q, weight=weight)
        )
        if previous_q is not None:
            weights *= torch.exp(
                -cost(
                    physical(states, case=case),
                    targets,
                    case=case,
                    q=previous_q,
                    weight=previous_weight,
                )
            )
        weights = (
            torch.ones_like(weights)
            if weights.sum() == 0
            else len(weights) * weights / weights.sum()
        )
        values = weights * torch.cat(scores)
        rank = min(math.ceil(alpha * (len(values) + 1)), len(values)) - 1
        result = values.sort().values[rank]
        if not torch.isfinite(result):
            raise FloatingPointError("校准分位数非有限")
        return float(result)
