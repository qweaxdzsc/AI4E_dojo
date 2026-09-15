"""原文献正式参数下，与独立 SciPy 基矩阵和原生 PyTorch 目标逐项核验。"""

import numpy as np
import torch
from scipy.interpolate import BSpline

from ai4e_contrib.ability.model.pibsnet import component as model_component
from ai4e_contrib.application.datasets.parametric import component
from tests.integration.test_pibsnet_training import configuration


def test_reference_defaults_do_not_add_condition_penalties():
    """非 Neumann 参考目标只有 PDE 与数据，不额外引入初值或周期权重。"""
    for case in configuration.CASES:
        cfg = configuration.defaults(case)
        constraints = cfg["model"]["constraints"]
        assert constraints["periodic_boundary_conditions"]["weight"] == 0
        assert constraints["initial_conditions"]["weight"] == (
            2 if case == "neumann_diffusion" else 0
        )
        assert cfg["model"]["sampling"]["interior"] == {"method": "all", "include_boundary": True}


def test_neumann_formal_native_physical_loss_and_gradients():
    cfg = configuration.defaults("neumann_diffusion")
    sample = component("neumann_diffusion").make_sample(
        np.random.default_rng(42), {"nx": 128, "nt": 128}, index=0, split="train"
    )
    sample.update(id="train-0", case="neumann_diffusion")
    torch.manual_seed(42)
    from ai4e_contrib.ability.model.pibsnet.model import PIBSNet, evaluate_fields
    from ai4e_contrib.ability.model.pibsnet.spline import prepare_grid
    from ai4e_core.abilities.sampling.physical import grid_points

    model = PIBSNet(["nu"], [40, 40], hidden_dim=128).double()
    # 通用物理样条能力仍接受标准物理导数；不再作为原Neumann默认目标。
    basis = prepare_grid(sample, cfg["model"])
    v = evaluate_fields(model, sample, basis, points=grid_points(sample), grid=True)
    losses = {
        "pde": (v["u_t"] - sample["parameters"]["nu"] * v["u_xx"]).square().mean(),
        "data": (v["u"] - sample["u"]).square().mean(),
        "initial": (v["u"][0] - torch.cos(torch.pi * sample["axes"]["x"].double())).square().mean(),
        "boundary/left": v["u_x"][:, 0].square().mean(),
        "boundary/right": v["u_x"][:, -1].square().mean(),
    }
    actual = {
        "losses": losses,
        "loss": losses["pde"]
        + 5 * losses["data"]
        + 2 * losses["initial"]
        + 2 * (losses["boundary/left"] + losses["boundary/right"]),
    }
    nu = sample["parameters"]["nu"]
    coefficients = model(torch.tensor([[nu]], dtype=torch.float64))[0]
    knots = np.r_[np.zeros(5), np.linspace(0, 1, 36), np.ones(5)]
    spline = BSpline(knots, np.eye(40), 5)
    b, d1, d2 = [
        torch.from_numpy(spline(sample["axes"]["x"].double().numpy(), nu=order))
        for order in range(3)
    ]
    field = b @ coefficients @ b.T
    dt = d1 @ coefficients @ b.T
    dx = b @ coefficients @ d1.T
    dxx = b @ coefficients @ d2.T
    expected = {
        "pde": (dt - nu * dxx).square().mean(),
        "data": (field - sample["u"]).square().mean(),
        "initial": (field[0] - torch.cos(torch.pi * sample["axes"]["x"].double())).square().mean(),
        "boundary/left": dx[:, 0].square().mean(),
        "boundary/right": dx[:, -1].square().mean(),
    }
    reference = (
        expected["pde"]
        + 5 * expected["data"]
        + 2 * expected["initial"]
        + 2 * (expected["boundary/left"] + expected["boundary/right"])
    )
    for name, value in expected.items():
        torch.testing.assert_close(actual["losses"][name], value, rtol=2e-12, atol=1e-10)
    torch.testing.assert_close(actual["loss"], reference, rtol=2e-12, atol=1e-10)
    a = torch.autograd.grad(actual["loss"], model.parameters())
    b = torch.autograd.grad(reference, model.parameters())
    for grad, expected_grad in zip(a, b, strict=True):
        torch.testing.assert_close(grad, expected_grad, rtol=1e-9, atol=1e-7)


def test_trapezoid_paper_equation_84_is_explicit_approximation():
    points = torch.tensor([[0.2, 0.3, 0.4], [0.5, 0.6, 0.7]], dtype=torch.float64)
    values = {
        "u_t": torch.ones(2),
        "u_xixi": torch.full((2,), 4.0),
        "u_etaeta": torch.full((2,), 6.0),
    }
    actual = model_component.equation("diffusion_trapezoid", values, {"a": 0.8}, points=points)
    expected = 1 - 0.5 * (4 / (2 - points[:, 1].float()).square() + 0.8 * 6)
    torch.testing.assert_close(actual, expected)
