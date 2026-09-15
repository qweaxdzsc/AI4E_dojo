"""完整预算梯形的双方原始产物验证；未提供实跑目录时不冒充数值验收。"""

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]


def test_incomplete_budget_cannot_publish_report(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "trapezoid_dojo_verification", ROOT / "tools/verification/pibsnet/trapezoid_dojo.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checkpoint = tmp_path / "runs/short/checkpoints/last.pt"
    checkpoint.parent.mkdir(parents=True)
    torch.save({"epoch": 2999, "updates": 29990}, checkpoint)
    with pytest.raises(AssertionError):
        module.report(tmp_path, tmp_path / "reference")
    assert not (tmp_path / "verification.json").exists()


def test_full_training_weights_history_and_all_fields():
    value = os.environ.get("DOJO_TRAPEZOID_ACCEPTANCE_ROOT")
    if not value:
        pytest.skip("显式提供完整实跑目录；skip不是数值验收")
    root = Path(value)
    verification = json.loads((root / "verification.json").read_text())
    state = torch.load(verification["checkpoint"], weights_only=False)
    reference = torch.load(root / "same_environment_reference/last.pt", weights_only=False)
    assert (state["epoch"], state["updates"]) == (3000, 30000)
    assert len(state["history"]) == len(reference["history"]) == 3000
    assert [r["loss"] for r in state["history"]] == reference["history"]
    assert np.isfinite(reference["history"]).all()
    assert set(state["model"]) == set(reference["model"])
    for name in state["model"]:
        torch.testing.assert_close(state["model"][name], reference["model"][name], rtol=0, atol=0)
    arrays = sorted((root / "predictions").glob("test-*.pt"))
    assert len(arrays) == 10
    error = []
    for file in arrays:
        actual = torch.load(file, weights_only=False)
        with np.load(root / "same_environment_reference" / f"{file.stem}.npz") as expected:
            np.testing.assert_array_equal(actual["prediction"].numpy(), expected["prediction"])
            np.testing.assert_array_equal(actual["target"].numpy(), expected["target"])
        p, t = actual["prediction"], actual["target"]
        assert tuple(p.shape) == (1001, 21, 21)
        assert torch.isfinite(p).all()
        error.extend(
            (
                (p - t).double().flatten(1).norm(dim=1)
                / (t.double().flatten(1).norm(dim=1) + 1e-12)
            ).tolist()
        )
    assert np.mean(error) == pytest.approx(verification["mean_time_relative_l2"], abs=1e-12)
