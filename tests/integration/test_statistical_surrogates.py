"""统计代理固定人工矩阵反例；本文件不执行参数优化、真实数据拟合或建树。"""

import importlib

import numpy as np
import pytest

from ai4e_core.abilities.modeling.models.kriging import Kriging
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition, SquaredExponential
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
from ai4e_core.abilities.training.boosting import fit_boosting
from ai4e_core.abilities.training.kriging import (
    condition_kriging,
    fit_kriging,
    solve_kriging_condition,
)
from tools.verification.operator_surrogates.reference_statistical import SOURCES, kriging_reference


def test_nontraining_covariance_independent_formula():
    x = np.array([[0.0, 1.0], [2.0, -1.0], [0.4, 0.1]])
    z = np.array([[0.3, 0.2], [1.0, 3.0]])
    kernel = SquaredExponential([0.4, 2.0], 1.7)
    expected = np.array(
        [
            [
                1.7
                * np.exp(
                    -0.5
                    * sum(
                        ((a - b) / s) ** 2 for a, b, s in zip(row, other, [0.4, 2.0], strict=True)
                    )
                )
                for other in z
            ]
            for row in x
        ]
    )
    np.testing.assert_allclose(kernel(x, z), expected, rtol=1e-14)
    np.testing.assert_array_equal(np.diag(kernel(x, x)), kernel.diagonal(x))
    np.testing.assert_array_equal(
        SquaredExponential.from_state(kernel.get_state())(x, z), kernel(x, z)
    )


@pytest.mark.parametrize(
    "scale,variance", [(0, 1), (-1, 1), ([1, np.nan], 1), (True, 1), (1, 0), (1, -1)]
)
def test_nontraining_bad_covariance(scale, variance):
    with pytest.raises(ValueError):
        SquaredExponential(scale, variance)


