"""后处理锚点评估、检查点只恢复权重、预测保存与可选点云。"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_core.abilities.inference.rebuild import rebuild
from ai4e_core.abilities.postproc.export.pointcloud import write_pointcloud
from tests.integration.test_dataset_recipe import public_config
from tests.integration.test_train_recipe import _fit_config, prepared_case


def _run_script(folder, cfg, *, entry="train.py", extra=(), timeout=180):
    """运行复制脚本并读取本次唯一新运行的摘要。"""
    OmegaConf.save(public_config(cfg), folder / "config.yaml")
    root = Path(cfg.run_root)
    before = set(root.iterdir()) if root.exists() else set()
    result = subprocess.run(
        [sys.executable, str(folder / entry), *extra],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env={**os.environ, "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
    )
    after = set(root.iterdir()) - before
    assert len(after) == 1, result.stderr
    directory = after.pop()
    return result, directory, json.loads((directory / "summary.json").read_text())


def _fit_then_post_config(cfg):
    cfg.post.legacy_predict = True  # 显式选择历史post数值对照入口。
    _fit_config(cfg)
    cfg.train.max_epochs = 1
    cfg.post.query = False
    cfg.post.evaluate = True
    cfg.post.save_predictions = True
    cfg.post.export_vtk = True
    return cfg


def test_rebuild_loads_weights_only(tmp_path):
    model = torch.nn.Linear(2, 2)
    rebuilt = torch.nn.Linear(2, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    contract = {
        "model_version": 2,
        "model": {"name": "dummy"},
        "trainprep": {"domains": {}},
        "normalization": {"version": 1},
    }
    path = tmp_path / "ckpt.pt"
    torch.save(
        {
            "version": 2,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "epoch": 7,
            "updates": 9,
            "contract": contract,
        },
        path,
    )
    loaded = rebuild(path, rebuilt, contract=contract)
    for name, value in model.state_dict().items():
        torch.testing.assert_close(rebuilt.state_dict()[name], value)
    assert "optimizer" not in loaded
    assert loaded["contract"]["model"] == contract["model"]


def test_rebuild_rejects_semantic_conflict(tmp_path):
    model = torch.nn.Linear(1, 1)
    contract = {
        "model_version": 2,
        "model": {"name": "dummy"},
        "trainprep": {},
        "normalization": {"version": 1},
    }
    path = tmp_path / "ckpt.pt"
    torch.save({"version": 2, "model": model.state_dict(), "contract": contract}, path)
    with pytest.raises(ValueError, match="语义冲突"):
        rebuild(
            path,
            torch.nn.Linear(1, 1),
            contract={**contract, "model": {"name": "other"}},
        )


def test_pointcloud_rejects_mismatched_fields(tmp_path):
    with pytest.raises(ValueError, match="点数或场形状"):
        write_pointcloud(
            tmp_path / "bad.vtp",
            torch.zeros(3, 3),
            {"pressure": torch.zeros(2, 1)},
        )


def test_anchor_eval_save_and_pointcloud(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    result, _, summary = _run_script(folder, cfg, entry="post.py")
    assert result.returncode == 0, result.stderr
    report = summary["reports"]["post"]
    assert report["mode"] == "post"
    assert report["split"] == "test"
    assert len(report["evaluation"]["metrics"]) == 6
    assert report["evaluation"]["loss"] == pytest.approx(
        sum(report["evaluation"]["losses"].values())
    )
    assert report["predictions"]
    sample = report["predictions"][0]
    dest = Path(sample["output"])
    for name, shape in sample["shapes"].items():
        value = torch.load(dest / f"{name}.pt", weights_only=True)
        assert list(value.shape) == shape and torch.isfinite(value).all()
    import vtk

    for filename, field, count in (
        ("surface.vtp", "surface_pressure", sample["shapes"]["surface_anchor_position"][0]),
        ("volume.vtp", "volume_velocity", sample["shapes"]["volume_anchor_position"][0]),
    ):
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(str(dest / filename))
        reader.Update()
        mesh = reader.GetOutput()
        assert mesh.GetNumberOfPoints() == count
        assert mesh.GetNumberOfVerts() == count
        assert mesh.GetNumberOfPolys() == 0
        assert mesh.GetPointData().GetArray(field) is not None


def test_missing_checkpoint_uses_current_run_last(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    cfg.pipeline.stages = ["train", "post"]
    cfg.post.checkpoint = None
    result, directory, summary = _run_script(folder, cfg, entry="pipeline.py")
    assert result.returncode == 0, result.stderr
    report = summary["reports"]["post"]
    assert Path(report["checkpoint"]) == directory / "checkpoints/last.pt"
    assert report["predictions"]


def test_semantic_conflict_writes_no_predictions(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    cfg.model.parameters.dim = int(cfg.model.parameters.dim) + 24
    before = (
        list(Path(cfg.paths.datasets.predictions).rglob("*.pt"))
        if Path(cfg.paths.datasets.predictions).exists()
        else []
    )
    result, _, summary = _run_script(folder, cfg, entry="post.py")
    assert result.returncode == 1
    assert summary["failed"]
    after = (
        list(Path(cfg.paths.datasets.predictions).rglob("*.pt"))
        if Path(cfg.paths.datasets.predictions).exists()
        else []
    )
    assert after == before


def test_dry_run_does_not_write_predictions(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    result, _, summary = _run_script(folder, cfg, entry="post.py", extra=("--dry-run",))
    assert result.returncode == 0, result.stderr
    assert summary["reports"]["post"]["mode"] == "post_check"
    assert not Path(cfg.paths.datasets.predictions).exists()


def test_export_vtk_can_be_disabled(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    cfg.post.export_vtk = False
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    result, _, summary = _run_script(folder, cfg, entry="post.py")
    assert result.returncode == 0, result.stderr
    dest = Path(summary["reports"]["post"]["predictions"][0]["output"])
    assert (dest / "surface_pressure.pt").is_file()
    assert not (dest / "surface.vtp").exists()
    assert not (dest / "volume.vtp").exists()


def test_post_metrics_match_shared_evaluate(tmp_path):
    from ai4e_contrib.ability.model.abupt.batch import collate
    from ai4e_contrib.ability.model.abupt.model import construct, predict
    from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
    from ai4e_core import run as core_run
    from ai4e_core.applications.aero_cfd.model.objectives import objectives
    from ai4e_core.applications.aero_cfd.post.evaluation import evaluate_model
    from ai4e_core.applications.aero_cfd.post.stage import restore_model
    from ai4e_core.applications.aero_cfd.trainprep.dataset import iter_partition_batches
    from ai4e_core.run.training import TrainingRun

    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    result, _, summary = _run_script(folder, cfg, entry="post.py")
    assert result.returncode == 0, result.stderr
    posted = summary["reports"]["post"]["evaluation"]

    from ai4e_core.abilities.inference.randomness import seeded_randomness

    @seeded_randomness(int(cfg.sampling.seed))
    def compare(inner_cfg):
        config = OmegaConf.to_container(inner_cfg, resolve=True)
        from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved

        config = apply_resolved(config, validate=False)
        run = TrainingRun()
        restored = restore_model(config, run, construct=construct)
        batches = iter_partition_batches(
            restored["index"],
            "test",
            prepare=prepare_inputs,
            collate=collate,
            normalization=restored["normalization"],
            physical_prepare=restored["physical_prepare"],
            normalized_input=restored["normalized_input"],
            sampling=config["sampling"],
            config=config,
            batch_size=int(config["train"]["batch_size"]),
            device=restored["device"],
            evaluation=True,
        )
        shared = evaluate_model(
            restored["model"],
            batches,
            predict=predict,
            objectives=objectives(config.get("model", {})),
            normalization=restored["normalization"],
        )
        assert shared["loss"] == pytest.approx(posted["loss"])
        assert shared["losses"] == pytest.approx(posted["losses"])
        assert shared["metrics"] == posted["metrics"]

    assert (
        core_run.run_recipe(
            cfg,
            stages={"post": lambda _: compare(cfg)},
            script=folder / "post.py",
            only=["post"],
            flags={"dry_run": False, "overwrite": False, "continue_on_error": False},
        )
        == 0
    )
