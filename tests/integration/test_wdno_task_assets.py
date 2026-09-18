"""真实小模型的资产复制、复制品消费、CLI与公开中断恢复。"""

import json
import os
from pathlib import Path

import pytest

from tests.integration.test_wdno_recipe import fixture
from tools.verification.wdno.task_management import exercise_management
from tools.verification.wdno.task_replay import staged_exercise


def test_copied_assets_and_public_recovery(tmp_path):
    cfg = fixture(tmp_path / "source", source="examples/wdno/burgers_base")
    staged = tmp_path / "staged"
    staged_exercise(staged, cfg, case="example")
    result = exercise_management(staged)
    assert result["passed"] and result["original_locations_hidden"]
    assert result["copy_states_equal"] and result["copy_tamper_rejected"]
    assert [x["mode"] for x in result["recovery"]] == ["python", "cli"]


def test_current_original_data_protocol_delivery():
    value = os.environ.get("DOJO_WDNO_PROTOCOL_ROOT")
    if not value:
        pytest.skip("需要当前四包安装后的三个原数据入口实跑目录")
    root = Path(value)
    ids = set()
    for case in ("recipe", "example", "extension"):
        result = json.loads((root / case / "staged/acceptance.json").read_text())
        assert result["passed"] and result["real_original_data"] and result["case"] == case
        assert result["training_states_equal"] and result["prediction_max_abs"] == 0
        assert result["post_without_model"] and result["prediction_unchanged_by_post"]
        assert len(result["runs"]) == 6 and all(r["status"] == "succeeded" for r in result["runs"])
        ids.add(result["task_id"])
    assert len(ids) == 3
    management = json.loads((root / "example/staged/management.json").read_text())
    assert management["passed"] and management["copy_states_equal"]
    assert management["original_locations_hidden"] and management["copy_tamper_rejected"]
    assert all(x["states_equal"] for x in management["recovery"])
    runtime = json.loads((root / "runtime.json").read_text())
    assert all(str(root / "installed") in p for p in runtime["modules"].values())
