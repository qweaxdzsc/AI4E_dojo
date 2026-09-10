"""三阶段独立入口、持久化交接及准备后数据冲突的整链验收。"""

import json
from pathlib import Path

import torch

from tests.integration.test_train_recipe import _fit_config, _run_script, prepared_case


def test_preparation_artifact_and_independent_train(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    cfg.train.device = "cpu"
    result, directory, summary = _run_script(folder, cfg, entry="trainprep.py")
    assert result.returncode == 0, result.stderr
    reference = summary["reports"]["trainprep"]["preparation"]
    record = json.loads(Path(reference).read_text())
    assert record["version"] == 2
    assert record["split_counts"] == {"test": 1, "train": 1}
    assert not (directory / "checkpoints").exists()
    cfg.train.preparation = reference
    result, trained, summary = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    assert Path(summary["reports"]["train"]["checkpoints"]["last"]).is_file()
    assert (trained / "artifacts/training.json").exists()
    assert sorted(p.name for p in (trained / "inputs").iterdir()) == ["config.yaml"]
    cfg.sampling.seed += 1
    result, _, summary = _run_script(folder, cfg)
    assert result.returncode == 1 and summary["failed"]


def test_preparation_rejects_changed_tensor(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    cfg.train.device = "cpu"
    result, _, summary = _run_script(folder, cfg, entry="trainprep.py")
    assert result.returncode == 0, result.stderr
    cfg.train.preparation = summary["reports"]["trainprep"]["preparation"]
    path = Path(cfg.paths.datasets.train) / "a/surface_pressure.pt"
    value = torch.load(path, weights_only=True)
    torch.save(value + 1, path)
    result, _, summary = _run_script(folder, cfg)
    assert result.returncode == 1
    assert summary["failed"]
    assert "数据已变化" in result.stderr


def test_three_stage_pipeline_and_dry_run(tmp_path):
    from tests.integration.test_dataset_recipe import setup_case

    folder, cfg = setup_case(tmp_path)
    _fit_config(cfg)
    cfg.train.device = "cpu"
    cfg.statistics.mode = "reference"
    cfg.sampling.supernodes.num_points = 2
    cfg.sampling.domains.surface.anchor.num_points = 2
    cfg.sampling.domains.volume.anchor.num_points = 1
    cfg.pipeline.stages = ["datapre", "trainprep", "train"]
    result, _checked, summary = _run_script(folder, cfg, entry="pipeline.py", extra=("--dry-run",))
    assert result.returncode == 0, result.stderr
    assert summary["reports"]["pipeline"]["deferred"] == ["trainprep", "train"]
    assert not Path(cfg.data_root).exists()
    result, directory, summary = _run_script(folder, cfg, entry="pipeline.py")
    assert result.returncode == 0, result.stderr
    assert {"trainprep", "train"} <= summary["reports"].keys()
    assert (directory / "artifacts/preparation.json").is_file()
    from omegaconf import OmegaConf

    effective = OmegaConf.load(directory / "inputs/config.yaml")
    assert "definition" not in effective.dataset
    assert summary["reports"]["dataset"]["definition"]
    preparation = json.loads((directory / "artifacts/preparation.json").read_text())
    assert Path(preparation["manifest"]).is_file()
    assert (directory / "checkpoints/last.pt").is_file()
    log = (directory / "logs/run.log").read_text()
    for stage in effective.pipeline.stages:
        assert f"[{stage}/阶段/开始]" in log


def test_cosine_resume_rejects_changed_training_horizon(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    cfg.train.scheduler = "warmup_cosine"
    cfg.train.max_epochs = 1
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.train.resume = str(directory / "checkpoints/latest.pt")
    cfg.train.max_epochs = 2
    result, _, _ = _run_script(folder, cfg)
    assert result.returncode != 0
    assert "语义冲突" in result.stderr
