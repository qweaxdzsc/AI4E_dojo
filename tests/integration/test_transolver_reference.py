"""E2：独立原入口对照与比较器反例；小数据结果不替代正式规模。"""

import json
import os
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest
import torch
from omegaconf import OmegaConf

from tests.transolver_assets import configuration
from tools.verification.transolver3.compare import compare, require

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT.parent / "Transolver-3"


def test_comparator_rejects_invalid_values():
    """E2：非有限、索引差异、形状和局部超差均拒绝。"""
    for left, right in [
        ([np.nan], [np.nan]),
        ([np.inf], [np.inf]),
        ([1], [2]),
        ([1.0, 0.0], [1.0, 0.01]),
    ]:
        assert not compare(left, right, identity="negative")["passed"]
    assert compare([1.0], [1.0 + 1e-7], identity="finite")["passed"]


def paired(tmp_path):
    """相同源文件与参数，分别运行原始和 Dojo 四阶段，禁止共享模型权重。"""
    if not (REFERENCE / "user_project/train.py").is_file():
        pytest.skip("需要只读原 Transolver-3 仓库")
    cfg, path = configuration(tmp_path)
    plain = OmegaConf.to_container(cfg, resolve=True)
    model = dict(plain["model"]["parameters"])
    checkpointing = model.pop("gradient_checkpointing")
    ref = tmp_path / "reference"
    settings = {
        "data": {
            **{
                k: plain["dataset"][k]
                for k in ("train_h5", "test_h5", "chunk_count", "split_seed", "validation_fraction")
            },
            "processed_dir": str(ref / "processed"),
            "predictions_dir": str(ref / "predictions"),
            "post_dir": str(ref / "post"),
        },
        "model": model,
        "training": {
            "checkpoint_dir": str(ref / "checkpoints"),
            "epochs": 2,
            "device": "cpu",
            "seed": 2,
            "gradient_checkpointing": checkpointing,
        },
    }
    settings_path = tmp_path / "reference.json"
    settings_path.write_text(json.dumps(settings))
    env = {
        **os.environ,
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    commands = [
        [
            sys.executable,
            "-B",
            str(ROOT / "tools/verification/transolver3/dojo.py"),
            "--config",
            str(path),
        ]
    ]
    for stage in ("preprocess", "train", "inference", "post"):
        commands.append(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools/verification/transolver3/reference.py"),
                "--repository",
                str(REFERENCE),
                "--settings",
                str(settings_path),
                "--stage",
                stage,
            ]
        )
    for command in commands:
        result = subprocess.run(
            command, cwd=tmp_path, env=env, capture_output=True, text=True, check=False
        )
        assert result.returncode == 0, result.stdout + result.stderr
    return cfg, ref, next(Path(cfg.run_root).iterdir())


def test_independent_two_epoch_reference(tmp_path):
    """B3/C3/D1/D2：原训练循环独立两轮，并对照所有预测块、数值场和指标。"""
    cfg, ref, run = paired(tmp_path)
    manifest = json.loads((Path(cfg.paths.datasets.root) / "manifest.json").read_text())
    reference_manifest = json.loads((ref / "processed/manifest.json").read_text())
    assert manifest["splits"] == reference_manifest["splits"]
    assert manifest["statistics"] == reference_manifest["statistics"]
    actual = torch.load(run / "checkpoints/latest.pt", weights_only=False)
    expected = torch.load(ref / "checkpoints/latest.pt", weights_only=False)
    assert list(actual["model"]) == list(expected["model_state_dict"])
    for key, tensor in actual["model"].items():
        require(
            tensor.numpy(), expected["model_state_dict"][key].numpy(), identity=f"weights/{key}"
        )
    for left, right in zip(actual["history"], expected["history"], strict=True):
        require(left["loss"], right["train_normalized_mse"], identity="train/loss")
        for key in ("normalized_mse", "physical_mse", "physical_mae"):
            require(left["evaluation"][key], right["validation"][key], identity=f"validation/{key}")
        assert left["learning_rate"] == right["learning_rate"]
    for path in (ref / "predictions/test").glob("*/prediction_part*.npy"):
        require(
            np.load(
                Path(cfg.paths.datasets.predictions)
                / "test"
                / path.relative_to(ref / "predictions/test")
            ),
            np.load(path),
            identity=str(path.relative_to(ref)),
        )
    for path in (ref / "post/test").glob("*.h5"):
        with (
            h5py.File(path) as expected_h5,
            h5py.File(Path(cfg.paths.datasets.post) / "test" / path.name) as actual_h5,
        ):
            assert set(actual_h5) == set(expected_h5)
            for key in expected_h5:
                require(actual_h5[key][...], expected_h5[key][...], identity=f"{path.name}/{key}")
    actual_metrics = json.loads((Path(cfg.paths.datasets.post) / "test/metrics.json").read_text())
    expected_metrics = json.loads((ref / "post/test/metrics.json").read_text())
    for key in ("mse", "mae", "relative_l2", "cf_magnitude"):
        for field in expected_metrics["aggregate"][key]:
            require(
                actual_metrics["aggregate"][key][field],
                expected_metrics["aggregate"][key][field],
                identity=f"metrics/{key}/{field}",
            )


