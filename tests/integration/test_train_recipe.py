"""复制案例通过唯一会话执行准备与归一化物化。"""

import importlib.util
import json
from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core import run
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization
from tests.integration.test_dataset_recipe import execute_case, public_config, setup_case


def prepared_case(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg.statistics.mode = "reference"
    assert execute_case(folder, cfg) == 0
    cfg.normalization.execute = True
    cfg.normalization.materialize = False
    cfg.train.mode = "prepare"
    cfg.sampling.supernodes.num_points = 2
    cfg.sampling.domains.surface.anchor.num_points = 2
    cfg.sampling.domains.volume.anchor.num_points = 1
    cfg.train.snapshot = False
    cfg.train.test_repeat = 1
    cfg.train.device = "auto"
    return folder, cfg


def test_prepare_uses_one_session_and_dry_run(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    spec = importlib.util.spec_from_file_location("copied_train", folder / "train.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    before = set(Path(cfg.run_root).iterdir())
    assert (
        run.run_recipe(
            public_config(cfg),
            stages={"train": module.train},
            script=folder / "train.py",
            only=["train"],
            flags={"dry_run": True},
        )
        == 0
    )
    new = set(Path(cfg.run_root).iterdir()) - before
    assert len(new) == 1
    summary = json.loads((new.pop() / "summary.json").read_text())
    assert summary["reports"]["train"]["mode"] == "prepare"
    assert not Path(cfg.paths.datasets.normalize.root).exists()


def test_materialized_roundtrip_and_frozen_record(tmp_path):
    _, cfg = prepared_case(tmp_path)
    cfg.normalization.materialize = True
    config = OmegaConf.to_container(cfg, resolve=True)
    result = probe(config, prepare=prepare_inputs)
    manifest = ManifestIndex(result["normalized_manifest"])
    fields = manifest.read("test")
    for name, value in result["normalized"].items():
        torch.testing.assert_close(fields[name], value)
    normalization = Normalization(manifest.manifest["normalization"])
    torch.testing.assert_close(
        normalization.inverse("surface_pressure", fields["surface_pressure"]),
        result["physical"]["surface_pressure"],
    )
    config["train"]["manifest"] = result["normalized_manifest"]
    config["normalization"]["execute"] = False
    config["normalization"]["materialize"] = False
    loaded = probe(config, prepare=prepare_inputs)
    torch.testing.assert_close(loaded["normalized"]["surface_pressure"], fields["surface_pressure"])
    manifest.manifest["normalization"]["fields"]["surface_pressure"]["parameters"]["mean"] = [999]
    Path(result["normalized_manifest"]).write_text(json.dumps(manifest.manifest))
    with pytest.raises(ValueError, match="摘要"):
        probe(config, prepare=prepare_inputs)


def test_materialization_failure_does_not_publish(tmp_path, monkeypatch):
    _, cfg = prepared_case(tmp_path)
    cfg.normalization.materialize = True
    original = torch.save
    calls = []

    def fail(value, path):
        calls.append(path)
        if len(calls) == 9:
            raise OSError("injected partial materialization")
        return original(value, path)

    monkeypatch.setattr(torch, "save", fail)
    with pytest.raises(OSError):
        probe(OmegaConf.to_container(cfg, resolve=True), prepare=prepare_inputs)
    root = Path(cfg.paths.datasets.normalize.root)
    assert not list(root.rglob("manifest.json"))
    assert not list(root.rglob("*.pt"))


def _fit_config(cfg):
    """正式 AB-UPT 的合法小配置，保留网络组成而降低验收成本。"""
    cfg.train.mode = "fit"
    cfg.model.parameters.update(
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    cfg.train.max_epochs = 2
    cfg.train.device = "auto"
    cfg.train.optimizer = "adamw"
    cfg.train.scheduler = "constant"
    cfg.train.test_repeat = 1
    cfg.train.snapshot = False
    return cfg


def _run_script(folder, cfg, *, entry="train.py", extra=()):
    """运行复制脚本并读取本次唯一新运行的摘要。"""
    import os
    import subprocess
    import sys

    OmegaConf.save(public_config(cfg), folder / "config.yaml")
    root = Path(cfg.run_root)
    before = set(root.iterdir()) if root.exists() else set()
    result = subprocess.run(
        [sys.executable, str(folder / entry), *extra],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
        env={**os.environ, "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
    )
    after = set(root.iterdir()) - before
    assert len(after) == 1, result.stderr
    directory = after.pop()
    return result, directory, json.loads((directory / "summary.json").read_text())


def test_real_recipe_fit_and_epoch_resume(tmp_path):
    """I2/I4/G4：直接脚本与 pipeline 训练和恢复使用正式贡献网络。"""
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    result, full_dir, summary = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    assert not summary["failed"]
    full = torch.load(full_dir / "checkpoints/last.pt", weights_only=False)
    assert full["epoch"] == 2 and full["updates"] == 2
    assert {p.name for p in (full_dir / "checkpoints").iterdir()} == {
        "best.pt",
        "latest.pt",
        "last.pt",
    }
    assert len(summary["reports"]["train"]["history"]) == 2
    assert len(summary["reports"]["train"]["history"][0]["evaluation"]["metrics"]) == 6
    assert full["contract"]["factory"].startswith("ai4e_contrib.")
    assert full["contract"]["normalization"]["version"] == 2
    cfg.train.max_epochs = 1
    result, one_dir, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.train.resume = str(one_dir / "checkpoints/latest.pt")
    cfg.train.max_epochs = 2
    cfg.pipeline.stages = ["train"]
    result, resumed_dir, resumed_summary = _run_script(folder, cfg, entry="pipeline.py")
    assert result.returncode == 0, result.stderr
    resumed = torch.load(resumed_dir / "checkpoints/last.pt", weights_only=False)
    for name, value in full["model"].items():
        torch.testing.assert_close(value, resumed["model"][name], rtol=1e-5, atol=1e-6)
    assert resumed["updates"] == full["updates"]
    assert resumed_summary["reports"]["train"]["history"][0]["epoch"] == 2
    assert full["ema"] is not None and resumed["ema"] is not None
    for name, value in full["ema"].items():
        torch.testing.assert_close(value, resumed["ema"][name], rtol=1e-5, atol=1e-6)
    assert full["effective_config"]["train"]["max_epochs"] == 2


def test_script_probe_and_fit_check_have_no_training_artifacts(tmp_path):
    """I3：probe 不需要变换，fit 检查没有检查点或数据写入。"""
    folder, cfg = prepared_case(tmp_path)
    cfg.train.mode = "probe"
    cfg.normalization = {"execute": False, "fields": {}}
    result, directory, summary = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    assert summary["reports"]["train"]["mode"] == "probe"
    assert not list(directory.rglob("*.pt"))
    # 从原模板恢复准备声明，然后通过正式 fit 的检查入口预检。
    import yaml

    from tests.integration.test_dataset_recipe import RECIPE

    cfg.normalization = yaml.safe_load((RECIPE / "config.yaml").read_text())["trainprep"][
        "normalization"
    ]
    cfg.normalization.execute = True
    cfg.normalization.materialize = True
    _fit_config(cfg)
    result, directory, summary = _run_script(folder, cfg, extra=("--dry-run",))
    assert result.returncode == 0, result.stderr
    assert summary["dry_run"]
    assert not list(directory.rglob("*.pt"))
    assert not Path(cfg.paths.datasets.normalize.root).exists()


def test_legacy_coordinate_method_still_prepares(tmp_path):
    """旧 method: coordinate 仍按共享边界变换消费，不被新页面拆列破坏。"""
    _, cfg = prepared_case(tmp_path)
    fields = OmegaConf.to_container(cfg.normalization.fields, resolve=True)
    assert fields["surface_position"]["method"] == "coordinate"
    cfg.normalization.materialize = True
    config = OmegaConf.to_container(cfg, resolve=True)
    result = probe(config, prepare=prepare_inputs)
    assert "surface_position" in result["normalized"]


def test_real_recipe_read_failure_is_run_failure(tmp_path):
    """F4：样本读取失败传播到会话，不写成功结束检查点。"""
    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    (Path(cfg.paths.datasets.train) / "a/surface_pressure.pt").unlink()
    result, directory, summary = _run_script(folder, cfg)
    assert result.returncode == 1
    assert summary["failed"]
    assert not (directory / "checkpoints/last.pt").exists()
    assert "surface_pressure" in (directory / "logs/errors.log").read_text()
