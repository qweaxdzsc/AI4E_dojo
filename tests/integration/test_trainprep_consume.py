"""现行准备消费只检查记录能否导入，不拿冻结声明挡当前平台参数。"""

import json
from copy import deepcopy

import pytest

from ai4e_core.applications.aero_cfd.trainprep.preparation import (
    consume,
    contract_conflict_message,
    declarations,
    describe_contract_diffs,
    digest,
    frozen_contract,
)


def _declared(**overrides):
    value = {
        "sampling": {
            "random_stream": "global",
            "seed": 42,
            "geometry": {"method": "uniform", "max_points": 64},
            "supernodes": {"method": "uniform", "num_points": 8},
            "domains": {
                "surface": {"anchor": {"method": "uniform", "num_points": 16}},
                "volume": {"anchor": {"method": "uniform", "num_points": 16}},
            },
        },
        "trainprep": {
            "use_physics_features": False,
            "physical_rules": {"zero_fields": {"surface_sdf": "surface_position"}},
            "geometry_field": "surface_position",
            "domains": {
                "surface": {
                    "position": "surface_position",
                    "features": {},
                    "targets": {"pressure": "surface_pressure"},
                }
            },
            "conditioning": {},
            "geometry_conditioning": {},
        },
        "data_specs": {
            "position_dim": 3,
            "domains": {"surface": {"output_dims": {"pressure": 1}}},
            "conditioning_dims": {},
        },
        "geometry_conditioning_dims": None,
        "batch_size": 1,
    }
    value.update(overrides)
    return value


def _config(declared):
    return {
        "sampling": deepcopy(declared["sampling"]),
        "trainprep": deepcopy(declared["trainprep"]),
        "model": {
            "data_specs": deepcopy(declared["data_specs"]),
            "parameters": {"geometry_conditioning_dims": declared["geometry_conditioning_dims"]},
        },
        "train": {"batch_size": declared["batch_size"]},
    }


def _write_record(path, declared):
    payload = {
        "version": 2,
        "manifest": str(path.with_name("manifest.json")),
        "dataset_digest": "unused",
        "normalization": {},
        "normalization_digest": "unused",
        "declarations": declared,
        "external_inputs": {},
        "components": {
            "prepare": {"name": "prepare", "sha256": "a"},
            "collate": {"name": "collate", "sha256": "b"},
        },
        "split_counts": {"train": 1},
        "partitions": {"train": ["s"]},
        "split": {},
    }
    payload["digest"] = digest(payload)
    path.write_text(json.dumps(payload))
    return path


def test_model_page_sampling_counts_and_batch_size_are_not_frozen():
    frozen = _declared()
    current = deepcopy(frozen)
    current["sampling"]["geometry"]["max_points"] = 3586
    current["sampling"]["supernodes"]["num_points"] = 512
    current["sampling"]["domains"]["surface"]["anchor"]["num_points"] = 256
    current["sampling"]["seed"] = 7
    current["batch_size"] = 8
    current["trainprep"]["split"] = {"method": "original", "seed": 0, "counts": {"train": 1}}
    assert frozen_contract(frozen) == frozen_contract(current)
    assert describe_contract_diffs(frozen_contract(frozen), frozen_contract(current)) == []


def test_missing_optional_keys_and_conditioning_path_do_not_false_alarm():
    frozen = _declared()
    current = deepcopy(frozen)
    del current["trainprep"]["use_physics_features"]
    current["trainprep"]["conditioning"] = {"inlet": {"path": "/other/inlet.npy", "dim": 1}}
    frozen["trainprep"]["conditioning"] = {"inlet": {"path": "/tmp/inlet.npy", "dim": 1}}
    assert frozen_contract(frozen) == frozen_contract(current)


def test_data_specs_and_field_roles_conflict_lists_chinese_items(tmp_path, monkeypatch):
    frozen = _declared()
    current = deepcopy(frozen)
    current["data_specs"] = {
        "position_dim": 3,
        "domains": {"surface": {"output_dims": {"pressure": 2}}},
        "conditioning_dims": {},
    }
    current["trainprep"] = {
        **current["trainprep"],
        "domains": {
            "surface": {
                "position": "surface_position",
                "features": {},
                "targets": {"pressure": "other_pressure"},
            }
        },
    }
    message = contract_conflict_message(frozen_contract(frozen), frozen_contract(current))
    assert "数据规格不一致" in message
    assert "字段角色不一致" in message
    assert "请重新运行 trainprep" in message
    path = _write_record(tmp_path / "preparation.json", frozen)
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.preparation.open_dataset",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("opened-prepared-data")),
    )
    with pytest.raises(RuntimeError, match="opened-prepared-data"):
        consume(_config(current), path, prepare=lambda item: item, collate=lambda items: items[0])


def test_sampling_method_change_does_not_block_consume(tmp_path, monkeypatch):
    frozen = _declared()
    current = deepcopy(frozen)
    current["sampling"]["geometry"]["method"] = "fps"
    path = _write_record(tmp_path / "preparation.json", frozen)
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.preparation.open_dataset",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("opened-prepared-data")),
    )
    with pytest.raises(RuntimeError, match="opened-prepared-data"):
        consume(_config(current), path, prepare=lambda item: item, collate=lambda items: items[0])


def test_new_declarations_omit_model_sampling_budgets():
    declared = declarations(_config(_declared()))
    sampling = declared["sampling"]
    assert "supernodes" not in sampling
    assert "max_points" not in sampling.get("geometry", {})
    assert "num_points" not in sampling.get("domains", {}).get("surface", {}).get("anchor", {})
    assert "seed" not in sampling
    assert "batch_size" not in declared
    assert sampling["geometry"]["method"] == "uniform"
    assert sampling["domains"]["surface"]["anchor"]["method"] == "uniform"


def test_old_prep_sampling_budgets_do_not_block_consume(tmp_path, monkeypatch):
    """旧准备即使带着 64/8/16，当前官方 3586/512/256 也不能挡消费。"""
    frozen = _declared()
    current = deepcopy(frozen)
    current["sampling"]["geometry"]["max_points"] = 3586
    current["sampling"]["supernodes"]["num_points"] = 512
    current["sampling"]["domains"]["surface"]["anchor"]["num_points"] = 256
    current["sampling"]["supernodes"]["method"] = "fps"
    path = _write_record(tmp_path / "preparation.json", frozen)
    assert frozen_contract(frozen) == frozen_contract(declarations(_config(current)))

    def prepare(item):
        return item

    def collate(items):
        return items[0]

    def records(component):
        return (
            {"name": "prepare", "sha256": "a"}
            if component is prepare
            else {"name": "collate", "sha256": "b"}
        )

    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.preparation.component_record", records
    )
    monkeypatch.setattr(
        "ai4e_core.applications.aero_cfd.trainprep.preparation.open_dataset",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("opened-prepared-data")),
    )
    with pytest.raises(RuntimeError, match="opened-prepared-data"):
        consume(_config(current), path, prepare=prepare, collate=collate)
