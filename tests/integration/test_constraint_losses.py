"""监督比较方法与门禁；不覆盖物理约束。"""

from pathlib import Path

import pytest
import torch
import torch.nn.functional as F
from omegaconf import OmegaConf

from ai4e_core.abilities.constraint.compare import compare
from ai4e_core.abilities.constraint.supervised import supervised, supervised_mse
from ai4e_core.abilities.eval.evaluation import evaluate
from ai4e_core.abilities.training.split import route
from ai4e_core.applications.aero_cfd.model.objectives import objectives
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd/config.yaml"


def test_compare_four_methods_match_formulas():
    prediction = torch.tensor([[1.0, 3.0], [2.0, 0.0]])
    target = torch.tensor([[0.0, 1.0], [2.0, 2.0]])
    delta = prediction - target
    torch.testing.assert_close(compare(prediction, target, "mse"), delta.square().mean())
    torch.testing.assert_close(compare(prediction, target, "mae"), delta.abs().mean())
    torch.testing.assert_close(
        compare(prediction, target, "huber"),
        F.huber_loss(prediction, target, reduction="mean", delta=1.0),
    )
    torch.testing.assert_close(
        compare(prediction, target, "relative_l2"),
        torch.linalg.vector_norm(delta) / torch.linalg.vector_norm(target),
    )
    torch.testing.assert_close(
        compare(prediction, target, "huber", delta=0.5),
        F.huber_loss(prediction, target, reduction="mean", delta=0.5),
    )


def test_compare_rejects_shape_empty_unknown_and_tiny_relative():
    with pytest.raises(ValueError, match="形状"):
        compare(torch.ones(2, 1), torch.zeros(2), "mse")
    with pytest.raises(ValueError, match="形状"):
        compare(torch.ones(0), torch.ones(0), "mse")
    with pytest.raises(ValueError, match="未知"):
        compare(torch.ones(1), torch.zeros(1), "nope")
    with pytest.raises(ValueError, match="范数"):
        compare(torch.ones(2), torch.zeros(2), "relative_l2")
    with pytest.raises(ValueError, match="宽度"):
        compare(torch.ones(1), torch.zeros(1), "huber", delta=0)


def test_supervised_default_and_alias_match_explicit_mse():
    predictions = {"p": torch.ones(2, 1)}
    targets = {"p": torch.zeros(2, 1)}
    bare = [{"name": "p", "prediction": "p", "target": "p", "weight": 1}]
    explicit = [{**bare[0], "loss": "mse"}]
    unnamed = supervised(predictions, targets, bare)
    named = supervised(predictions, targets, explicit)
    alias = supervised_mse(predictions, targets, [{**bare[0], "loss": "mae"}])
    torch.testing.assert_close(unnamed["loss"], named["loss"])
    torch.testing.assert_close(unnamed["loss"], alias["loss"])
    assert unnamed["loss"] == 1


def test_supervised_mae_and_gates():
    terms = [{"name": "p", "prediction": "p", "target": "p", "weight": 2, "loss": "mae"}]
    result = supervised({"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, terms)
    assert result["loss"] == 2
    with pytest.raises(ValueError, match="形状"):
        supervised({"p": torch.ones(2, 1)}, {"p": torch.zeros(2)}, terms)
    with pytest.raises(ValueError, match="未知"):
        supervised(
            {"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, [{**terms[0], "loss": "nope"}]
        )
    with pytest.raises(ValueError, match="权重"):
        supervised({"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, [{**terms[0], "weight": -1}])
    with pytest.raises(ValueError, match="正权重"):
        supervised({"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, [{**terms[0], "weight": 0}])
    with pytest.raises(ValueError, match="监督项"):
        supervised({"p": torch.ones(2, 1)}, {"p": torch.zeros(2, 1)}, [])


def test_aero_cfd_objectives_default_two_mse():
    resolved = apply_resolved(OmegaConf.to_container(OmegaConf.load(RECIPE), resolve=True))
    terms = objectives(resolved["model"])
    assert [item["name"] for item in terms] == ["surface_pressure", "volume_velocity"]
    assert all(item["loss"] == "mse" and item["weight"] == 1.0 for item in terms)


def test_recipe_default_losses_are_mse():
    resolved = apply_resolved(OmegaConf.to_container(OmegaConf.load(RECIPE), resolve=True))
    terms = objectives(resolved["model"])
    assert [item["loss"] for item in terms] == ["mse", "mse"]
    assert all(item["weight"] == 1.0 for item in terms)


def test_recipe_rejects_unknown_loss_method():
    cfg = OmegaConf.load(RECIPE)
    cfg.model.supervision[0].loss = "nope"
    with pytest.raises(ValueError, match="未知比较方法"):
        apply_resolved(OmegaConf.to_container(cfg, resolve=True))


@pytest.mark.parametrize("method", ["mse", "mae", "huber", "relative_l2"])
def test_recipe_losses_reach_train_step_and_eval(method):
    cfg = OmegaConf.load(RECIPE)
    for term in cfg.model.supervision:
        term.loss = method
    resolved = apply_resolved(OmegaConf.to_container(cfg, resolve=True))
    terms = objectives(resolved["model"])
    assert {item["name"]: item["loss"] for item in terms} == {
        "surface_pressure": method,
        "volume_velocity": method,
    }
    pressure = torch.tensor([[[2.0], [0.0]]], requires_grad=True)
    velocity = torch.tensor([[[2.0, 0.0, 1.0], [0.0, 1.0, 2.0]]], requires_grad=True)
    pressure_target = torch.ones_like(pressure)
    velocity_target = torch.ones_like(velocity)
    predictions = {"surface_pressure": pressure, "volume_velocity": velocity}
    targets = {
        "surface_pressure_target": pressure_target,
        "volume_velocity_target": velocity_target,
    }
    step = supervised(
        route(predictions, [item["prediction"] for item in terms], kind="预测"),
        route(targets, [item["target"] for item in terms], kind="目标"),
        terms,
    )
    expected = compare(pressure, pressure_target, method) + compare(
        velocity, velocity_target, method
    )
    torch.testing.assert_close(step["loss"], expected)

    normalization = Normalization(
        {
            "version": 1,
            "fields": {
                name: {
                    "method": "zscore",
                    "parameters": {
                        "mean": [0] * (3 if name == "volume_velocity" else 1),
                        "std": [1] * (3 if name == "volume_velocity" else 1),
                    },
                }
                for name in ["surface_pressure", "volume_velocity"]
            },
        }
    )
    result = evaluate(
        torch.nn.Linear(1, 1),
        [{"inputs": predictions, "targets": targets}],
        lambda _, inputs: inputs,
        terms,
        normalization,
    )
    assert result["loss"] == pytest.approx(step["loss"].item())
    assert set(result["losses"]) == {item["name"] for item in terms}
    assert sum(result["losses"].values()) == pytest.approx(result["loss"])
    step["loss"].backward()
    assert pressure.grad is not None and velocity.grad is not None
