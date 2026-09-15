"""选定梯形原函数逐层对照；验收算法交接，不以最终误差接近代替。"""

import ast
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from ai4e_contrib.ability.model.pibsnet import component, trapezoid
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import (
    make_sample,
    parameter_streams,
    solve,
)
from ai4e_core.abilities.training.optimization import update
from tests.integration.test_pibsnet_training import configuration, configuration_for, run_stages

SOURCE = Path(__file__).resolve().parents[3] / "PI-BSNet/src/diffusion_trapezoid.ipynb"


def reference():
    notebook = json.loads(SOURCE.read_text())
    source = "".join(notebook["cells"][2]["source"])
    source = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith(("!", "%"))
    )
    names = {
        "BsFun",
        "build_bspline_basis",
        "build_bspline_derivatives",
        "BSplineNet_a",
        "compute_loss_pde_data_icbc",
    }
    nodes = [
        n
        for n in ast.parse(source).body
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
    ]
    assert len(nodes) == len(names)
    namespace = {"np": np, "torch": torch, "nn": nn}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)  # noqa: S102 - 锁定参考数值定义
    return namespace


def test_original_basis_forward_gradients_adam_and_axis_layout():
    torch.set_num_threads(1)
    ref = reference()
    cfg = configuration.defaults("diffusion_trapezoid")
    cfg["model"].update(control_points=[7, 5, 6], degree=3, hidden_dim=8)
    sample = make_sample(
        np.random.RandomState(42), {"nx": 9, "ny": 7, "nt": 201}, index=0, split="train"
    )
    sample.update(id="train-00000", case="diffusion_trapezoid")
    prepared = component.prepare(sample, cfg)
    matrices = []
    for count, cp in zip([201, 9, 7], [7, 6, 5], strict=True):
        b, knots, coords = ref["build_bspline_basis"](cp, 3, count)
        d, dd = ref["build_bspline_derivatives"](cp, 3, count, knots, coords)
        matrices.append((b, d, dd))
    for actual, expected in zip(
        prepared["grid_bases"], [matrices[0], matrices[2], matrices[1]], strict=True
    ):
        for p, q in zip(actual, expected, strict=True):
            torch.testing.assert_close(p, q, rtol=0, atol=0)
    torch.manual_seed(42)
    original = ref["BSplineNet_a"](7, 6, 5, hidden_dim=8)
    torch.manual_seed(42)
    actual = component.build(cfg)
    for p, q in zip(original.parameters(), actual.parameters(), strict=True):
        torch.testing.assert_close(p, q, rtol=0, atol=0)
    a = torch.tensor([[sample["parameters"]["a"]]], dtype=torch.float32)
    bt, bx, by = matrices
    expected = ref["compute_loss_pde_data_icbc"](
        original,
        a,
        sample["u"].float(),
        bt[0],
        bx[0],
        by[0],
        bt[1],
        bx[2],
        by[2],
        lambda_data=1,
        lambda_phys=0.001,
    )
    result = component.step(actual, prepared, cfg)
    torch.testing.assert_close(
        component.predictions(actual, prepared, cfg)["u"], expected[3][0], rtol=0, atol=0
    )
    torch.testing.assert_close(result["loss"], expected[0], rtol=0, atol=0)
    torch.testing.assert_close(
        trapezoid.constrained_coefficients(actual, a), expected[4], rtol=0, atol=0
    )
    expected[0].backward()
    result["loss"].backward()
    for p, q in zip(original.parameters(), actual.parameters(), strict=True):
        torch.testing.assert_close(p.grad, q.grad, rtol=0, atol=0)
    op = torch.optim.Adam(original.parameters(), lr=0.001)
    oa = torch.optim.Adam(actual.parameters(), lr=0.001)
    op.step()
    update(actual, oa, lambda m, b: component.step(m, b, cfg), prepared, clip=None)
    for p, q in zip(original.parameters(), actual.parameters(), strict=True):
        torch.testing.assert_close(p, q, rtol=0, atol=0)
    for sp, sq in zip(op.state.values(), oa.state.values(), strict=True):
        for key in sp:
            torch.testing.assert_close(sp[key], sq[key], rtol=0, atol=0)


