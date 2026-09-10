"""共享评估的物理指标与异常状态恢复。"""

import pytest
import torch

from ai4e_core.abilities.eval.evaluation import evaluate
from ai4e_core.abilities.eval.metrics import field_metrics
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization


def test_metrics_zero_target():
    result = field_metrics(torch.ones(3, 1), torch.zeros(3, 1))
    assert result == {"mse": 1.0, "mae": 1.0, "relative_l2": None}


def test_evaluation_restores_state_on_failure():
    model = torch.nn.Sequential(torch.nn.Linear(1, 1), torch.nn.Dropout())
    model.train()
    model[0].eval()
    rng = torch.get_rng_state().clone()

    def fail(*args):
        torch.rand(5)
        raise RuntimeError("injected")

    with pytest.raises(RuntimeError):
        evaluate(model, [{"inputs": {}}], fail, [], Normalization({"version": 1, "fields": {}}))
    assert model.training and not model[0].training and model[1].training
    assert torch.equal(rng, torch.get_rng_state())


def test_evaluation_is_per_sample_and_shared_with_post():
    import random

    import numpy as np

    from ai4e_core.applications.aero_cfd.post.evaluation import evaluate_model as post_evaluate

    model = torch.nn.Linear(1, 1)
    normalization = Normalization(
        {
            "version": 1,
            "fields": {
                name: {
                    "method": "zscore",
                    "parameters": {
                        "mean": [0] * (3 if name == "volume_velocity" else 1),
                        "std": [2] * (3 if name == "volume_velocity" else 1),
                    },
                }
                for name in ["surface_pressure", "volume_velocity"]
            },
        }
    )
    terms = [
        {"name": name, "prediction": name, "target": name + "_target", "weight": 1}
        for name in ["surface_pressure", "volume_velocity"]
    ]
    calls = []

    def predict(_, inputs):
        calls.append(1)
        random.random()
        np.random.rand()
        torch.rand(1)
        return inputs

    def batch(values):
        p = torch.tensor(values).reshape(-1, 1, 1).float()
        return {
            "inputs": {"surface_pressure": p, "volume_velocity": p.expand(-1, 1, 3)},
            "targets": {
                "surface_pressure_target": torch.zeros_like(p),
                "volume_velocity_target": torch.zeros_like(p.expand(-1, 1, 3)),
            },
        }

    rng = torch.get_rng_state().clone()
    result = evaluate(model, [batch([1, 2]), batch([3])], predict, terms, normalization)
    assert len(calls) == 2
    assert result["loss"] == pytest.approx(28 / 3)
    assert result["losses"] == pytest.approx(
        {"surface_pressure": 14 / 3, "volume_velocity": 14 / 3}
    )
    assert sum(result["losses"].values()) == pytest.approx(result["loss"])
    assert len(result["metrics"]) == 6
    assert result["metrics"]["surface_pressure/mse"]["value"] == pytest.approx(56 / 3)
    assert result["metrics"]["surface_pressure/relative_l2"] == {
        "value": None,
        "valid": 0,
        "skipped": 3,
    }
    assert model.training and torch.equal(rng, torch.get_rng_state())
    other = post_evaluate(
        model,
        [batch([1]), batch([2]), batch([3])],
        predict=predict,
        objectives=terms,
        normalization=normalization,
    )
    assert other["loss"] == pytest.approx(result["loss"])
    assert other["losses"] == pytest.approx(result["losses"])
    assert other["metrics"] == result["metrics"]
