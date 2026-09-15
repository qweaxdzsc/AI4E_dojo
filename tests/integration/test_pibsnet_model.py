"""独立多项式复原证明样条导数与梯形完整坐标变换正确。"""

import numpy as np
import torch
from scipy.interpolate import BSpline

from ai4e_contrib.ability.model.pibsnet import PIBSNet, basis
from ai4e_core.abilities.transform.trapezoid import physical_derivatives


def test_physical_spline_polynomial_and_endpoints():
    x = torch.linspace(-2, 5, 61, dtype=torch.float64)
    b, d, dd = basis(x, bounds=(-2, 5), control_points=9, degree=3)
    knots = np.r_[np.repeat(-2.0, 3), np.linspace(-2, 5, 7), np.repeat(5.0, 3)]
    greville = np.array([knots[i + 1 : i + 4].mean() for i in range(9)])
    c = np.linalg.solve(BSpline(knots, np.eye(9), 3)(greville), greville**2)
    coeff = torch.from_numpy(c)
    torch.testing.assert_close(b @ coeff, x * x)
    torch.testing.assert_close(d @ coeff, 2 * x)
    torch.testing.assert_close(dd @ coeff, torch.full_like(x, 2))


def test_trapezoid_manufactured_physical_quadratic():
    xi = torch.linspace(0.1, 0.9, 9, dtype=torch.float64)
    eta = xi * 0.7
    width = 2 - eta
    physical_x = -1 + 0.5 * eta + xi * width
    # u = X² + 3Y²。
    values = physical_derivatives(
        xi=xi,
        eta=eta,
        u_xi=2 * physical_x * width,
        u_eta=2 * physical_x * (0.5 - xi) + 6 * eta,
        u_xixi=2 * width**2,
        u_xieta=2 * width * (0.5 - xi) - 2 * physical_x,
        u_etaeta=2 * (0.5 - xi) ** 2 + 6,
    )
    torch.testing.assert_close(values["u_x"], 2 * physical_x)
    torch.testing.assert_close(values["u_y"], 6 * eta)
    torch.testing.assert_close(values["u_xx"], torch.full_like(xi, 2))
    torch.testing.assert_close(values["u_yy"], torch.full_like(xi, 6))


def test_hard_boundary_and_parameter_gradient():
    model = PIBSNet(["nu"], [5, 6], hidden_dim=8, hard_boundaries={"right": 1})
    coefficients = model(torch.tensor([[0.2], [0.3]]))
    assert torch.all(coefficients[:, :, -1] == 1)
    coefficients.sum().backward()
    assert model.net[0].weight.grad is not None