def test_resume_matches_reference_restart(tmp_path):
    """C2/C4：第一轮状态恢复后的独立数据生成器重建及第二轮轨迹配对。"""
    import yaml

    _cfg, ref, run = paired(tmp_path)
    trace = json.loads((ref / "checkpoints/input-trace.json").read_text())
    protocol = json.loads((run / "artifacts/training-protocol.json").read_text())
    assert protocol["initialization"] == trace["initialization"]
    assert protocol["inputs"] == trace["inputs"]
    config = yaml.safe_load((tmp_path / "configuration/config.yaml").read_text())
    config["run_root"] = str(tmp_path / "resume-runs")
    config["pipeline"]["stages"] = ["train"]
    config.setdefault("inputs", {}).setdefault("train", {})["resume"] = str(
        tmp_path / "configuration/dojo-epoch-snapshots" / run.name / "epoch-1.pt"
    )
    config_path = tmp_path / "configuration/resume.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    settings = json.loads((tmp_path / "reference.json").read_text())
    settings["training"]["checkpoint_dir"] = str(ref / "resume-checkpoints")
    settings_path = tmp_path / "reference-resume.json"
    settings_path.write_text(json.dumps(settings))
    commands = [
        [
            sys.executable,
            "-B",
            str(ROOT / "tools/verification/transolver3/dojo.py"),
            "--config",
            str(config_path),
        ],
        [
            sys.executable,
            "-B",
            str(ROOT / "tools/verification/transolver3/reference.py"),
            "--repository",
            str(REFERENCE),
            "--settings",
            str(settings_path),
            "--stage",
            "train",
            "--resume",
            str(ref / "checkpoints/epoch-1.pt"),
        ],
    ]
    for command in commands:
        result = subprocess.run(
            command,
            cwd=tmp_path,
            env={**os.environ, "OMP_NUM_THREADS": "1"},
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    resumed = next((tmp_path / "resume-runs").iterdir())
    actual = torch.load(resumed / "checkpoints/latest.pt", weights_only=False)
    expected = torch.load(ref / "resume-checkpoints/latest.pt", weights_only=False)
    assert len(actual["history"]) == 2
    for key, value in actual["model"].items():
        require(value.numpy(), expected["model_state_dict"][key].numpy(), identity=f"resume/{key}")
    trace = json.loads((ref / "resume-checkpoints/input-trace.json").read_text())
    protocol = json.loads((resumed / "artifacts/training-protocol.json").read_text())
    assert protocol["inputs"] == trace["inputs"]


def test_baseline_rejects_missing_identity(tmp_path):
    """E1：来源锁定与数据身份为数值验收前置条件。"""
    from tools.verification.transolver3.protocol import validate

    baseline = json.loads((ROOT / ".context/mvp/transolver3-results/baseline.json").read_text())
    coverage = json.loads((ROOT / ".context/mvp/transolver3-results/coverage.json").read_text())
    with pytest.raises(ValueError, match="数据身份"):
        validate(baseline, coverage, reference_root=REFERENCE, dataset_identity="")
    assert (
        validate(baseline, coverage, reference_root=REFERENCE, dataset_identity="fixture")[
            "mapped_items"
        ]
        == 100
    )
    with pytest.raises(ValueError, match="覆盖"):
        validate(baseline, coverage[:-1], reference_root=REFERENCE, dataset_identity="fixture")
