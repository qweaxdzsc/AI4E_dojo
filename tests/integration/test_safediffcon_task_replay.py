"""Task 独立进程的真实小网络闭环；人工小数组只验交接，不验精度。"""

from pathlib import Path

import ai4e_task as task
import numpy as np
import pytest
from omegaconf import OmegaConf

from ai4e_core.applications.pde_control.contracts import save_arrays
from tools.verification.safediffcon.task_replay import exercise


@pytest.mark.parametrize("extension", [False, True])
def test_task_real_training_inference_and_fixed_post(tmp_path, extension):
    """实际训练/恢复/响应/post，并核对失败状态和组合执行不增加版本。"""
    recipe = Path(__file__).resolve().parents[2] / "recipes/safediffcon"
    if extension:
        recipe = tmp_path / "copied-example"
        task.copy_example("recipe_extensions.task_labels", recipe)
    cfg = OmegaConf.to_container(OmegaConf.load(recipe / "config.yaml"), resolve=True)
    physical = {}
    for split in ("train", "cal", "test"):
        physical[split] = save_arrays(
            tmp_path / "physical" / split,
            {
                "states": np.zeros((2, 11, 128), dtype=np.float32),
                "controls": np.zeros((2, 10, 128), dtype=np.float32),
            },
            kind="control_physical_v1",
            metadata={"case": "burgers", "split": split, "count": 2},
        )
    cfg["inputs"]["trainprep"] = {"dataset_" + s: path for s, path in physical.items()}
    cfg["model"].update(dim=8, ddim_steps=2)
    cfg["train"].update(updates=1, batch_size=2, device="cpu")
    cfg["posttrain"].update(updates_per_round=1, subset_size=2, batch_size=2, calibration_samples=2)
    cfg["infer"].update(device="cpu", adaptation_updates=1, test_samples=2, batch_size=2)
    cfg["solver"].update(python=None)
    cfg["inputs"]["infer"]["solver_assets"] = None
    cfg["pipeline"] = {"stages": ["trainprep"]}
    result = exercise(tmp_path / "project", recipe, cfg)
    assert len(result["runs"]) == 8
    assert [r["status"] for r in result["runs"]].count("succeeded") == 7
    assert result["runs"][-2]["status"] == "failed"
    candidates = task.list_stage_artifacts(tmp_path / "project", result["task_id"])
    calibration = [
        row for row in candidates if row["binding"] == "inputs.posttrain.preparation_cal"
    ]
    assert calibration and all(row["semantics"]["split"] == "cal" for row in calibration)
    assert all(row["name"] == "cal" and row["file_name"] == "manifest.json" for row in calibration)
    requirement = task.describe_recipe(recipe)["description"]["inputs"][
        "inputs.posttrain.preparation_cal"
    ]
    assert all(
        task.match_asset(row, requirement, status="succeeded")["matches"] for row in calibration
    )
    weights = [row for row in candidates if row["binding"] == "inputs.infer.checkpoint"]
    assert len(weights) >= 2 and all(row["semantics"]["phase"] == "posttrain_1" for row in weights)
    captured = task.get_run(tmp_path / "project", result["runs"][3]["id"])
    assert (
        captured["lineage"]["assets"]["inputs.posttrain.preparation_cal"]["semantics"]["split"]
        == "cal"
    )
