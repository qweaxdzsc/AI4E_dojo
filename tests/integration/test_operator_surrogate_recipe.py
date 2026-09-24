"""本批资源、完整配置及用户组合的非训练验证；不构造优化器或更新参数。"""

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from ai4e_task.templates import resources
from omegaconf import OmegaConf

from ai4e_contrib.application.operator_learning.binding import construct
from ai4e_contrib.application.operator_learning.configuration import validate
from ai4e_core.abilities.data.save.surrogate import read_state, save_state
from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.modeling.models.pod import POD

ROOT = Path(__file__).resolve().parents[2]
STANDALONE = (
    "operator_learning.darcy",
    "operator_learning.shapenet_volume",
    "operator_learning.double_cylinder",
    "surrogate_modeling.nasa_crm",
    "surrogate_modeling.double_cylinder",
)
EXTENSIONS = (
    "recipe_extensions.operator_branch_replacement",
    "recipe_extensions.operator_physical_loss",
    "recipe_extensions.pod_surrogate_replacement",
)


@pytest.fixture(autouse=True)
def source_resources(monkeypatch):
    """资源指向源码；真实独立安装有专门证据测试，不能由此替代。"""
    monkeypatch.setattr(resources, "resource_root", lambda: ROOT)
    threads = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(threads)


@pytest.mark.parametrize("identity", STANDALONE + EXTENSIONS)
def test_nontraining_eight_resources_copy_and_five_recipe_sources(tmp_path, identity):
    catalog = {item["id"]: item for item in resources.list_examples()}
    case = catalog[identity]
    assert resources.check_example(identity)["ok"]
    target = tmp_path / "copied"
    resources.copy_example(identity, target)
    assert (target / "pipeline.py").is_file()
    assert all(
        (target / name).is_file()
        for name in ("config.yaml", "configuration.py", "train.py", "infer.py", "post.py")
    )
    if identity in STANDALONE:
        assert case["recipe_source"] == case["path"]
        for name in case["shared_stage_files"]:
            assert (ROOT / "examples" / case["path"] / name).read_bytes() == (
                ROOT / "recipes" / case["recipe_source"] / name
            ).read_bytes()


@pytest.mark.parametrize("case", ["darcy", "shapenet_volume", "double_cylinder"])
def test_nontraining_complete_omegaconf_reaches_operator_forward(case):
    cfg = OmegaConf.load(ROOT / "recipes/operator_learning" / case / "config.yaml")
    dims = cfg.model.spatial_dims
    cfg.model.family = "fno"
    cfg.model.grid_shape = [8] * dims
    cfg.model.parameters = {"modes": [2] * dims, "width": 4, "depth": 1, "padding": [1] * dims}
    full = validate(cfg)
    assert type(full) is dict
    assert type(full["model"]["parameters"]["modes"]) is list
    assert type(full["model"]["parameters"]["padding"]) is list
    model = construct(full).eval()
    history = full["model"].get("history", 1)
    shape = (
        (1, history, 8, 8, full["model"]["in_channels"])
        if history > 1
        else (1, *([8] * dims), full["model"]["in_channels"])
    )
    with torch.no_grad():
        output = model(torch.randn(shape))
    assert output.shape == (1, *([8] * dims), full["model"]["out_channels"])
    assert torch.isfinite(output).all()


