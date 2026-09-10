"""复制脚本、可安装适配器、惰性数据流、产物读回与日志的整链验收。"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf
from omegaconf.errors import OmegaConfBaseException

from ai4e_contrib.application.datasets import shapenet_car
from ai4e_core import run
from ai4e_core.applications.aero_cfd import rawprep as pre
from ai4e_core.applications.aero_cfd.train import open_manifest_sample
from tests.integration.test_shapenet_pre_recipe import _write_sample

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"


# 普通模板并非安装包；测试按其实际目录加载配置模块。
sys.path.insert(0, str(RECIPE))
from configuration import _public, application_parameters, load_configuration


def public_config(cfg):
    """将底层回归夹具显式转换为新版用户配置，不改变被测库接口。"""
    data = OmegaConf.to_container(cfg, resolve=True)
    data["pipeline"]["stages"] = [
        "rawprep" if x == "datapre" else x for x in data["pipeline"]["stages"]
    ]
    return OmegaConf.create(_public(data))


def load_internal(path, overrides=None):
    """旧底层夹具继续消费内部输入，新案例入口使用新配置。"""
    return OmegaConf.create(application_parameters(load_configuration(path, overrides)))


def setup_case(tmp_path):
    """创建真实小网格，不使用全局数据路径或已安装 recipe。"""
    folder = tmp_path / "experiment"
    shutil.copytree(RECIPE, folder, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    raw = tmp_path / "raw"
    for sample in ("a", "b"):
        _write_sample(raw / sample)
    manifest = yaml.safe_load(shapenet_car.MANIFEST_PATH.read_text())
    manifest["reference_statistics"] = str(shapenet_car.MANIFEST_PATH.with_name("statistics.yaml"))
    manifest["fields"]["surface"]["pressure"]["array"] = "pressure"
    manifest["fields"]["volume"]["velocity"]["array"] = "velocity"
    manifest_path = tmp_path / "source-manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest))
    cfg = yaml.safe_load((folder / "config.yaml").read_text())
    cfg["dataset"].update(
        root=str(raw), manifest=str(manifest_path), partition={"train": ["a"], "test": ["b"]}
    )
    cfg["pipeline"]["stages"] = ["rawprep"]
    cfg["data_root"] = "../data"
    cfg["run_root"] = "../records"
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    return folder, load_internal(folder / "config.yaml")


def load_datapre(folder):
    """按文件加载用户脚本，不依赖 package 注册。"""
    spec = importlib.util.spec_from_file_location("user_datapre", folder / "rawprep.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rawprep


def execute_case(folder, cfg, **flags):
    return run.run_recipe(
        public_config(cfg),
        stages={"rawprep": load_datapre(folder)},
        script=folder / "rawprep.py",
        flags={"dry_run": False, "overwrite": False, "continue_on_error": False, **flags},
    )


def test_copy_pipeline_and_datapre_are_equivalent(tmp_path):
    folder, _cfg = setup_case(tmp_path)
    for entry in ("pipeline.py", "rawprep.py"):
        output = tmp_path / entry.removesuffix(".py")
        result = subprocess.run(
            [sys.executable, "-B", str(folder / entry), "--set", f"data_root={output}"],
            cwd=tmp_path,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert result.returncode == 0, result.stdout + result.stderr
        loaded = open_manifest_sample(output / "manifest.json", partition="train")
        assert loaded["surface_pressure"].tolist() == [1, 2, 3, 4]
        assert not (output / "normalize").exists()
    records = list((tmp_path / "records").iterdir())
    assert len(records) == 2
    for record in records:
        names = sorted(p.name for p in (record / "inputs").iterdir())
        assert names == ["config.yaml"]
        effective = yaml.safe_load((record / "inputs/config.yaml").read_text())
        assert effective["execution"]["dry_run"] is False
        assert effective["pipeline"]["stages"] == ["rawprep"]
        log = (record / "logs/run.log").read_text()
        for phrase in (
            "[rawprep/字段提取/开始]",
            "[rawprep/字段提取/结束]",
            "[rawprep/批量前处理/进度]",
            "[rawprep/统计/开始]",
            "[rawprep/数据清单/结束]",
        ):
            assert phrase in log
        assert "[rawprep/阶段/开始]" in log
        assert "[rawprep/datapre/" not in log
        assert "展开配置=" not in log
        assert "'results':" not in log
    assert not list(folder.rglob("__pycache__"))
    assert not list(folder.glob("__*__.py"))
    assert not (folder / "pre.py").exists()


def test_pipeline_rejects_legacy_pre_stage(tmp_path):
    folder, _cfg = setup_case(tmp_path)
    config = yaml.safe_load((folder / "config.yaml").read_text())
    config["pipeline"]["stages"] = ["pre"]
    (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    result = subprocess.run(
        [sys.executable, str(folder / "pipeline.py")],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "请改用 rawprep" in result.stderr


def test_paths_and_independent_partition_override(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg = load_internal(folder / "config.yaml", {"paths.datasets.test": "../separate/test"})
    assert cfg.paths.datasets.train == str(tmp_path / "data/train")
    assert cfg.paths.datasets.normalize.train == str(tmp_path / "data/normalize/train")
    assert execute_case(folder, cfg) == 0
    assert (tmp_path / "separate/test/b/volume_velocity.pt").exists()
    assert not (tmp_path / "data/eval").exists()
    assert not list(folder.rglob("*.pt"))


@pytest.mark.parametrize("value", ["${missing_root}/train", "${paths.datasets.train}"])
def test_invalid_interpolation_rejected(tmp_path, value):
    folder, _ = setup_case(tmp_path)
    with pytest.raises(OmegaConfBaseException):
        load_internal(folder / "config.yaml", {"paths.datasets.train": value})
    assert not (tmp_path / "records").exists()


def test_dataset_registration_never_reads_mesh(tmp_path, monkeypatch):
    folder, cfg = setup_case(tmp_path)
    import importlib

    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    calls = []
    original = module.read_file

    def reader(*a, **kw):
        calls.append(str(a[0]))
        return original(*a, **kw)

    monkeypatch.setattr(module, "read_file", reader)
    dataset = shapenet_car.open_dataset(
        root=cfg.dataset.root, manifest=cfg.dataset.manifest, partition=cfg.dataset.partition
    )
    prep = pre.read(dataset, sources=cfg.sources)
    prep = pre.extract_fields(prep, fields=cfg.fields)
    assert not calls
    assert not dataset.steps
    assert prep.steps
    assert execute_case(folder, cfg) == 0
    assert len(calls) == 4


def test_train_statistics_excludes_test(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg.statistics.mode = "fit"
    assert execute_case(folder, cfg) == 0
    stats = yaml.safe_load((tmp_path / "data/train/statistics.yaml").read_text())
    assert stats["metadata"]["samples"] == ["a"]
    assert stats["surface_pressure_mean"] == [2.5]
    assert stats["surface_pressure_count"] == 4
    manifest = json.loads((tmp_path / "data/manifest.json").read_text())
    assert manifest["statistics"]["mode"] == "fit"
    assert manifest["state"] == "physical"


@pytest.mark.parametrize("continue_on_error", [False, True])
def test_failure_keeps_commits_without_complete_manifest(tmp_path, continue_on_error):
    folder, cfg = setup_case(tmp_path)
    (tmp_path / "raw/b/hexvelo_smpl.vtk").unlink()
    assert execute_case(folder, cfg, continue_on_error=continue_on_error) == 1
    assert (tmp_path / "data/train/a/surface_pressure.pt").exists()
    assert not (tmp_path / "data/manifest.json").exists()
    assert not (tmp_path / "data/train/statistics.yaml").exists()
    record = next((tmp_path / "records").iterdir())
    summary = json.loads((record / "summary.json").read_text())
    assert summary["failed"] and summary["success"] == 1
    assert (record / "logs/errors.log").exists()


def test_dry_run_and_overwrite_preflight(tmp_path):
    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg, dry_run=True) == 0
    assert not (tmp_path / "data").exists()
    assert execute_case(folder, cfg) == 0
    manifest = (tmp_path / "data/manifest.json").read_bytes()
    assert execute_case(folder, cfg) == 1
    assert (tmp_path / "data/manifest.json").read_bytes() == manifest


def test_unknown_field_dimensions_and_source_overlap(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg.fields.surface.pressure.components = 2
    assert execute_case(folder, cfg) == 1
    assert not (tmp_path / "data").exists()
    cfg.fields.surface.pressure.components = 1
    cfg.paths.datasets.train = str(tmp_path / "raw/train")
    assert execute_case(folder, cfg) == 1
    assert not (tmp_path / "raw/train").exists()


def test_reference_statistics_and_normalization_declaration(tmp_path):
    folder, cfg = setup_case(tmp_path)
    cfg.statistics.mode = "reference"
    assert execute_case(folder, cfg) == 0
    manifest = json.loads((tmp_path / "data/manifest.json").read_text())
    assert manifest["statistics"]["mode"] == "reference"
    assert manifest["statistics"]["samples"] is None
    assert not (tmp_path / "data/train/statistics.yaml").exists()
    enabled = load_internal(folder / "config.yaml", {"trainprep.normalization.execute": True})
    assert enabled.normalization.execute


def test_duplicate_partition_identity_rejected(tmp_path):
    _folder, cfg = setup_case(tmp_path)
    with pytest.raises(ValueError, match="重复"):
        shapenet_car.open_dataset(
            root=cfg.dataset.root,
            manifest=cfg.dataset.manifest,
            partition={"train": ["a"], "test": ["a"]},
        )


def test_overwrite_failure_withdraws_old_manifest(tmp_path):
    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg) == 0
    (tmp_path / "raw/b/hexvelo_smpl.vtk").unlink()
    assert execute_case(folder, cfg, overwrite=True) == 1
    assert not (tmp_path / "data/manifest.json").exists()
    assert list((tmp_path / "data").glob(".manifest.*.previous.json"))


def test_long_operation_reports_time_without_fake_percentage(caplog, monkeypatch):
    import time

    from ai4e_core.base import events

    monkeypatch.setattr(events, "INTERVAL", 0.01)
    with caplog.at_level("INFO", logger="ai4e_core.run"), events.operation("慢能力"):
        time.sleep(0.04)
    assert "[慢能力/开始]" in caplog.text
    assert "[慢能力/运行中]" in caplog.text
    assert "[慢能力/结束]" in caplog.text
    assert "%" not in caplog.text


def test_training_standard_uses_manifest(tmp_path):
    from ai4e_core.applications.aero_cfd.trainprep.dataset import (
        open_splits_step,
        read_probe_sample_step,
    )

    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg) == 0
    ctx = {"config": {"train": {"manifest": str(tmp_path / "data/manifest.json")}}}
    ctx = open_splits_step(ctx)
    ctx["model"] = "ab_upt"
    ctx = read_probe_sample_step(ctx)
    assert ctx["split_counts"] == {"train": 1, "test": 1}
    assert ctx["sample_id"] == "b"
    assert ctx["sample"]["surface_sdf"].count_nonzero().item() == 0


def test_reader_checks_manifest_shape_and_state(tmp_path):
    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg) == 0
    path = tmp_path / "data/manifest.json"
    manifest = json.loads(path.read_text())
    manifest["samples"][0]["fields"]["surface_pressure"]["shape"] = [100]
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="清单不一致"):
        open_manifest_sample(path, partition="train")


def test_adapter_can_be_copied_and_modified(tmp_path):
    _folder, cfg = setup_case(tmp_path)
    copied = tmp_path / "shared_adapter"
    shutil.copytree(shapenet_car.MANIFEST_PATH.parent, copied)
    spec = importlib.util.spec_from_file_location("copied_adapter", copied / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.open_dataset(root=cfg.dataset.root, partition={"train": ["a"]})
    assert data.samples == ("a",)
    assert Path(data.metadata["manifest_path"]).parent == copied
    assert importlib.util.find_spec("ai4e_recipes") is None


def test_previous_sample_meshes_released_before_next_sample(tmp_path, monkeypatch):
    import importlib
    import weakref

    folder, cfg = setup_case(tmp_path)
    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.read")
    original = module.read_file
    references = []

    def reader(*args, **kwargs):
        if len(references) == 2:
            assert all(reference() is None for reference in references)
        mesh = original(*args, **kwargs)
        references.append(weakref.ref(mesh))
        return mesh

    monkeypatch.setattr(module, "read_file", reader)
    assert execute_case(folder, cfg) == 0
    assert len(references) == 4
    assert all(reference() is None for reference in references)


def test_geometry_parameters_are_forwarded(tmp_path, monkeypatch):
    import importlib

    folder, cfg = setup_case(tmp_path)
    module = importlib.import_module("ai4e_core.applications.aero_cfd.rawprep.derive")
    original = module.nearest_vertex_distance_and_direction
    received = []

    def nearest(*args, **kwargs):
        received.append(kwargs["epsilon"])
        return original(*args, **kwargs)

    monkeypatch.setattr(module, "nearest_vertex_distance_and_direction", nearest)
    cfg.geometry = {name: {} for name in cfg.geometry}
    cfg.geometry.nearest_vertex.epsilon = 1e-6
    assert execute_case(folder, cfg) == 0
    assert received == [1e-6, 1e-6]
