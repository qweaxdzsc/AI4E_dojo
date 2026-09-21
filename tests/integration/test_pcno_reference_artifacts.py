"""显式选择本机真实参考产物，区分已完成准入与尚未完成的长训练。"""

import json
import os
from pathlib import Path

import pytest

from tools.verification.pcno.reference import digest


@pytest.fixture
def reference():
    selected = os.environ.get("DOJO_PCNO_REFERENCE_ROOT")
    if not selected:
        pytest.skip("Set DOJO_PCNO_REFERENCE_ROOT to verify real PCNO artifacts")
    return Path(selected)


def test_real_data_identity(reference):
    report = json.loads((reference / "data-audit.json").read_text())
    assert len(report["training"]) == report["distinct_training_inputs"] == 24
    assert len(report["demonstration"]) == report["distinct_demo_inputs"] == 18
    assert report["overlapping_inputs"] == []
    assert report["demo_fields_equal_author_prediction"] == {"pres": True, "temp": True}
    assert report["demo_independent_truth"] is False
    for branch in ["pres", "temp"]:
        identity = json.loads((reference / f"{branch}-250/identity.json").read_text())
        for name, checksum in report["sha256"].items():
            assert identity["data"][name] == checksum
        assert identity["branch"] == branch
        assert identity["epochs"] == 250 and identity["modes"] == [1] * 4 and identity["width"] == 8


def test_real_economic_replay(reference):
    directory = reference / "economy"
    report = json.loads((directory / "comparison.json").read_text())
    assert report["byte_equal"] is True
    assert (
        digest(directory / "Tech_Eco_Result_75_0.85.csv")
        == report["expected_sha256"]
        == report["actual_sha256"]
    )


def test_real_full_resolution_first_steps(reference):
    for branch in ["pres", "temp"]:
        report = json.loads((reference / f"{branch}-first-step-parity.json").read_text())
        assert report["passed"] is True
        assert report["checks"] == {"prediction": True, "gradients": True, "state": True}
        assert report["rtol"] == 1e-5 and report["atol"] == 1e-6
        root = reference / f"{branch}-250"
        for name in [
            "initial.pt",
            "first-gradient.pt",
            "first-update.pt",
            "first-prediction.pt",
            "observer-source.py",
            "adapted-trainer.py",
        ]:
            assert (root / name).stat().st_size > 0
        first = json.loads((root / "updates.jsonl").read_text().splitlines()[0])
        assert first["sample"] == "chunk_06/0"
        assert first["update"] == 1 and first["epoch"] == 1
