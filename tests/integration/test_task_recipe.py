"""真实小网格、正式 AB-UPT 经 task new/fork 执行含独立infer的五阶段闭环。"""

from pathlib import Path

import ai4e_task as task
from omegaconf import OmegaConf

from tests.integration.test_dataset_recipe import public_config, setup_case
from tests.integration.test_train_recipe import _fit_config


def test_formal_recipe_new_fork_train_post(tmp_path):
    source, cfg = setup_case(tmp_path)
    _fit_config(cfg)
    cfg.statistics.mode = "reference"
    cfg.normalization.execute = True
    cfg.train.device = "cpu"
    cfg.train.max_epochs = 1
    cfg.train.test_repeat = 1
    cfg.sampling.supernodes.num_points = 2
    cfg.sampling.domains.surface.anchor.num_points = 2
    cfg.sampling.domains.volume.anchor.num_points = 1
    cfg.pipeline.stages = ["datapre", "trainprep", "train", "infer", "post"]
    cfg.post.sample_indices = [0]
    cfg.infer = {"samples": ["b"], "split": "test", "device": "cpu"}
    OmegaConf.save(public_config(cfg), source / "config.yaml")
    project = tmp_path / "study"
    task.create_project(project)
    first = task.new_task(project, "baseline", source=source)
    a = task.submit_run(project, first["id"])
    a = task.wait_run(project, a["id"], timeout=90)
    assert a["status"] == "succeeded", a
    assert (Path(a["run_dir"]) / "checkpoints/last.pt").is_file()
    assert "post" in a["summary"]["reports"]
    assert "infer" in a["summary"]["reports"]
    child = task.fork_task(
        project, first["id"], copy_datasets=True, copy_preparation=True, copy_checkpoints=True
    )
    assert {a["kind"] for a in child["copied_outputs"].values()} == {"preparation", "checkpoint"}
    assert all(asset["source"]["run_id"] == a["id"] for asset in child["copied_outputs"].values())
    b = task.submit_run(project, child["id"], overrides=["train.learning_rate=0.0002"])
    b = task.wait_run(project, b["id"], timeout=90)
    assert b["status"] == "succeeded", b
    assert Path(a["data_dir"]) != Path(b["data_dir"])
    assert len(task.get_lineage(project)) == 2
    assert len(task.list_runs(project)) == 2
    comparison = task.compare_runs(project, a["id"], b["id"], save=True)
    assert comparison["metrics"]
    assert all(x["status"] == "available" for x in comparison["metrics"].values()), comparison
    shared = task.share_run_asset(
        project,
        b["id"],
        "trained-weights",
        Path(b["run_dir"]) / "checkpoints/last.pt",
        kind="checkpoint",
    )
    assert shared["source"]["version_id"] == child["version_id"]
