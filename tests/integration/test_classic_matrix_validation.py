"""矩阵完整恢复和独立test预测的非训练fixture验证。"""

import copy
import json
import random
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from ai4e_core.abilities.data.save.array_manifest import save_arrays
from tools.verification.classic_networks.run_matrix import (
    compare_checkpoints,
    compare_reference_predictions,
    reference_test_predictions,
)


def checkpoint():
    return {
        "version": 2,
        "model": {"weight": torch.tensor([1.0, 2.0])},
        "optimizer": {
            "state": {
                0: {
                    "step": torch.tensor(3.0),
                    "exp_avg": torch.tensor([0.1, 0.2]),
                    "exp_avg_sq": torch.tensor([0.01, 0.04]),
                }
            },
            "param_groups": [{"lr": 0.001, "params": [0], "betas": (0.9, 0.999)}],
        },
        "epoch": 0,
        "updates": 3,
        "best": float("inf"),
        "contract": {"seed": 42, "lr": 0.001},
        "python_rng": random.getstate(),
        "numpy_rng": np.random.get_state(),
        "torch_rng": torch.get_rng_state(),
        "cuda_rng": None,
        "mps_rng": None,
        "ema": None,
        "scaler": None,
        "scheduler": None,
        "loop_kind": "iterations",
        "stream": {
            "count": 2,
            "batch_size": 1,
            "offset": 1,
            "order": torch.tensor([1, 0]),
            "rng": torch.Generator().manual_seed(42).get_state(),
        },
        "history": [0.4, 0.3, 0.2],
        "algorithm_state": {},
        "status": "complete",
        "effective_config": {"run_root": "first", "inputs": {"resume": None}},
    }


def test_full_checkpoint_comparison_ignores_only_execution_metadata():
    original = checkpoint()
    restored = copy.deepcopy(original)
    restored["effective_config"] = {"run_root": "resumed", "inputs": {"resume": "old.pt"}}
    report = compare_checkpoints(original, restored)
    assert report["maximum_difference"] == 0
    assert report["contract_compared_exactly"]
    assert set(report["components"]) == set(original) - {"effective_config"}


@pytest.mark.parametrize(
    "changed",
    ["optimizer", "step", "stream", "torch_rng", "numpy_rng", "contract", "scheduler", "missing"],
)
def test_full_checkpoint_detects_non_model_recovery_errors(changed):
    original = checkpoint()
    restored = copy.deepcopy(original)
    if changed == "optimizer":
        restored["optimizer"]["state"][0]["exp_avg"][0] += 0.01
    elif changed == "step":
        restored["optimizer"]["state"][0]["step"] += 0.000001
    elif changed == "stream":
        restored["stream"]["offset"] = 2
    elif changed == "torch_rng":
        restored["torch_rng"][0] ^= 1
    elif changed == "numpy_rng":
        restored["numpy_rng"][1][0] ^= 1
    elif changed == "contract":
        restored["contract"]["lr"] += 1e-9
    elif changed == "scheduler":
        restored["scheduler"] = {"last_epoch": 2}
    else:
        del restored["optimizer"]
    with pytest.raises(AssertionError):
        compare_checkpoints(original, restored)


class ReferenceGrid(nn.Module):
    def __init__(self):
        super().__init__()
        self.factor = nn.Parameter(torch.tensor(2.0))
        self.child = nn.Dropout(0.1)
        self.calls = 0

    def forward(self, value, valid=None, coordinates=None):
        self.calls += 1
        assert not self.training
        torch.rand(1)
        return value[..., :1] * self.factor


def prepared_fixture(root, *, corrupt=False):
    x = np.arange(36, dtype=np.float32).reshape(2, 2, 3, 3) / 10
    valid = np.ones((2, 2, 3), bool)
    valid[0, 0, 0] = False
    arrays = {
        "input": x,
        "physical_input": x.copy(),
        "target": x[..., :1],
        "physical_target": x[..., :1] * 3 + 10,
        "valid": valid,
        "entity_ids": np.broadcast_to(np.arange(6).reshape(2, 3), (2, 2, 3)).copy(),
    }
    metadata = {
        "case": "darcy",
        "ids": ["a", "b"],
        "fields": ["sol"],
        "units": ["1"],
        "statistics": {"target": {"mean": [10.0], "scale": [3.0]}},
    }
    manifest = save_arrays(
        root / "prepared" / "test", arrays, kind="classic-inputs-v1", metadata=metadata
    )
    prepared = root / "prepared" / "manifest.json"
    prepared.write_text(
        json.dumps(
            {
                "kind": "classic-preparation-v1",
                "splits": {"test": str(Path(manifest).relative_to(prepared.parent))},
            }
        )
    )
    prediction = x[..., :1] * 6 + 10
    prediction[~valid] = 0
    if corrupt:
        prediction[1, 0, 0, 0] += 0.1
    fixed = save_arrays(
        root / "fixed",
        {
            "prediction": prediction,
            "target": arrays["physical_target"],
            "valid": valid,
            "entity_ids": arrays["entity_ids"],
            "physical_input": x,
        },
        kind="classic-results-v1",
        metadata=metadata,
    )
    cfg = {"dataset": {"case": "darcy"}, "model": {"family": "mlp"}}
    return cfg, arrays, {"metadata": metadata}, prepared, fixed


def test_independent_full_test_predictions_restore_rng_modes_and_mask(tmp_path):
    cfg, arrays, record, prepared, fixed = prepared_fixture(tmp_path)
    model = ReferenceGrid()
    model.train()
    model.child.eval()
    rng = torch.get_rng_state().clone()
    expected = arrays["input"][..., :1] * 6 + 10
    expected[~arrays["valid"]] = 0
    actual = reference_test_predictions(model, cfg, arrays, record, "cpu")
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-6)
    assert model.calls == 2 and model.training and not model.child.training
    assert torch.equal(rng, torch.get_rng_state())
    report = compare_reference_predictions(
        model, cfg, prepared, fixed, tmp_path / "comparison", "cpu"
    )
    assert report["samples"] == 2 and report["valid_points"] == 11
    assert report["valid_maximum_difference"] < 1e-5
    saved = np.load(report["prediction"])
    np.testing.assert_array_equal(saved["valid"], arrays["valid"])
    np.testing.assert_allclose(saved["prediction"], expected, rtol=1e-5, atol=1e-6)


def test_prediction_failure_preserves_difference_evidence(tmp_path):
    cfg, _, _, prepared, fixed = prepared_fixture(tmp_path, corrupt=True)
    output = tmp_path / "comparison"
    with pytest.raises(AssertionError):
        compare_reference_predictions(ReferenceGrid(), cfg, prepared, fixed, output, "cpu")
    report = json.loads((output / "comparison.json").read_text())
    assert report["maximum_difference"] > 0.09
    assert (output / "reference-prediction.npz").is_file()
