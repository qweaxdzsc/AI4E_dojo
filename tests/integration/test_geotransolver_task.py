"""公开 Task 真实案例验收产物门禁；没有实跑记录不能计作通过。"""

import json
import os
from pathlib import Path

import pytest


@pytest.mark.parametrize("case", ["darcy", "bumper_beam", "darcy-extension"])
def test_installed_real_task_replay(case):
    configured = os.environ.get("DOJO_GEOTRANSOLVER_ACCEPTANCE_ROOT")
    if configured is None:
        pytest.skip("显式真实验收需 DOJO_GEOTRANSOLVER_ACCEPTANCE_ROOT；不代表已通过")
    path = Path(configured) / case / "acceptance.json"
    assert path.is_file(), f"缺少真实Task证据 {path}"
    record = json.loads(path.read_text())
    assert record["same_weights_prediction"] and record["resume_updates"] == 3
    assert record["uninterrupted_equal"]
    assert record["task_run"]["status"] == "succeeded"
    assert record["post"]["samples"] == (7 if case == "bumper_beam" else 200)
    assert "/installed/venv/" in record["runtime"]["core"]


def test_real_extension_changes_predictions():
    configured = os.environ.get("DOJO_GEOTRANSOLVER_ACCEPTANCE_ROOT")
    if configured is None:
        pytest.skip("真实扩展需显式验收目录")
    record = json.loads((Path(configured) / "extension-comparison.json").read_text())
    assert record["changed"] and record["prediction_max_difference"] > 0


@pytest.mark.parametrize("case", ["darcy", "bumper_beam"])
def test_real_task_asset_copy_without_sources(case):
    configured = os.environ.get("DOJO_GEOTRANSOLVER_ACCEPTANCE_ROOT")
    if configured is None:
        pytest.skip("真实资产复制需显式验收目录")
    record = json.loads((Path(configured) / case / "asset-acceptance.json").read_text())
    assert record["preparation_copied"] and record["checkpoint_copied"]
    assert record["source_isolated"] and record["prediction_max_difference"] == 0
