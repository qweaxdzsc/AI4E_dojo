"""用户脚本直接调用方程：不创建 Field/Equation 对象，不包装 PyTorch。"""

import torch

from ai4e_contrib.ability.constraint.equations import burgers, navier_stokes_2d


def burgers_loss(values, mu=1.0, nu=0.01):
    """values 是用户或模型计算的物理场/导数字典。"""
    residual = burgers(
        u=values["u"],
        u_t=values["u_t"],
        u_x=values["u_x"],
        u_xx=values["u_xx"],
        convection_coefficient=mu,
        viscosity=nu,
    )
    return residual.square().mean()


def ns_losses(values, density=1.0, viscosity=0.01):
    """NS 用户自行组合连续性和动量损失；函数不求导或补充边界条件。"""
    residuals = navier_stokes_2d(**values, density=density, kinematic_viscosity=viscosity)
    return {name: residual.square().mean() for name, residual in residuals.items()}


def custom_step(model, prepared):
    """最小用户训练步接口示例：普通函数返回 loss 和 losses 即可。"""
    parameter = next(model.parameters())
    sample = prepared["sample"]
    inputs = torch.tensor(
        [[sample["parameters"][n] for n in model.parameter_names]],
        device=parameter.device,
        dtype=parameter.dtype,
    )
    loss = model(inputs).square().mean()
    return {"loss": loss, "losses": {"custom_coefficient_penalty": loss}}
