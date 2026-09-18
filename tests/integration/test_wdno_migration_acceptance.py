"""真实两侧2000更新及完整评价验收；缺少产物不能称已通过。"""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from tools.verification.wdno.protocol import digest


@pytest.fixture
def root():
    location = os.environ.get("DOJO_WDNO_MIGRATION_ROOT")
    if not location:
        pytest.skip("需要明确指定本次真实迁移产物")
    return Path(location)


def test_full_paired_training_and_all_predictions(root):
    comparison = json.loads((root / "dojo-final/comparison.json").read_text())
    assert comparison["passed"] and comparison["updates"] == 2000
    assert (
        comparison["parameters_max_abs"]
        == comparison["ema_max_abs"]
        == comparison["loss_max_abs"]
        == 0
    )
    assert comparison["paper_reproduced"] is False
    assert comparison["optimizer_equal"]
    prep = json.loads((root / "dojo-final/preparation-comparison.json").read_text())
    assert prep == {"samples": 18000, "max_abs": 0.0}
    reference = json.loads((root / "reference-current-2/result.json").read_text())
    assert reference["original_trainer"] and reference["status"] == "slice_complete"
    assert reference["torch"] == comparison["torch"]
    for split, count in [("validation", 64), ("test", 128)]:
        stats = comparison["evaluation"][split]
        assert stats["samples"] == count and stats["prediction_max_abs"] == 0
        assert stats["target_max_abs"] == 0
        assert np.isclose(stats["mse"], stats["reference_mse"], rtol=2e-6, atol=1e-7)
    assert comparison["source_checkpoint_sha256"] == digest(
        root / "reference-current-2/checkpoints/latest.pt"
    )


def test_cumulative_budget_and_installed_delivery(root):
    ledger = json.loads((root / "budget.json").read_text())
    assert ledger["seconds"] < 10800
    assert all(entry["status"] != "running" for entry in ledger["runs"])
    delivery = json.loads((root / "dojo-final/delivery.json").read_text())
    assert delivery["dojo_migrated"] and not delivery["paper_reproduced"]
    for item in delivery["installed_modules"].values():
        assert "installed-final" in item["path"]
        assert digest(item["path"]) == item["sha256"]
    for filename, expected in delivery["wheels"].items():
        assert digest(filename) == expected


def test_real_data_variants_and_original_weight_import(root):
    variant = json.loads((root / "variant/acceptance.json").read_text())
    assert variant["passed"] and variant["real_original_data"] and variant["updates"] == 2
    assert Path(variant["configuration"]) == root / "variant/config.yaml"
    assert Path(variant["configuration"]).is_file()
    import yaml

    cfg = yaml.safe_load(Path(variant["configuration"]).read_text())
    baseline = yaml.safe_load((root / "dojo-final/config.yaml").read_text())
    assert cfg["data"]["prepared"] == baseline["data"]["prepared"]
    for split, count in [("validation", 64), ("test", 128)]:
        assert variant["evaluation"][split]["samples"] == count
        assert variant["evaluation"][split]["energy_readback"]
    replay = json.loads((root / "source-import/replay.json").read_text())
    for split in ("validation", "test"):
        assert replay[split] == {"samples": 16, "max_abs": 0.0, "passed": True}
