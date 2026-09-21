"""通用多步状态 rollout。"""

from __future__ import annotations

from collections.abc import Callable

import torch


def rollout(
    initial_state: torch.Tensor,
    steps: int,
    advance: Callable[[torch.Tensor, int], torch.Tensor],
    *,
    preserve: torch.Tensor | None = None,
) -> torch.Tensor:
    """按 ``advance`` 推进状态并返回包含初始状态的时间序列。

    ``preserve`` 为布尔节点 mask 时，每一步保留这些节点的原状态；边界值由调用方
    在 ``advance`` 中提供，能力本身不解释物理边界名称。
    """
    if steps < 0:
        raise ValueError("steps 不能为负")
    if preserve is not None and preserve.shape != initial_state.shape[:-1]:
        raise ValueError("preserve 必须匹配状态的非分量轴")
    states = [initial_state]
    current = initial_state
    for index in range(steps):
        next_state = advance(current, index)
        if next_state.shape != initial_state.shape:
            raise ValueError("rollout 每一步必须保持状态形状")
        if not torch.isfinite(next_state).all():
            raise ValueError("rollout 产生非有限状态")
        if preserve is not None:
            next_state = torch.where(preserve.unsqueeze(-1), initial_state, next_state)
        states.append(next_state)
        current = next_state
    return torch.stack(states, dim=0)