def test_nontraining_copied_branch_is_consumed_and_state_restores(tmp_path, monkeypatch):
    target = tmp_path / "branch"
    resources.copy_example(EXTENSIONS[0], target)
    monkeypatch.syspath_prepend(str(target))
    previous = sys.modules.pop("branch_replacement", None)
    try:
        cfg = OmegaConf.load(target / "config.yaml")
        cfg.model.grid_shape = [8, 8, 8]
        cfg.model.parameters.sensor_stride = 4
        model = construct(validate(cfg)).double().eval()
        local = importlib.import_module("branch_replacement")
        assert Path(local.__file__).resolve().parent == target.resolve()
        assert isinstance(model.network.branch, local.ResidualBranch)
        calls = []
        handle = model.network.branch.register_forward_hook(lambda *_: calls.append(True))
        values, coordinates = (
            torch.randn(1, 8, 8, 8, 5, dtype=torch.float64),
            torch.randn(1, 8, 8, 8, 3, dtype=torch.float64),
        )
        with torch.no_grad():
            prediction = model(values, coordinates=coordinates)
        handle.remove()
        assert calls == [True] and prediction.shape == (1, 8, 8, 8, 3)
        state = {name: value.detach().numpy().copy() for name, value in model.state_dict().items()}
        manifest = save_state(
            tmp_path / "branch-state", state, context={"component": cfg.components.model}
        )
        loaded, context = read_state(manifest)
        restored = construct(validate(cfg)).double().eval()
        restored.load_state_dict(
            {name: torch.as_tensor(value) for name, value in loaded.items()}, strict=True
        )
        with torch.no_grad():
            torch.testing.assert_close(
                restored(values, coordinates=coordinates), prediction, rtol=0, atol=0
            )
        assert context["component"] == "branch_replacement.build_model"
    finally:
        sys.modules.pop("branch_replacement", None)
        if previous is not None:
            sys.modules["branch_replacement"] = previous


def test_nontraining_copied_pod_mlp_state_and_frozen_decoder_gradient(tmp_path, monkeypatch):
    target = tmp_path / "pod-extension"
    resources.copy_example(EXTENSIONS[2], target)
    monkeypatch.syspath_prepend(str(target))
    previous = sys.modules.pop("pod_mlp", None)
    try:
        local = importlib.import_module("pod_mlp")
        assert Path(local.__file__).resolve().parent == target.resolve()
        torch.manual_seed(47)
        network = MLP(6, 2, (4,)).double()
        # 人工已知正交基不调用SVD/POD拟合；仅验证冻结解码与可微组合。
        basis_state = {
            "kind": "pod-v1",
            "mean": np.arange(6, dtype=np.float64),
            "weights": np.ones(6),
            "basis": np.eye(6)[:, :2],
            "singular_values": np.array([3.0, 2.0]),
            "rank": 2,
        }
        mlp_state = {
            "kind": "local-pod-mlp-v1",
            "input_dim": 6,
            "output_dim": 2,
            "hidden": [4],
            "weights": {
                key: value.detach().numpy().copy() for key, value in network.state_dict().items()
            },
        }
        manifest = save_state(
            tmp_path / "pod-mlp-state",
            {"pod": basis_state, "predictor": mlp_state},
            context={"rank": 2},
        )
        state, context = read_state(manifest)
        predictor = local.rebuild(state["predictor"])
        decoder = POD.from_state(state["pod"]).torch_decoder(dtype=torch.float64)
        values = torch.randn(3, 6, dtype=torch.float64)
        np.testing.assert_array_equal(
            predictor.predict(values.numpy()), network(values).detach().numpy()
        )
        before = {
            key: value.detach().clone() for key, value in predictor.model.state_dict().items()
        }
        coefficients = predictor.model(values)
        decoded = decoder(coefficients)
        np.testing.assert_allclose(
            decoded.detach().numpy(), POD(state["pod"]).decode(coefficients.detach().numpy())
        )
        decoded.square().mean().backward()
        gradients = [parameter.grad for parameter in predictor.model.parameters()]
        assert all(
            gradient is not None and torch.isfinite(gradient).all() for gradient in gradients
        )
        assert any(torch.count_nonzero(gradient).item() > 0 for gradient in gradients)
        assert list(decoder.parameters()) == []
        assert context == {"rank": 2}
        for key, value in predictor.model.state_dict().items():
            torch.testing.assert_close(value, before[key], rtol=0, atol=0)
    finally:
        sys.modules.pop("pod_mlp", None)
        if previous is not None:
            sys.modules["pod_mlp"] = previous
