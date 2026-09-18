"""真实原仓库切片产物门槛；无真实数据不能记作通过。"""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from tools.verification.wdno.protocol import digest, verify


@pytest.fixture
def root():
    location = os.environ.get("DOJO_WDNO_SLICE_ROOT")
    if not location:
        pytest.skip("需显式指定真实三小时切片，不以合成产物替代")
    return Path(location)


def test_actual_original_trainer_budget_checkpoint_and_provenance(root):
    verify(root / "frozen")
    output = root / "main"
    result = json.loads((output / "result.json").read_text())
    acceptance = json.loads((output / "acceptance.json").read_text())
    ledger = json.loads((root / "budget.json").read_text())
    assert result["status"] == "slice_complete" and not result["diagnostic"]
    assert result["parameters"] == 140748553 and result["original_trainer"]
    assert result["ema_initial_step"] == 0 and 0 < result["updates"] <= 2000
    assert acceptance["updates"] == result["updates"]
    history = json.loads((output / "losses.json").read_text())
    assert len(history) == result["updates"]
    assert result["last_loss"] == history[-1]["loss"]
    assert acceptance["checkpoint_replay"]["ema_step"] == result["updates"]
    assert acceptance["checkpoint_replay"]["status"] == "passed"
    assert acceptance["checkpoint_sha256"] == digest(output / "checkpoints" / "latest.pt")
    assert acceptance["cumulative_seconds"] <= ledger["seconds"] <= 10800
    assert all(entry["status"] != "running" for entry in ledger["runs"])
    assert acceptance["paper_reproduced"] is False
    assert acceptance["dojo_migrated"] is False
    assert acceptance["paper_comparable"] is False
    entries = json.loads((output / "entry-source.json").read_text())
    assert entries["reference_sha256"] == digest(output / "entry-code" / "reference.py")
    assert entries["protocol_tool_sha256"] == digest(output / "entry-code" / "protocol.py")


def test_all_fixed_samples_and_source_metric_are_present(root):
    output = root / "main"
    indices = json.loads((root / "frozen" / "indices.json").read_text())
    for split, count in (("validation", 64), ("test", 128)):
        with np.load(output / (split + "-results.npz"), allow_pickle=False) as values:
            assert values["ids"].tolist() == indices[split]
            assert values["prediction"].shape == (count, 81, 120)
            assert values["prediction"].dtype == np.float32
            error = (values["prediction"][:, 1:] - values["target"][:, 1:]) ** 2
            assert np.isfinite(error).all()
            assert np.allclose(error.mean(axis=(1, 2)), values["mse"], rtol=2e-6, atol=1e-6)
    assert (output / "REPORT.md").is_file()
    assert (output / "training-curve.png").stat().st_size > 1000
    assert (output / "test-fields.png").stat().st_size > 1000
