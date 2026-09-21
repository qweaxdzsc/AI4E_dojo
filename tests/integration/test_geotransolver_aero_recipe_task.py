"""仓库外完整案例、Task、恢复及固定结果消费。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import ai4e_task as task
import pytest
import torch
import yaml

from tests.geotransolver_aero_assets import setup_case
from tests.integration.test_meshgraphnet_aero_task import _assert_state_equal


def execute(case, cfg):
    """运行公开脚本并返回当次目录。"""
    (case / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    root = Path(cfg["run_root"])
    before = set(root.iterdir()) if root.exists() else set()
    result = subprocess.run(
        [sys.executable, str(case / "pipeline.py")],
        cwd=case.parent,
        env={**os.environ, "OMP_NUM_THREADS": "2"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return (set(root.iterdir()) - before).pop()


@pytest.mark.parametrize("dataset", ["shapenet_car", "nasa_crm"])
def test_direct_task_and_independent_post(tmp_path, dataset):
    case, platform, cfg = setup_case(tmp_path / "source", dataset)
    direct = execute(case, cfg)
    prediction = direct / "artifacts/physical-predictions.json"
    saved = json.loads(prediction.read_text())
    for row in saved["results"]:
        metadata = json.loads(Path(row["manifest"]).read_text())
        assert metadata["meshes"]
        assert all(
            Path(row["manifest"]).with_name(m["path"]).is_file()
            for m in metadata["meshes"].values()
        )
    project = tmp_path / "project"
    task.create_project(project)
    item = task.new_task(project, "geo", source=case)
    managed = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=120)
    assert managed["status"] == "succeeded", task.read_log(project, managed["id"])
    a = torch.load(direct / "checkpoints/last.pt", weights_only=False)
    b = torch.load(Path(managed["run_dir"]) / "checkpoints/last.pt", weights_only=False)
    for name in ("model", "optimizer", "scheduler"):
        _assert_state_equal(a[name], b[name])
    # 固定结果仅复制数组和网格，清单重定位后隐藏全部原始运行与物理输入。
    detached = tmp_path / "detached"
    detached.mkdir()
    for i, row in enumerate(saved["results"]):
        source = Path(row["manifest"])
        dest = detached / str(i)
        shutil.copytree(source.parent, dest)
        row["manifest"] = str(dest / source.name)
    fixed = detached / "results.json"
    fixed.write_text(json.dumps(saved))
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["post"]["results"] = str(fixed)
    cfg["run_root"] = str(tmp_path / "post-runs")
    original_data = Path(cfg["data_root"])
    original_data.rename(original_data.with_name("hidden-data"))
    platform.rename(platform.with_name("hidden-platform"))
    direct.rename(direct.with_name("hidden-run"))
    independent = execute(case, cfg)
    assert (independent / "summary.json").is_file()


def test_resume_matches_continuous(tmp_path):
    case, _, cfg = setup_case(tmp_path / "source", "nasa_crm")
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    continuous = execute(case, cfg)
    cfg["train"]["max_epochs"] = 1
    first = execute(case, cfg)
    cfg["train"]["max_epochs"] = 2
    cfg["pipeline"]["stages"] = ["train"]
    cfg["inputs"]["train"].update(
        preparation=str(first / "artifacts/preparation.json"),
        resume=str(first / "checkpoints/last.pt"),
    )
    resumed = execute(case, cfg)
    a = torch.load(continuous / "checkpoints/last.pt", weights_only=False)
    b = torch.load(resumed / "checkpoints/last.pt", weights_only=False)
    for key in ("model", "optimizer", "scheduler", "updates", "epoch"):
        _assert_state_equal(a[key], b[key])


def test_loss_extension_changes_weights_and_consumes_saved_error(tmp_path):
    case, _, cfg = setup_case(tmp_path / "source", "shapenet_car")
    cfg["train"]["max_epochs"] = 1
    base = execute(case, cfg)
    extension = (
        Path(__file__).resolve().parents[2] / "examples/recipe_extensions/geotransolver_aero"
    )
    for name in ("variants.py", "train.py", "infer.py", "post.py"):
        shutil.copyfile(extension / name, case / name)
    cfg["post"].update(figures=["surface"], image_size=[300, 200])
    changed = execute(case, cfg)
    a = torch.load(base / "checkpoints/last.pt", weights_only=False)["model"]
    b = torch.load(changed / "checkpoints/last.pt", weights_only=False)["model"]
    assert any(not torch.equal(a[name], b[name]) for name in a)
    result = json.loads((changed / "artifacts/physical-predictions.json").read_text())
    manifest = Path(result["results"][0]["manifest"])
    fields = json.loads(manifest.read_text())["filemap"]
    assert "surface.absolute_error" in fields
    cfg["inputs"]["post"]["results"] = str(changed / "artifacts/physical-predictions.json")
    cfg["pipeline"]["stages"] = ["post"]
    (changed / "checkpoints").rename(changed / "hidden-checkpoints")
    post = execute(case, cfg)
    assert list((Path(cfg["data_root"]) / post.name).rglob("*.png"))
