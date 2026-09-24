"""小矩阵代数反例、独立参考、状态往返与真实公共组件复用；不跑真实拟合。"""

import copy
import io

import numpy as np
import pytest
import torch

from ai4e_core.abilities.modeling.models.pod import POD
from ai4e_core.abilities.modeling.models.rbf import RBFInterpolator
from ai4e_core.abilities.modeling.models.rsm import ResponseSurface
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
from ai4e_core.abilities.modeling.modules.radial import RadialBasis
from ai4e_core.abilities.training.algebraic import fit_least_squares, fit_rbf, fit_rsm
from ai4e_core.abilities.training.reduced_basis import fit_pod
from tools.verification.operator_surrogates import reference_algebraic as reference


def fixture_values():
    rng = np.random.default_rng(47)
    x = rng.uniform(-1, 1, (40, 3))
    y = np.column_stack((x[:, 0] ** 2 + 2 * x[:, 1] * x[:, 2] + 4, 3 * x[:, 2] - x[:, 0]))
    return rng, x, y


@pytest.mark.parametrize("degree,count", [(0, 1), (1, 7), (2, 28)])
def test_polynomial_order_reference_and_restoration(degree, count):
    x = np.random.default_rng(10).normal(size=(9, 6))
    basis = PolynomialBasis(6, degree)
    expected = reference.PolynomialFeatures(degree).fit(x)
    np.testing.assert_array_equal(basis.powers, expected.powers_)
    np.testing.assert_allclose(basis(x), expected.transform(x), rtol=1e-14, atol=1e-14)
    assert basis(x).shape == (9, count)
    np.testing.assert_array_equal(PolynomialBasis.from_state(basis.to_state())(x), basis(x))
    invalid = basis.to_state()
    invalid["powers"][0][0] += 1
    with pytest.raises(ValueError, match="指数"):
        PolynomialBasis.from_state(invalid)


@pytest.mark.parametrize("kwargs", [{"degree": 3}, {"degree": 0, "include_bias": False}])
def test_polynomial_invalid_definition(kwargs):
    with pytest.raises(ValueError):
        PolynomialBasis(2, **kwargs)


def test_weighted_pod_optimal_projection_and_no_refit():
    rng, _, _ = fixture_values()
    x = rng.normal(size=(11, 20)) + 3
    weights = np.exp(rng.normal(size=20))
    state = fit_pod(x, 4, weights=weights)
    model = POD(state)
    oracle = reference.fit_pod(x, 4, weights=weights)
    np.testing.assert_allclose(
        state["basis"].T @ (weights[:, None] * state["basis"]), np.eye(4), rtol=1e-12, atol=1e-12
    )
    np.testing.assert_allclose(model.reconstruct(x), oracle.reconstruct(x), rtol=1e-11, atol=1e-11)
    error = ((x - model.reconstruct(x)) ** 2 * weights).sum()
    np.testing.assert_allclose(error, (state["singular_values"][4:] ** 2).sum(), rtol=1e-12)
    unseen = rng.normal(size=(2, 3, 20)) + 100
    assert model.encode(unseen).shape == (2, 3, 4)
    before = model.to_state()
    model.reconstruct(unseen)
    for key in ("mean", "basis", "weights"):
        np.testing.assert_array_equal(model.to_state()[key], before[key])


@pytest.mark.parametrize("case", ["constant", "rank", "weight", "complex", "nonfinite"])
def test_pod_degenerate_inputs_fail(case):
    x = np.arange(24.0).reshape(6, 4)
    weights = np.ones(4)
    rank = 1
    if case == "constant":
        x[:] = 1
    if case == "rank":
        rank = 2
    if case == "weight":
        weights[0] = 0
    if case == "complex":
        x = x.astype(complex) + 1j
    if case == "nonfinite":
        x[0, 0] = np.nan
    with pytest.raises(ValueError):
        fit_pod(x, rank, weights=weights)


def test_pod_torch_decoder_gradient_buffers_and_state_readback():
    x = np.random.default_rng(11).normal(size=(9, 13))
    model = POD(fit_pod(x, 3, weights=np.arange(1.0, 14.0)))
    decoder = model.torch_decoder()
    coefficients = torch.randn(2, 4, 3, dtype=torch.float64, requires_grad=True)
    output = decoder(coefficients)
    np.testing.assert_allclose(
        output.detach().numpy(), model.decode(coefficients.detach().numpy()), rtol=1e-13, atol=1e-13
    )
    output.sum().backward()
    torch.testing.assert_close(coefficients.grad, decoder.basis.sum(0).expand_as(coefficients))
    assert list(decoder.parameters()) == []
    buffer = io.BytesIO()
    torch.save(decoder.state_dict(), buffer)
    buffer.seek(0)
    restored = model.torch_decoder()
    restored.load_state_dict(torch.load(buffer, weights_only=True))
    torch.testing.assert_close(restored(coefficients), output, rtol=0, atol=0)
    # 冻结解码接入已有MLP，梯度可回传而无需改变训练器；不更新参数。
    from ai4e_core.abilities.modeling.models.mlp import MLP

    network = MLP(2, 3, (5,)).double()
    decoder(network(torch.randn(4, 2, dtype=torch.float64))).square().sum().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in network.parameters())


@pytest.mark.parametrize("degree", [1, 2])
def test_response_surface_multitarget_independent_fit(degree):
    rng, x, y = fixture_values()
    state = fit_rsm(x, y, degree=degree)
    model = ResponseSurface(state)
    oracle = reference.fit_rsm(x, y, degree=degree)
    query = rng.normal(size=(7, 3))
    np.testing.assert_allclose(model.predict(query), oracle.predict(query), rtol=1e-11, atol=1e-11)
    if degree == 2:
        np.testing.assert_allclose(model.predict(x), y, rtol=1e-12, atol=1e-12)


