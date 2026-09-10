"""整链入口：选定模型、设备映射与唯一运行目录。"""

from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.train.resolve import TRAIN_DEFAULTS
from ai4e_core.run.session import run_recipe
from tests.integration.test_dataset_recipe import RECIPE
from tests.integration.test_train_recipe import prepared_case


def test_gpu_maps_to_cuda_and_fails_when_unavailable(monkeypatch):
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(ValueError, match="CUDA"):
        resolve_device("gpu")
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    assert resolve_device("gpu").type == "cuda"


def test_recipe_train_creates_single_run_and_selects_abupt(tmp_path):
    assert TRAIN_DEFAULTS["device"] == "auto"
    assert yaml.safe_load((RECIPE / "config.yaml").read_text())["train"]["device"] == "auto"
    folder, cfg = prepared_case(tmp_path)
    cfg.train.device = "auto"
    cfg.train.mode = "probe"
    OmegaConf.save(cfg, folder / "config.yaml")
    before = set(Path(cfg.run_root).iterdir()) if Path(cfg.run_root).exists() else set()
    assert (
        run_recipe(
            cfg,
            stages={"train": lambda _: None},
            script=folder / "train.py",
            only=["train"],
            flags={"dry_run": False, "overwrite": False, "continue_on_error": False},
        )
        == 0
    )
    created = set(Path(cfg.run_root).iterdir()) - before
    assert len(created) == 1
    resolved = OmegaConf.load(created.pop() / "inputs" / "config.yaml")
    assert resolved.model.parameters.num_heads == 3
    assert resolved.train.device == "auto"
