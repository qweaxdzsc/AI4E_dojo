"""普通 PyTorch 方程：解析残差、形状门禁及参数梯度。"""

import pytest
import torch

from ai4e_contrib.ability.constraint.equations import (
    advection,
    burgers,
    convection_diffusion,
    diffusion,
    navier_stokes_2d,
)


def test_burgers_manufactured_gradient():
    x = torch.linspace(0.1, 1, 7, dtype=torch.float64)
    nu = torch.tensor(0.1, dtype=x.dtype, requires_grad=True)
    residual = burgers(
        u=x * x,
        u_t=x,
        u_x=2 * x,
        u_xx=torch.full_like(x, 2),
        convection_coefficient=2.0,
        viscosity=nu,
    )
    torch.testing.assert_close(residual, x + 4 * x**3 - 2 * nu)
    residual.sum().backward()
    assert nu.grad == -14


def test_heat_and_advection_exact():
    x = torch.linspace(0, 1, 21, dtype=torch.float64)
    value = torch.cos(torch.pi * x) * torch.exp(torch.tensor(-0.2 * torch.pi**2, dtype=x.dtype))
    torch.testing.assert_close(
        diffusion(u_t=-0.2 * torch.pi**2 * value, u_xx=-(torch.pi**2) * value, diffusivity=0.2),
        torch.zeros_like(x),
    )
    torch.testing.assert_close(advection(u_t=-2 * x, u_x=x, velocity=2), torch.zeros_like(x))
    torch.testing.assert_close(
        convection_diffusion(u_t=x, u_x=x, u_xx=4 * x, velocity=1, diffusivity=0.5),
        torch.zeros_like(x),
    )


def test_navier_stokes_taylor_green():
    x = torch.linspace(0.1, 1, 11, dtype=torch.float64)
    y, nu, rho, t = x * 0.7, 0.03, 2.0, 0.2
    e = torch.exp(torch.tensor(-2 * nu * t, dtype=x.dtype))
    u, v = -torch.cos(x) * torch.sin(y) * e, torch.sin(x) * torch.cos(y) * e
    residuals = navier_stokes_2d(
        u=u,
        v=v,
        u_t=-2 * nu * u,
        v_t=-2 * nu * v,
        u_x=torch.sin(x) * torch.sin(y) * e,
        u_y=-torch.cos(x) * torch.cos(y) * e,
        v_x=torch.cos(x) * torch.cos(y) * e,
        v_y=-torch.sin(x) * torch.sin(y) * e,
        p_x=rho / 2 * torch.sin(2 * x) * e**2,
        p_y=rho / 2 * torch.sin(2 * y) * e**2,
        u_xx=-u,
        u_yy=-u,
        v_xx=-v,
        v_yy=-v,
        density=rho,
        kinematic_viscosity=nu,
    )
    for value in residuals.values():
        torch.testing.assert_close(value, torch.zeros_like(value), atol=1e-14, rtol=0)


@pytest.mark.parametrize("coefficient", [torch.ones(3, 1), float("nan"), -1.0])
def test_coefficient_gate(coefficient):
    with pytest.raises(ValueError):
        diffusion(u_t=torch.ones(3), u_xx=torch.ones(3), diffusivity=coefficient)


def test_no_field_broadcast():
    with pytest.raises(ValueError):
        diffusion(u_t=torch.ones(3, 1), u_xx=torch.ones(3), diffusivity=1)
