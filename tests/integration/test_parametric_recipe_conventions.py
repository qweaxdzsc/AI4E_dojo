"""复制 PDE 正文的真实生成、训练、预测和仅固定结果后处理。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import ai4e_task as task
import pytest
import yaml

from ai4e_contrib.application.datasets.parametric import component

ROOT = Path(__file__).resolve().parents[2]


def test_copied_pipeline_task_and_independent_post(tmp_path):
    component("neumann_diffusion").generate({
        "output": str(tmp_path / "physical"), "train": 2, "test": 1, "nx": 9, "nt": 7,
    })
    recipe = tmp_path / "recipe"
    shutil.copytree(ROOT / "recipes/parametric_pde", recipe)
    cfg = yaml.safe_load((recipe / "config.yaml").read_text())
    for inputs in cfg["inputs"].values():
        for key in ("dataset", "manifest"):
            if key in inputs:
                inputs[key] = str(tmp_path / "physical/manifest.json")
    cfg["model"] = {"control_points": [5, 5], "degree": 3, "hidden_dim": 8}
    cfg["train"].update(max_epochs=2, device="cpu", precision="fp64", snapshot=False)
    (recipe / "config.yaml").write_text(yaml.safe_dump(cfg))
    project = tmp_path / "project"
    task.create_project(project)
    created = task.new_task(project, "PDE", source=recipe)
    result = task.wait_run(project, task.submit_run(project, created["id"])["id"], timeout=90)
    assert result["status"] == "succeeded", task.read_log(project, result["id"])
    index = json.loads((Path(result["run_dir"]) / "artifacts/assets.json").read_text())
    predictions = Path(index["items"]["infer/results"]["path"])
    cfg["inputs"]["post"]["results"] = str(predictions)
    cfg["pipeline"]["stages"] = ["post"]
    cfg["run_root"], cfg["data_root"] = str(tmp_path / "post_runs"), str(tmp_path / "post_data")
    # 权重被隐藏，独立 post 必须仍真实重算成功。
    checkpoints = Path(result["run_dir"]) / "checkpoints"
    checkpoints.rename(checkpoints.with_name("hidden_checkpoints"))
    (recipe / "config.yaml").write_text(yaml.safe_dump(cfg))
    replay = subprocess.run([sys.executable, str(recipe / "pipeline.py")], cwd=tmp_path,
                            capture_output=True, text=True, timeout=60)
    assert replay.returncode == 0, replay.stdout + replay.stderr
    source = json.loads(predictions.read_text())
    post = json.loads(next((tmp_path / "post_data").glob("*/post/metrics.json")).read_text())
    assert post["mean_relative_l2"] == pytest.approx(source["mean_relative_l2"])
