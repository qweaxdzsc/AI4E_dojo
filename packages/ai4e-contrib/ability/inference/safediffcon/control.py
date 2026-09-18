"""扩散控制采样、原安全梯度及输入条件绑定。"""

import torch

from ai4e_contrib.ability.constraint.safediffcon.objective import cost
from ai4e_contrib.ability.transform.safediffcon.preparation import physical


def guidance(x: torch.Tensor, target, *, case: str, q: float, weight: float) -> torch.Tensor:
    """输入梯度用于安全引导；不直接更新网络参数。"""
    with torch.enable_grad():
        x = x.detach().requires_grad_()
        value = cost(physical(x, case=case), target, case=case, q=q, weight=weight).sum()
        return torch.autograd.grad(value, x)[0]


def sample(
    model, state, target, *, case, q=0.0, weight=1.0, calibration=False, adapt=False, guide=guidance
):
    """区别普通采样、固定控制校准与最后一步可反传采样。"""
    conditions = (
        {"u_init": state[:, 0, 0, :], "u_final": state[:, 0, 10, :]}
        if case == "burgers"
        else {"u_init": state[:, :3, 0], "u_final": state[:, [0, 2], :122]}
    )
    controls = state[:, 1] if case == "burgers" else state[:, 3:]
    return model.sample(
        batch_size=len(state),
        clip_denoised=True,
        device=state.device,
        guidance_u0=not calibration,
        w_groundtruth=controls if calibration else None,
        nablaJ=None if calibration else lambda x: guide(x, target, case=case, q=q, weight=weight),
        J_scheduler=None if calibration else lambda t: 1.0,
        w_scheduler=None if calibration else lambda t: 1.0,
        enable_grad=adapt,
        **conditions,
    )
