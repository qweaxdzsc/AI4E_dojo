"""正式两轮全量：官方规模、正式模型配置与参考统计量。"""

import json
from pathlib import Path

import pytest
import torch
import yaml

from ai4e_contrib.application.datasets import shapenet_car
from ai4e_core.abilities.data.source.split import load_split_lists
from tests.support import shapenet_processed_root

pytestmark = pytest.mark.local_data

PARTITION = Path(shapenet_car.MANIFEST_PATH).with_name("partition.yaml")
STATS = Path(shapenet_car.MANIFEST_PATH).with_name("statistics.yaml")
FILEMAP = {
    "surface_pressure": "surface_pressure.pt",
    "surface_position": "surface_points.pt",
    "surface_normals": "surface_normals.pt",
    "volume_velocity": "volume_velocity.pt",
    "volume_position": "volume_points.pt",
    "volume_sdf": "volume_sdf.pt",
    "volume_normals": "volume_normals.pt",
}


def _official_root(root: Path) -> Path | None:
    if (root / "param0").is_dir():
        return root
    nested = root / "preprocessed"
    return nested if (nested / "param0").is_dir() else None


def _existing_manifest(root: Path) -> Path | None:
    for candidate in (root / "manifest.json", root.parent / "manifest.json"):
        if candidate.is_file():
            return candidate
    return None


def _build_official_manifest(root: Path, dest: Path, partitions: dict[str, list[str]]) -> Path:
    """按官方分片与已落盘张量写出 version=1 物理清单。"""
    samples = []
    for partition, names in partitions.items():
        for sample in names:
            directory = root / sample
            if not directory.is_dir():
                raise FileNotFoundError(f"缺少官方样本目录: {directory}")
            fields = {}
            for name, filename in FILEMAP.items():
                path = directory / filename
                if not path.is_file():
                    raise FileNotFoundError(f"缺少官方场文件: {path}")
                value = torch.load(path, map_location="cpu", weights_only=True)
                fields[name] = {
                    "shape": list(value.shape),
                    "dtype": str(value.dtype),
                    "state": "physical",
                }
                del value
            samples.append(
                {
                    "partition": partition,
                    "sample": sample,
                    "written": True,
                    "path": str(directory.resolve()),
                    "filemap": dict(FILEMAP),
                    "fields": fields,
                }
            )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(
            {
                "version": 1,
                "state": "physical",
                "partitions": {key: list(value) for key, value in partitions.items()},
                "samples": samples,
                "statistics": {
                    "mode": "reference",
                    "path": str(STATS.resolve()),
                    "state": "physical",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return dest


def _resolve_official_manifest(tmp_path: Path) -> Path:
    root = _official_root(shapenet_processed_root())
    if root is None:
        pytest.skip(f"缺少官方预处理库: {shapenet_processed_root()}")
    official = load_split_lists(PARTITION)
    if len(official["train"]) != 789 or len(official["test"]) != 100:
        raise AssertionError("官方分片名单必须是 789/100")
    existing = _existing_manifest(root)
    if existing is not None:
        manifest = json.loads(existing.read_text())
        partitions = manifest.get("partitions") or {}
        if len(partitions.get("train") or []) == 789 and len(partitions.get("test") or []) == 100:
            assert partitions["train"] == official["train"]
            assert partitions["test"] == official["test"]
            return existing
    return _build_official_manifest(root, tmp_path / "official_manifest.json", official)


def test_formal_two_epoch_official_scale(tmp_path):
    manifest_path = _resolve_official_manifest(tmp_path)
    official = load_split_lists(PARTITION)
    manifest = json.loads(manifest_path.read_text())
    assert manifest["partitions"]["train"] == official["train"]
    assert manifest["partitions"]["test"] == official["test"]
    import os
    import subprocess
    import sys

    from omegaconf import OmegaConf

    from tests.integration.test_dataset_recipe import public_config, setup_case

    folder, cfg = setup_case(tmp_path)
    cfg.statistics.mode = "reference"
    cfg.normalization.execute = True
    cfg.normalization.statistics = str(STATS)
    cfg.train.mode = "fit"
    cfg.train.manifest = str(manifest_path)
    cfg.train.max_epochs = 2
    cfg.train.optimizer = "lion"
    cfg.train.scheduler = "warmup_cosine"
    cfg.train.test_repeat = 10
    cfg.train.snapshot = True
    cfg.train.device = "auto"
    cfg.pipeline.stages = ["train"]
    OmegaConf.save(public_config(cfg), folder / "config.yaml")
    run_root = Path(cfg.run_root)
    before = set(run_root.iterdir()) if run_root.exists() else set()
    result = subprocess.run(
        [sys.executable, str(folder / "train.py")],
        capture_output=True,
        text=True,
        timeout=None,
        check=False,
        env={**os.environ, "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
    )
    after = set(run_root.iterdir()) - before
    assert len(after) == 1, result.stderr
    directory = after.pop()
    summary = json.loads((directory / "summary.json").read_text())
    assert result.returncode == 0, result.stderr
    assert not summary["failed"]
    assert (directory / "inputs" / "config.yaml").is_file()
    assert (directory / "code.tar.gz").is_file()
    resolved = yaml.safe_load((directory / "inputs" / "config.yaml").read_text())
    assert resolved["model"]["parameters"]["dim"] == 192
    assert resolved["train"]["optimizer"] == "lion"
    names = {path.name for path in (directory / "checkpoints").iterdir()}
    assert names >= {"best.pt", "latest.pt", "last.pt"}
    last = torch.load(directory / "checkpoints" / "last.pt", weights_only=False)
    assert last["epoch"] == 2
    assert last["ema"] is not None
    assert "loss" in summary["reports"]["train"]["history"][0]["evaluation"]
