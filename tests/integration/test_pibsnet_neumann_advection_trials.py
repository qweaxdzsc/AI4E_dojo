"""独立六组协议的数学含义、更新范围及来源门禁。"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

TOOL = Path(__file__).parents[2] / "tools/verification/pibsnet/neumann_advection_trials.py"
spec = importlib.util.spec_from_file_location("trial_tool", TOOL)
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


def test_physical_basis_derivatives():
    ns = {"np": np}
    exec(trial.PHYSICAL, ns)  # noqa: S102 - 执行本测试工具中固定的数学定义
    x, knots, b = ns["BsKnots"](40, 5, 128)
    d1, d2 = ns["BsKnots_derivatives"](40, 5, 128, knots, x)
    greville = np.array([knots[i + 1 : i + 6].mean() for i in range(40)]) / 35
    np.testing.assert_allclose(b @ greville, x / 35, atol=1e-14)
    np.testing.assert_allclose(d1 @ greville * 35, 1, atol=1e-12)
    np.testing.assert_allclose(d2 @ greville * 35**2, 0, atol=1e-10)
    assert np.count_nonzero(d1[-1]) == 2


def test_update_matrix_and_source_identity():
    assert len(trial.VARIANTS) == 6
    assert trial.VARIANTS["neumann_physical_instance"][3:] == (5000, 250000)
    assert trial.VARIANTS["neumann_source_epoch"][3:] == (5000, 5000)
    assert trial.amend("untouched", "advection", "cell-10", "advection_source") == "untouched"
    with pytest.raises(ValueError):
        trial.replace_once("x x", "x", "y")
    with pytest.raises(ValueError):
        trial.amend("x", "advection", "cell-10", "neumann_source_epoch")


def test_neumann_instance_patch():
    source = (
        "        for sample in train_data:\n"
        "            total_L = total_L + L\n"
        "        total_L.backward()\n        optimizer.step()"
    )
    result = trial.amend(source, "neumann_diffusion", "script", "neumann_source_instance")
    assert "            optimizer.zero_grad()" in result
    assert "            L.backward()\n            optimizer.step()" in result
    assert "total_L = total_L + L.detach()" in result
    assert "total_L.backward()" not in result


def test_report_rejects_incomplete_budget(tmp_path, monkeypatch):
    import json
    import sys

    monkeypatch.syspath_prepend(str(TOOL.parent))
    import neumann_advection_report as report

    (tmp_path / "protocol.json").write_text(json.dumps({"baseline": str(tmp_path)}))
    case = tmp_path / "neumann_source_epoch/neumann_diffusion"
    case.mkdir(parents=True)
    (case / "status.json").write_text(json.dumps({"status": "running"}))
    (case / "result.json").write_text(json.dumps({"epochs_completed": 1, "updates": 1}))
    with pytest.raises(ValueError, match="预算未完成"):
        report.verify(tmp_path)
    assert not (tmp_path / "reports/verified_evidence.json").exists()
    assert "neumann_advection_report" in sys.modules


def test_physical_second_derivative_against_finite_difference():
    from scipy.interpolate import BSpline

    ns = {"np": np}
    exec(trial.PHYSICAL, ns)  # noqa: S102 - 固定数学定义
    _, knots, _ = ns["BsKnots"](40, 5, 128)
    points = np.array([0.33, 2.37, 10.41, 30.22, 34.76])
    first, second = ns["BsKnots_derivatives"](40, 5, len(points), knots, points)
    weights = np.sin(np.arange(40))
    field = BSpline(knots, weights, 5)
    h = 1e-4
    np.testing.assert_allclose(
        first @ weights, (field(points + h) - field(points - h)) / (2 * h), atol=1e-7
    )
    np.testing.assert_allclose(
        second @ weights,
        (field(points + h) - 2 * field(points) + field(points - h)) / h**2,
        atol=5e-7,
    )
