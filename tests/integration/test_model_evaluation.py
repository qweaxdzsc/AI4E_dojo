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

    from ai4e_core.applications.aero_cfd.infer.anchor_evaluation import (
        evaluate_model as post_evaluate,
    )

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


@pytest.mark.parametrize("names", [["mae"], ["mse", "relative_l2"], []])
def test_selected_metrics_are_calculated_and_loss_is_preserved(names):
    """反归一化后只交付所选项，清空仍计算用于选优的评估损失。"""
    normalization = Normalization(
        {
            "version": 1,
            "fields": {"p": {"method": "zscore", "parameters": {"mean": [0], "std": [2]}}},
        }
    )
    model = torch.nn.Linear(1, 1)
    batch = {
        "inputs": {"p": torch.tensor([[[2.0], [4.0]]])},
        "targets": {"p": torch.tensor([[[1.0], [2.0]]])},
    }
    result = evaluate(
        model,
        [batch],
        lambda _, x: x,
        [{"name": "p", "prediction": "p", "target": "p"}],
        normalization,
        metric_names=names,
    )
    assert result["loss"] == 2.5
    assert set(result["metrics"]) == {"p/" + name for name in names}
    expected = {"mse": 10.0, "mae": 3.0, "relative_l2": 1.0}
    for name in names:
        assert result["metrics"]["p/" + name]["value"] == pytest.approx(expected[name])


@pytest.mark.parametrize("names", [["unknown"], ["mse", "mse"], "mae", [3]])
def test_invalid_metric_selection_is_rejected_before_prediction(names):
    with pytest.raises(ValueError, match="评估指标"):
        evaluate(
            torch.nn.Linear(1, 1),
            [],
            lambda *_: pytest.fail("不应前向"),
            [],
            None,
            metric_names=names,
        )
    from ai4e_core.applications.aero_cfd.train.resolve import validate_joint

    with pytest.raises(ValueError, match="评估指标"):
        validate_joint({"train": {"evaluation_metrics": names}})


@pytest.mark.parametrize("names", [["mae"], []])
def test_training_configuration_hands_selected_metrics_to_real_fit(tmp_path, monkeypatch, names):
    """平台保存、训练装配、真实更新与训练报告交接同一指标选择。"""
    import json
    from types import SimpleNamespace

    from ai4e_server.modules.stages import compose_configuration

    from ai4e_core.applications.aero_cfd.train import fitting
    from tests.integration.test_train_loop import Run

    config = compose_configuration(
        {
            "train": {
                "evaluation_enabled": True,
                "max_epochs": 3,
                "batch_size": 1,
                "validation_interval": 2,
                "evaluation_split": "test",
                "test_repeat": 1,
            },
            "sampling": {},
            "trainprep": {},
        },
        "train",
        {"evaluation_metrics": names},
        edited_paths=[["evaluation_metrics"]],
    )
    batch = {"inputs": {"p": torch.ones(1, 2, 1)}, "targets": {"p": torch.ones(1, 2, 1) * 2}}
    calls = []

    def batches(index, partition, **kwargs):
        calls.append(partition)
        yield batch

    monkeypatch.setattr(fitting, "iter_partition_batches", batches)
    monkeypatch.setattr(
        fitting, "describe_model", lambda *_: {"model_version": 1, "input_layout": {}}
    )
    model = torch.nn.Linear(1, 1)
    data = SimpleNamespace(
        index=SimpleNamespace(
            manifest={"state": "physical"}, partitions={"train": ["s"], "test": ["t"]}
        ),
        normalization=Normalization(
            {
                "version": 1,
                "fields": {"p": {"method": "zscore", "parameters": {"mean": [0], "std": [1]}}},
            }
        ),
        physical_prepare=None,
        prepare=None,
        collate=None,
    )
    run = Run(tmp_path)
    run.run_dir = run.writer.run_dir
    job = fitting.TrainingJob(
        config, run, data, torch.nn.Linear, lambda network, x: {"p": network(x["p"])}, "fixture"
    )
    job.model, job.device = model, torch.device("cpu")
    job.terms = [{"name": "p", "prediction": "p", "target": "p"}]
    job.optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    fitting.configure_evaluation(job)
    result = fitting.execute_training(job)
    assert result["updates"] == 3
    history = json.loads((run.run_dir / "artifacts/training.json").read_text())["history"]
    assert history[1]["evaluation"] is None
    for row in [history[0], history[2]]:
        assert set(row["evaluation"]["metrics"]) == {"p/" + name for name in names}
        assert row["learning_rate"] == 0.1
    assert calls.count("test") == 2
    job.config["train"].update(max_epochs=4, evaluation_metrics=["mse"])
    fitting.configure_evaluation(job)
    fitting.configure_resume(job, checkpoint=str(run.run_dir / "checkpoints/last.pt"))
    resumed = fitting.execute_training(job)
    assert resumed["updates"] == 4
    assert set(resumed["history"][-1]["evaluation"]["metrics"]) == {"p/mse"}
    job.data.index.partitions["test"] = []
    with pytest.raises(ValueError, match="评估分片 test 为空"):
        fitting.configure_evaluation(job)


def test_training_metric_capability_is_owned_by_algorithm():
    from types import SimpleNamespace

    from ai4e_server.modules.stages.application import _capability_options

    from ai4e_core.applications.aero_cfd.inspection import parameter_capabilities

    caps = parameter_capabilities({"train": {"evaluation_enabled": False}}, SimpleNamespace())
    described = _capability_options({"capabilities": caps})
    assert described["evaluation_metrics"]["default"] == ["mse", "mae", "relative_l2"]
    assert [item["value"] for item in described["evaluation_metrics"]["options"]] == [
        "mse",
        "mae",
        "relative_l2",
    ]
