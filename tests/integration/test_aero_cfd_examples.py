"""A1—A3：共享 recipe 的组件选择及完整复制运行。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from ai4e_contrib.application.aero_cfd import load, resolve_config
from tests.transolver_assets import configuration

ROOT = Path(__file__).resolve().parents[2]


def test_components_have_distinct_defaults(tmp_path):
    """A1：公共入口按声明选择，另一模型的默认参数不能混入。"""
    cfg, _ = configuration(tmp_path)
    from omegaconf import OmegaConf

    resolved = resolve_config(OmegaConf.to_container(cfg, resolve=True))
    assert "radius" not in resolved["model"]["parameters"]
    assert load({}).model.SOURCE != load(cfg).model.SOURCE


def test_copied_four_stage_pipeline(tmp_path):
    """A2：历史复制脚本仍完整运行 NPY 参考前处理、训练与数值后处理。"""
    cfg, path = configuration(tmp_path, legacy=True)
    folder = tmp_path / "recipe"
    shutil.copytree(
        ROOT / "tests/fixtures/recipe_before_explicit",
        folder,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    result = subprocess.run(
        [sys.executable, "-B", str(folder / "pipeline.py"), "--config", str(path)],
        check=False,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={**os.environ, "OMP_NUM_THREADS": "1"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = next(Path(cfg.run_root).iterdir())
    training = json.loads((run / "artifacts/training.json").read_text())
    assert training["epochs"] == 2 and training["updates"] == 8
    progress = json.loads((run / "artifacts/post-progress.json").read_text())
    assert progress["status"] == "succeeded"
    metrics = json.loads((Path(cfg.data_root) / "post/test/metrics.json").read_text())
    assert metrics["aggregate"]["point_count"] == 48
    assert len(list((Path(cfg.data_root) / "predictions/test").glob("*/prediction_part*.npy"))) == 8


def test_relative_hdf_paths_follow_copied_configuration(tmp_path):
    """A2：从其他工作目录运行，所有HDF来源仍相对配置文件解析。"""
    import yaml

    from tests.integration.test_dataset_recipe import load_internal

    _, path = configuration(tmp_path)
    public = yaml.safe_load(path.read_text())
    public["inputs"]["rawprep"].update(
        source="../raw",
        train_h5="${inputs.rawprep.source}/training.h5",
        test_h5="${inputs.rawprep.source}/test.h5",
    )
    path.write_text(yaml.safe_dump(public, sort_keys=False))
    actual = load_internal(path)
    assert Path(actual.dataset.train_h5) == tmp_path / "raw/training.h5"
    assert Path(actual.dataset.test_h5) == tmp_path / "raw/test.h5"


def test_partial_sampling_defaults_stay_in_public_model(tmp_path):
    """A1：缺少采样子项时补齐自身默认值，公共配置不注入旧顶层字段。"""
    import yaml

    from tests.integration.test_dataset_recipe import load_configuration

    _, path = configuration(tmp_path)
    public = yaml.safe_load(path.read_text())
    public["trainprep"].pop("sampling", None)
    public["trainprep"].pop("sampling", None)
    public["model"]["sampling"] = {"seed": 17}
    path.write_text(yaml.safe_dump(public, sort_keys=False))
    actual = load_configuration(path)
    assert actual.model.sampling.seed == 17 and actual.model.sampling.stride == 4
    assert "sampling" not in actual and "normalization" not in actual


def test_independent_stages_match_pipeline_weights_and_predictions(tmp_path):
    """A2：分别启动四个阶段，通过持久化准备与权重交接得到相同结果。"""
    import numpy as np
    import torch
    import yaml

    cfg, path = configuration(tmp_path / "separate", legacy=True)
    public = yaml.safe_load(path.read_text())
    runs = Path(cfg.run_root)
    environment = {**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}
    last = None
    for stage in ("rawprep", "trainprep", "train", "post"):
        public["pipeline"]["stages"] = [stage]
        if stage == "train":
            public["train"]["preparation"] = str(last / "artifacts/preparation.json")
        if stage == "post":
            public["post"]["checkpoint"] = str(last / "checkpoints/best.pt")
        path.write_text(yaml.safe_dump(public, sort_keys=False))
        before = set(runs.iterdir()) if runs.exists() else set()
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tests/fixtures/recipe_before_explicit" / f"{stage}.py"),
                "--config",
                str(path),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        last = (set(runs.iterdir()) - before).pop()
        if stage == "train":
            trained = last
    assert json.loads((last / "artifacts/post-progress.json").read_text())["status"] == "succeeded"
    other, other_path = configuration(tmp_path / "pipeline", legacy=True)
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(ROOT / "tests/fixtures/recipe_before_explicit/pipeline.py"),
            "--config",
            str(other_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run = next(Path(other.run_root).iterdir())
    left = torch.load(trained / "checkpoints/latest.pt", weights_only=False)["model"]
    right = torch.load(run / "checkpoints/latest.pt", weights_only=False)["model"]
    for name in left:
        torch.testing.assert_close(left[name], right[name], rtol=0, atol=0)
    for prediction in (Path(cfg.data_root) / "predictions/test").glob("*/prediction_part*.npy"):
        other_prediction = (
            Path(other.data_root)
            / "predictions/test"
            / prediction.relative_to(Path(cfg.data_root) / "predictions/test")
        )
        np.testing.assert_array_equal(np.load(prediction), np.load(other_prediction))


def test_rawprep_dry_run_and_overwrite_gate(tmp_path):
    """B1/B2：真实入口干跑不写数据，非空目标在干跑和提交中均拒绝覆盖。"""
    cfg, path = configuration(tmp_path, legacy=True)
    command = [
        sys.executable,
        "-B",
        str(ROOT / "tests/fixtures/recipe_before_explicit/rawprep.py"),
        "--config",
        str(path),
    ]
    result = subprocess.run(
        command + ["--dry-run"], cwd=tmp_path, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    root = Path(cfg.data_root)
    assert not root.exists() or not list(root.iterdir())
    root.mkdir(exist_ok=True)
    sentinel = root / "unrelated.txt"
    sentinel.write_text("keep")
    for flags in (["--dry-run"], []):
        result = subprocess.run(
            command + flags, cwd=tmp_path, capture_output=True, text=True, check=False
        )
        assert result.returncode != 0
        assert "非空" in result.stdout + result.stderr
        assert sentinel.read_text() == "keep"
        assert not (root / "manifest.json").exists()
