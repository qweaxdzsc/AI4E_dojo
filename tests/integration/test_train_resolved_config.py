"""第 32 项：默认展开、联合校验与最终生效配置。"""

from pathlib import Path

import yaml
from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved, validate_joint
from ai4e_core.run.session import run_recipe
from tests.integration.test_train_recipe import prepared_case


def test_partial_config_expands_defaults_and_writes_resolved(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    cfg.train.mode = "probe"
    del cfg.model.parameters.dim
    del cfg.train.learning_rate
    OmegaConf.save(cfg, folder / "config.yaml")
    before = set(Path(cfg.run_root).iterdir()) if Path(cfg.run_root).exists() else set()
    assert (
        run_recipe(
            cfg,
            stages={"train": lambda _: None},
            script=folder / "train.py",
            only=["train"],
            source_config=folder / "config.yaml",
            resolver=apply_resolved,
            flags={"dry_run": False, "overwrite": False, "continue_on_error": False},
        )
        == 0
    )
    run_dir = (set(Path(cfg.run_root).iterdir()) - before).pop()
    resolved = yaml.safe_load((run_dir / "inputs" / "config.yaml").read_text())
    assert resolved["model"]["parameters"]["dim"] == 192
    assert resolved["model"]["parameters"]["blocks"] == "pscscscscsc"
    assert resolved["train"]["optimizer"] == "lion"
    assert resolved["train"]["scheduler"] == "warmup_cosine"
    assert resolved["train"]["warmup_ratio"] == 0.05
    assert resolved["train"]["min_lr"] == 1.0e-6
    assert not (run_dir / "inputs" / "source.yaml").exists()


def test_joint_validation_rejects_batch_and_sampling_conflict():
    config = apply_resolved(
        {
            "fields": {
                "surface": {"pressure": {"components": 1}},
                "volume": {"velocity": {"components": 3}},
            },
            "sampling": {"geometry": {"max_points": 10}, "supernodes": {"num_points": 20}},
            "train": {"batch_size": 0, "snapshot": False},
            "model": {"parameters": {}},
        },
        validate=False,
    )
    try:
        validate_joint(config)
    except ValueError as exc:
        assert "批次" in str(exc)
    else:
        raise AssertionError("应拒绝非正批次")
    config["train"]["batch_size"] = 1
    try:
        validate_joint(config)
    except ValueError as exc:
        assert "超节点" in str(exc)
    else:
        raise AssertionError("应拒绝采样预算冲突")