def test_underdetermined_rsm_requires_explicit_regularization():
    x = np.random.default_rng(44).normal(size=(2, 6))
    y = np.array([[1.0, 2], [3, 4]])
    with pytest.raises(ValueError, match="秩不足"):
        fit_rsm(x, y)
    model = ResponseSurface(fit_rsm(x, y, ridge=0.2))
    np.testing.assert_allclose(
        model(x), reference.fit_rsm(x, y, ridge=0.2).predict(x), rtol=1e-11, atol=1e-11
    )
    assert model.to_state()["diagnostics"]["rank"] == 2


@pytest.mark.parametrize("smoothing", [0.0, 0.01])
def test_rbf_independent_multioutput_interpolation_and_smoothing(smoothing):
    rng, x, y = fixture_values()
    y = y + np.sin(4 * x[:, :1])
    state = fit_rbf(x, y, smoothing=smoothing)
    model = RBFInterpolator(state)
    oracle = reference.fit_rbf(x, y, smoothing=smoothing)
    query = rng.uniform(-1, 1, size=(7, 3))
    np.testing.assert_allclose(model(query), oracle(query), rtol=1e-10, atol=1e-10)
    p = model.polynomial((x - state["shift"]) / state["scale"])
    np.testing.assert_allclose(p.T @ state["radial_coefficients"], 0, atol=1e-10)
    if smoothing == 0:
        np.testing.assert_allclose(model(x), y, rtol=1e-10, atol=1e-10)
    else:
        assert np.max(abs(model(x) - y)) > 1e-5


def test_rbf_linear_reproduction_and_failures():
    rng, x, _ = fixture_values()
    y = np.column_stack((1 + 2 * x[:, 0] - x[:, 1], x[:, 2]))
    model = RBFInterpolator(fit_rbf(x, y))
    query = rng.normal(size=(5, 3))
    np.testing.assert_allclose(
        model(query),
        np.column_stack((1 + 2 * query[:, 0] - query[:, 1], query[:, 2])),
        rtol=1e-11,
        atol=1e-11,
    )
    with pytest.raises(ValueError, match="重复中心"):
        fit_rbf(np.concatenate((x, x[:1])), np.concatenate((y, y[:1])))
    with pytest.raises(ValueError, match="尾项"):
        fit_rbf(x, y, polynomial=PolynomialBasis(3, 0))
    with pytest.raises(ValueError, match="秩不足"):
        fit_rbf(np.column_stack((x[:, 0], x[:, 0])), y)


def test_state_roundtrip_and_tampering(tmp_path):
    _, x, y = fixture_values()
    pairs = [
        (POD(fit_pod(y, 2)), y),
        (ResponseSurface(fit_rsm(x, y)), x),
        (RBFInterpolator(fit_rbf(x, y)), x),
    ]
    for index, (model, inputs) in enumerate(pairs):
        state = model.to_state()
        # 本测试只证数值状态持久化；主控另测正式清单与迁移。
        arrays = {key: value for key, value in state.items() if isinstance(value, np.ndarray)}
        path = tmp_path / f"{index}.npz"
        np.savez(path, **arrays)
        with np.load(path, allow_pickle=False) as loaded:
            restored_state = {**state, **{key: loaded[key].copy() for key in loaded.files}}
        restored = type(model).from_state(restored_state)
        operation = "reconstruct" if isinstance(model, POD) else "predict"
        np.testing.assert_array_equal(
            getattr(model, operation)(inputs), getattr(restored, operation)(inputs)
        )
    broken = pairs[0][0].to_state()
    broken["basis"] = broken["basis"] * 2
    with pytest.raises(ValueError, match="正交"):
        POD(broken)
    broken = pairs[1][0].to_state()
    broken["coefficients"] = broken["coefficients"][:-1]
    with pytest.raises(ValueError):
        ResponseSurface(broken)
    broken = pairs[2][0].to_state()
    broken["scale"][0] = 0
    with pytest.raises(ValueError):
        RBFInterpolator(broken)


def test_complete_models_use_injected_public_blocks():
    _, x, y = fixture_values()

    class SpyPolynomial(PolynomialBasis):
        calls = 0

        def __call__(self, inputs):
            self.calls += 1
            return super().__call__(inputs)

    polynomial = SpyPolynomial(3, 2)
    model = ResponseSurface(fit_rsm(x, y, basis=polynomial), basis=polynomial)
    previous = polynomial.calls
    model(x)
    assert polynomial.calls == previous + 1
    radial = RadialBasis()
    tail = SpyPolynomial(3, 1)
    model = RBFInterpolator(
        fit_rbf(x, y, radial=radial, polynomial=tail), radial=radial, polynomial=tail
    )
    previous = tail.calls
    model(x)
    assert model.radial is radial and tail.calls == previous + 1
    representation = POD(fit_pod(y, 2)).representation
    assert POD(representation=representation).representation is representation


def test_source_identity_and_reference_independence():
    metadata = reference.source_identity()
    assert metadata["paper_reproduction"] is False
    assert all(len(item["sha256"]) == 64 for item in metadata["sources"].values())
    import inspect

    assert "ai4e_core" not in inspect.getsource(reference)


@pytest.mark.parametrize("operation", [fit_rsm, fit_rbf, fit_least_squares])
def test_algebraic_nonfinite_and_target_mismatch(operation):
    _, x, y = fixture_values()
    with pytest.raises(ValueError):
        operation(x, y[:2])
    bad = copy.deepcopy(y)
    bad[0, 0] = np.inf
    with pytest.raises(ValueError):
        operation(x, bad)