@pytest.mark.parametrize("degree", [0, 1])
def test_nontraining_gls_matches_independent_augmented_system(degree):
    x = np.array([[-1.0, -0.7], [-0.5, 0.8], [-0.2, -0.2], [0.2, 0.5], [0.6, -0.8], [1.0, 0.1]])
    y = 2 + x[:, 0] - 0.3 * x[:, 1] + 0.2 * np.sin(3 * x[:, 0])
    q = np.array([[-1.2, 0.8], [0.1, 0.2], [1.1, -0.4]])
    model, report = condition_kriging(
        x,
        y,
        trend=PolynomialBasis(2, degree),
        kernel_config={"length_scale": [0.7, 1.2], "variance": 1.8},
        noise_variance=0.015,
        jitter=1e-9,
    )
    oracle = kriging_reference(
        x,
        y,
        q,
        length_scale=[0.7, 1.2],
        variance=1.8,
        degree=degree,
        noise_variance=0.015,
        jitter=1e-9,
    )
    mean, variance = model.predict(q, return_variance=True)
    np.testing.assert_allclose(mean, oracle["mean"], rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(variance, oracle["variance"], rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(report["nll"], oracle["nll"], rtol=1e-7, atol=1e-9)
    assert isinstance(model.trend, PolynomialBasis)
    assert isinstance(model.condition, KrigingCondition)


def test_nontraining_unknown_trend_variance_counterexample():
    x = np.linspace(-1, 1, 6)[:, None]
    y = 2 + 3 * x[:, 0]
    q = np.array([[-1.5], [0.25], [1.5]])
    model, _ = condition_kriging(
        x,
        y,
        trend=PolynomialBasis(1, 1),
        kernel_config={"length_scale": 0.7},
        noise_variance=0.02,
        jitter=0,
    )
    mean, var = model.predict(q, return_variance=True)
    np.testing.assert_allclose(mean, 2 + 3 * q[:, 0], atol=1e-12)
    cross = model.covariance(q, x)
    known = 1 - (
        cross * np.linalg.solve(model.covariance(x, x) + 0.02 * np.eye(len(x)), cross.T).T
    ).sum(1)
    assert np.max(var - known) > 0.05
    assert np.all(var >= known)
    np.testing.assert_allclose(
        var,
        kriging_reference(x, y, q, length_scale=0.7, variance=1.0, degree=1, noise_variance=0.02)[
            "variance"
        ],
        rtol=1e-7,
        atol=1e-9,
    )


def test_nontraining_public_condition_is_actual_model_path(monkeypatch):
    x = np.arange(5.0)[:, None]
    model, _ = condition_kriging(x, np.sin(x[:, 0]))
    calls = []
    original = model.condition.predict

    def tracked(*args, **kwargs):
        calls.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(model.condition, "predict", tracked)
    model.predict(x)
    assert calls == [True]


def test_nontraining_noise_jitter_and_state_roundtrip():
    x = np.linspace(-1, 1, 7)[:, None]
    model, _ = condition_kriging(x, np.sin(x[:, 0]), jitter=0)
    mean, var = model.predict(x, return_variance=True)
    np.testing.assert_allclose(mean, np.sin(x[:, 0]), atol=1e-9)
    np.testing.assert_allclose(var, 0, atol=1e-12)
    noisy, _ = condition_kriging(x, np.sin(x[:, 0]), noise_variance=0.02, jitter=0.005)
    latent = noisy.predict(x, return_variance=True)[1]
    observed = noisy.predict(x, return_variance=True, query_noise=0.03)[1]
    np.testing.assert_allclose(observed - latent, 0.03, atol=1e-15)
    state = noisy.get_state()
    restored = Kriging.from_state(state)
    np.testing.assert_array_equal(restored.predict(x), noisy.predict(x))
    state["condition"]["alpha"][:] = 100
    np.testing.assert_array_equal(restored.predict(x), noisy.predict(x))
    assert restored.get_state()["condition"]["jitter"] == 0.005
    np.testing.assert_array_equal(
        restored.get_state()["condition"]["noise_variance"], np.full(7, 0.02)
    )
    with pytest.raises(ValueError, match="只在请求"):
        noisy.predict(x, query_noise=0.03)
    with pytest.raises(ValueError):
        noisy.predict(x, return_variance=True, query_noise=1j)


def test_nontraining_duplicate_and_rank_failures():
    x = np.array([[0.0], [0.0], [1.0], [2.0]])
    y = np.array([0.0, 1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="非正定"):
        condition_kriging(x, y, jitter=0)
    model, _ = condition_kriging(x, y, jitter=1e-6)
    assert np.isfinite(model.predict(x)).all()
    model, _ = condition_kriging(x, y, noise_variance=0.01, jitter=0)
    assert np.isfinite(model.predict(x)).all()
    with pytest.raises(ValueError, match="满列秩"):
        solve_kriging_condition(np.eye(5), np.ones((5, 2)), np.arange(5.0))
    with pytest.raises(ValueError, match="自由度"):
        solve_kriging_condition(np.eye(2), np.eye(2), np.ones(2))
    with pytest.raises(ValueError, match="常数或线性"):
        condition_kriging(np.arange(6.0)[:, None], np.arange(6.0), trend=PolynomialBasis(1, 2))


def test_nontraining_corrupt_state_and_negative_variance():
    x = np.arange(4.0)[:, None]
    model, _ = condition_kriging(x, np.sin(x[:, 0]))
    state = model.get_state()
    state["condition"]["chol_covariance"][0, 1] = 1
    with pytest.raises(ValueError, match="下三角"):
        Kriging.from_state(state)
    with pytest.raises(FloatingPointError, match="显著为负"):
        model.condition.predict(
            np.ones((1, 4)) * 100, np.ones(1), np.ones((1, 1)), return_variance=True
        )


def test_nontraining_optional_backend_missing_only_when_selected(monkeypatch):
    real_import = importlib.import_module

    def blocked(name, *args, **kwargs):
        if name == "lightgbm":
            raise ModuleNotFoundError("deliberately blocked")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", blocked)
    importlib.reload(real_import("ai4e_core.abilities.modeling.models.lightgbm"))
    assert np.isfinite(SquaredExponential()(np.ones((2, 1)), np.ones((1, 1)))).all()
    with pytest.raises(ImportError, match=r"ai4e-core\[boosting\]"):
        fit_boosting(
            np.arange(8.0).reshape(4, 2),
            np.arange(4.0),
            target_names=["response"],
            num_boost_round=1,
        )


def test_nontraining_stopping_does_not_start_optimization_or_tree_build(monkeypatch):
    import scipy.optimize

    def forbidden(*args, **kwargs):
        raise AssertionError("优化器不应在非法输入时调用")

    monkeypatch.setattr(scipy.optimize, "minimize", forbidden)
    with pytest.raises(ValueError, match="未知优化"):
        fit_kriging(np.arange(5.0)[:, None], np.arange(5.0), optimization={"bogus": 1})
    with pytest.raises(InterruptedError, match="取消"):
        fit_boosting(
            np.arange(8.0).reshape(4, 2),
            np.arange(4.0),
            target_names=["response"],
            cancelled=lambda: True,
        )
    with pytest.raises(ValueError, match="别名"):
        fit_boosting(
            np.arange(8.0).reshape(4, 2),
            np.arange(4.0),
            target_names=["response"],
            params={"n_estimators": 1},
        )
    with pytest.raises(ValueError, match="字段或版本"):
        LightGBMPredictor.from_state({"kind": "lightgbm", "version": 2})


def test_nontraining_reference_provenance_and_no_zero_mean_substitution():
    assert SOURCES["lightgbm"]["version"] == "4.6.0"
    assert SOURCES["lightgbm"]["license"] == "MIT"
    assert SOURCES["kriging"]["paper_reproduction"] is False
    x = np.arange(5.0)[:, None]
    q = np.array([[20.0]])
    oracle = kriging_reference(x, np.full(5, 7.0), q, length_scale=1.0, variance=1.0, degree=0)
    np.testing.assert_allclose(oracle["mean"], 7.0, atol=1e-12)


@pytest.mark.parametrize("degree", [0, 1])
def test_nontraining_profile_analytic_gradients_match_centered_differences(degree):
    from ai4e_core.abilities.training.kriging import kriging_profile_gradient

    x = np.array([[-1.0, -0.7], [-0.5, 0.8], [-0.2, -0.2], [0.2, 0.5], [0.6, -0.8], [1.0, 0.1]])
    y = 1.7 + 0.8 * x[:, 0] - 0.3 * x[:, 1] + 0.2 * np.sin(3 * x[:, 0])
    initial = np.log([0.7, 1.2, 1.8])
    basis = PolynomialBasis(2, degree)

    def values(parameters):
        positive = np.exp(parameters)
        model, report = condition_kriging(
            x,
            y,
            trend=basis,
            kernel_config={"length_scale": positive[:-1], "variance": float(positive[-1])},
            noise_variance=0.015,
            jitter=1e-9,
        )
        oracle = kriging_reference(
            x,
            y,
            x,
            length_scale=positive[:-1],
            variance=positive[-1],
            degree=degree,
            noise_variance=0.015,
            jitter=1e-9,
            return_gradient=True,
        )
        return report["nll"], oracle["nll"], kriging_profile_gradient(model), oracle["gradient"]

    _, _, product, reference = values(initial)
    np.testing.assert_allclose(product, reference, rtol=1e-9, atol=1e-10)
    product_fd, reference_fd = [], []
    step = 1e-5
    for axis in range(len(initial)):
        delta = np.zeros_like(initial)
        delta[axis] = step
        plus, minus = values(initial + delta), values(initial - delta)
        product_fd.append((plus[0] - minus[0]) / (2 * step))
        reference_fd.append((plus[1] - minus[1]) / (2 * step))
    np.testing.assert_allclose(product, product_fd, rtol=1e-6, atol=1e-7)
    np.testing.assert_allclose(reference, reference_fd, rtol=1e-6, atol=1e-7)