def test_dataset_scalar_numpy1_arithmetic_and_rng():
    xi, eta, t, actual = solve(nx=7, ny=5, nt=101, a=0.7)
    expected = np.ones_like(actual)
    expected[0, 1:-1, 1:-1] = 0
    for k in range(1, len(t)):
        old = expected[k - 1]
        for j in range(1, len(eta) - 1):
            dx = (2 - eta[j]) / (len(xi) - 1)
            for i in range(1, len(xi) - 1):
                xx = (float(old[j, i + 1]) - 2 * float(old[j, i]) + float(old[j, i - 1])) / (dx**2)
                yy = (float(old[j + 1, i]) - 2 * float(old[j, i]) + float(old[j - 1, i])) / (
                    (1 / (len(eta) - 1)) ** 2
                )
                expected[k, j, i] = float(old[j, i]) + 0.01 * (0.5 * (xx + 0.7 * yy))
    np.testing.assert_array_equal(actual, expected)
    streams = parameter_streams({"seed": 42})
    _, rng = next(streams)
    train = rng.uniform(0, 1.5, 10)
    _, rng = next(streams)
    test = rng.uniform(0, 1.5, 10)
    all_values = np.random.RandomState(42).uniform(0, 1.5, 21)
    np.testing.assert_array_equal(train, all_values[:10])
    np.testing.assert_array_equal(test, all_values[11:])
    with pytest.raises(ValueError, match="稳定"):
        solve(nx=21, ny=21, nt=5, a=1)


def test_reject_old_data_and_unsupported_conditions():
    cfg = configuration.defaults("diffusion_trapezoid")
    with pytest.raises(ValueError, match="数据协议"):
        component.prepare({}, cfg)
    cfg["model"]["boundary_conditions"]["left"]["u"]["value"] = 0
    with pytest.raises(ValueError, match="初始系数"):
        component.build(cfg)


def test_restore_and_independent_post(tmp_path):
    from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import generate

    generate({"output": str(tmp_path / "data"), "train": 2, "test": 1, "nx": 7, "ny": 5, "nt": 101})
    cfg = configuration_for("diffusion_trapezoid", tmp_path)
    cfg["train"]["max_epochs"] = 1
    assert run_stages(cfg, ["trainprep", "train"]) == 0
    checkpoint = next((tmp_path / "runs").glob("*/checkpoints/last.pt"))
    resumed = deepcopy(cfg)
    resumed["train"].update(max_epochs=2, resume=str(checkpoint))
    resumed["run_root"] = str(tmp_path / "resumed")
    assert run_stages(resumed, ["train"]) == 0
    resumed_checkpoint = next((tmp_path / "resumed").glob("*/checkpoints/last.pt"))
    cfg["train"]["max_epochs"] = 2
    cfg["run_root"] = str(tmp_path / "continuous")
    assert run_stages(cfg, ["train"]) == 0
    continuous = next((tmp_path / "continuous").glob("*/checkpoints/last.pt"))
    a, b = [torch.load(p, weights_only=False) for p in (resumed_checkpoint, continuous)]
    assert a["updates"] == b["updates"] == 4
    for key in a["model"]:
        torch.testing.assert_close(a["model"][key], b["model"][key], rtol=0, atol=0)
    cfg["post"]["checkpoint"] = str(resumed_checkpoint)
    assert run_stages(cfg, ["post"]) == 0
    report = json.loads((tmp_path / "predictions/predictions.json").read_text())
    result = torch.load(tmp_path / "predictions/test-00000.pt", weights_only=False)
    d = (result["prediction"] - result["target"]).double().flatten(1)
    r = result["target"].double().flatten(1)
    assert report["mean_time_relative_l2"] == pytest.approx(
        float((d.norm(dim=1) / (r.norm(dim=1) + 1e-12)).mean())
    )
