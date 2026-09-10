"""归一化版本记录、独立物化与失败恢复验收。"""

import json
from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization
from tests.integration.test_train_recipe import prepared_case


def test_memory_record_and_three_probe_spaces(tmp_path):
    _, cfg = prepared_case(tmp_path)
    result = probe(OmegaConf.to_container(cfg, resolve=True), prepare=prepare_inputs)
    record = Path(result["normalization_path"])
    assert record.is_file()
    assert not list(record.parent.rglob("*.pt"))
    assert not list(record.parent.rglob("manifest.json"))
    frozen = Normalization(result["normalization"])
    digest = frozen.digest
    exposed = frozen.record
    exposed["fields"]["surface_pressure"]["parameters"]["mean"] = [999]
    assert frozen.digest == digest
    assert frozen.record["training_samples"] == ["a"]
    assert frozen.record["source"]
    for name in ("surface_pressure", "surface_position", "volume_velocity", "surface_sdf"):
        torch.testing.assert_close(
            frozen.inverse(name, result["normalized"][name]), result["physical"][name]
        )
    if "surface_normals" in result["physical"]:
        torch.testing.assert_close(
            result["physical"]["surface_normals"], result["normalized"]["surface_normals"]
        )
    physical = result["physical"]["surface_pressure"].clone()
    result["sampled"]["targets"]["surface_pressure_target"].add_(100)
    torch.testing.assert_close(result["physical"]["surface_pressure"], physical)


def test_frozen_read_without_statistics_and_config_conflicts(tmp_path):
    _, cfg = prepared_case(tmp_path)
    cfg.normalization.materialize = True
    config = OmegaConf.to_container(cfg, resolve=True)
    import shutil
    from importlib.resources import files

    statistics = tmp_path / "reference.yaml"
    shutil.copyfile(
        files("ai4e_contrib.application.datasets.shapenet_car").joinpath("statistics.yaml"),
        statistics,
    )
    config["normalization"]["statistics"] = str(statistics)
    result = probe(config, prepare=prepare_inputs)
    # 仅移走测试自行持有的统计副本，不删除已安装包资源。
    assert Path(result["normalization"]["source"]).is_relative_to(tmp_path)
    Path(result["normalization"]["source"]).unlink()
    config["train"]["manifest"] = result["normalized_manifest"]
    config["normalization"].update(execute=False, materialize=False)
    loaded = probe(config, prepare=prepare_inputs)
    for name, value in result["normalized"].items():
        torch.testing.assert_close(loaded["normalized"][name], value)
    config["normalization"]["fields"]["surface_pressure"]["parameters"] = {"mean": [999]}
    with pytest.raises(ValueError, match="冲突"):
        probe(config, prepare=prepare_inputs)


def test_failed_new_version_preserves_old_asset(tmp_path, monkeypatch):
    _, cfg = prepared_case(tmp_path)
    cfg.normalization.materialize = True
    config = OmegaConf.to_container(cfg, resolve=True)
    old = probe(config, prepare=prepare_inputs)
    old_path = Path(old["normalized_manifest"])
    old_bytes = old_path.read_bytes()
    config["normalization"]["fields"]["surface_pressure"]["parameters"] = {"mean": [123]}
    original = torch.save
    calls = 0

    def fail(value, path):
        nonlocal calls
        calls += 1
        if calls == 9:
            raise OSError("second sample failure")
        return original(value, path)

    monkeypatch.setattr(torch, "save", fail)
    with pytest.raises(OSError):
        probe(config, prepare=prepare_inputs)
    assert old_path.read_bytes() == old_bytes
    index = ManifestIndex(old_path)
    assert index.read("test")["surface_pressure"].numel() > 0
    root = Path(config["paths"]["datasets"]["normalize"]["root"])
    assert list(root.rglob("manifest.json")) == [old_path]
    assert json.loads(old_bytes)["state"] == "normalized"
