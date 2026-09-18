"""推理预检只比权重结构和采样方法，不把模型页点数当成不兼容。"""

import json
from copy import deepcopy
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.inference.rebuild import model_restore_contract, rebuild
from ai4e_core.applications.aero_cfd.infer import inspect_checkpoint
from ai4e_core.applications.aero_cfd.trainprep.preparation import digest


def _sampling(geometry=64, supernodes=8, anchor=16):
    return {
        "random_stream": "global",
        "seed": 42,
        "geometry": {"method": "uniform", "max_points": geometry},
        "supernodes": {"method": "uniform", "num_points": supernodes},
        "domains": {
            "surface": {"anchor": {"method": "uniform", "num_points": anchor}},
            "volume": {"anchor": {"method": "uniform", "num_points": anchor}},
        },
    }


def _model(dim=24, blocks="psc", sampling=None):
    return {
        "parameters": {
            "dim": dim,
            "geometry_depth": 1,
            "num_heads": 3,
            "blocks": blocks,
            "num_domain_decoder_blocks": {"surface": 1, "volume": 1},
        },
        "data_specs": {"position_dim": 3, "domains": {}, "conditioning_dims": {}},
        "supervision": [{"name": "surface_pressure", "weight": 1.0}],
        "freeze": [],
        "sampling": sampling or _sampling(),
    }


def _write_manifest(path: Path) -> Path:
    sample = path.parent / "sample"
    sample.mkdir()
    (sample / "field.bin").write_text("x")
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "state": "physical",
                "partitions": {"train": ["one"], "test": ["one"]},
                "samples": [
                    {
                        "partition": partition,
                        "sample": "one",
                        "written": True,
                        "path": str(sample),
                        "filemap": {"field": "field.bin"},
                    }
                    for partition in ("train", "test")
                ],
            }
        )
    )
    return path


def _write_preparation(path: Path, manifest: Path) -> Path:
    payload = {
        "version": 2,
        "manifest": str(manifest),
        "dataset_digest": "unused",
        "normalization": {},
        "normalization_digest": "unused",
        "declarations": {
            "sampling": _sampling(),
            "trainprep": {"domains": {}, "physical_rules": {}, "geometry_field": None},
            "data_specs": {"position_dim": 3, "domains": {}, "conditioning_dims": {}},
            "geometry_conditioning_dims": None,
            "batch_size": 1,
        },
        "external_inputs": {},
        "components": {
            "prepare": {"name": "prepare", "sha256": "a"},
            "collate": {"name": "collate", "sha256": "b"},
        },
        "split_counts": {"train": 1},
        "partitions": {"train": ["one"], "test": ["one"]},
        "split": {},
    }
    payload["digest"] = digest(payload)
    path.write_text(json.dumps(payload))
    return path


def _effective(model):
    return {
        "rawprep": {},
        "model": deepcopy(model),
        "trainprep": {"domains": {}, "physical_rules": {}, "geometry_field": None},
        "normalization": {"execute": True},
        "components": {"model": "ai4e_contrib.ability.model.abupt.component"},
        "train": {"batch_size": 1, "preparation": None},
    }


def _checkpoint(path: Path, model, digest_value: str) -> Path:
    torch.save(
        {
            "version": 2,
            "model": {"weight": torch.ones(2)},
            "epoch": 1,
            "updates": 1,
            "contract": {"preparation": digest_value, "model": {"parameters": model["parameters"]}},
            "effective_config": _effective(model),
        },
        path,
    )
    return path


def _inspect(tmp_path, current_model, checkpoint_model=None):
    manifest = _write_manifest(tmp_path / "manifest.json")
    preparation = _write_preparation(tmp_path / "preparation.json", manifest)
    digest_value = json.loads(preparation.read_text())["digest"]
    checkpoint = _checkpoint(tmp_path / "last.pt", checkpoint_model or _model(), digest_value)
    config = _effective(current_model)
    config["train"]["preparation"] = str(preparation)
    return inspect_checkpoint(checkpoint, preparation=preparation, config=config)


def test_inference_inspect_uses_prepared_slices_not_source_manifest(tmp_path):
    manifest = _write_manifest(tmp_path / "manifest.json")
    payload = {
        "version": 2,
        "manifest": str(manifest),
        "dataset_digest": "unused",
        "normalization": {},
        "normalization_digest": "unused",
        "declarations": {
            "sampling": _sampling(),
            "trainprep": {"domains": {}, "physical_rules": {}, "geometry_field": None},
            "data_specs": {"position_dim": 3, "domains": {}, "conditioning_dims": {}},
            "geometry_conditioning_dims": None,
            "batch_size": 1,
        },
        "external_inputs": {},
        "components": {
            "prepare": {"name": "prepare", "sha256": "a"},
            "collate": {"name": "collate", "sha256": "b"},
        },
        "split_counts": {"train": 1, "test": 0, "eval": 0},
        "partitions": {"train": ["one"]},
        "split": {"method": "original", "seed": 0, "counts": {"train": 1, "test": 0, "eval": 0}},
    }
    payload["digest"] = digest(payload)
    preparation = tmp_path / "preparation.json"
    preparation.write_text(json.dumps(payload))
    digest_value = payload["digest"]
    checkpoint = _checkpoint(tmp_path / "last.pt", _model(), digest_value)
    config = _effective(_model())
    config["train"]["preparation"] = str(preparation)
    result = inspect_checkpoint(checkpoint, preparation=preparation, config=config)
    assert result["compatibility"]["status"] == "compatible", result["compatibility"]
    assert result["preparation"]["partitions"] == {"train": ["one"], "test": [], "eval": []}


def test_sampling_counts_alone_do_not_block_inference_inspect(tmp_path):
    trained = _model(sampling=_sampling(64, 8, 16))
    current = _model(sampling=_sampling(3586, 512, 256))
    result = _inspect(tmp_path, current, trained)
    assert result["compatibility"]["status"] == "compatible", result["compatibility"]


def test_weight_structure_mismatch_blocks_inference_inspect(tmp_path):
    trained = _model(dim=24, blocks="psc")
    current = _model(dim=192, blocks="pscscscscsc")
    result = _inspect(tmp_path, current, trained)
    assert result["compatibility"]["status"] == "invalid"
    assert "权重结构" in result["compatibility"]["reason"]


def test_data_specs_mismatch_blocks_inference_inspect(tmp_path):
    trained = _model()
    current = _model()
    current["data_specs"] = {
        "position_dim": 3,
        "domains": {"surface": {"output_dims": {"pressure": 2}}},
        "conditioning_dims": {},
    }
    result = _inspect(tmp_path, current, trained)
    assert result["compatibility"]["status"] == "invalid"
    assert "权重结构" in result["compatibility"]["reason"]


def test_rebuild_sampling_counts_are_not_semantic_conflict(tmp_path):
    model = torch.nn.Linear(2, 2)
    saved = {
        "model_version": 2,
        "model": {
            "parameters": {"dim": 24},
            "data_specs": {"position_dim": 3},
            "sampling": _sampling(64, 8, 16),
        },
        "trainprep": {"domains": {}},
        "normalization": {"version": 1},
    }
    path = tmp_path / "ckpt.pt"
    torch.save({"version": 2, "model": model.state_dict(), "contract": saved}, path)
    current = deepcopy(saved)
    current["model"]["sampling"] = _sampling(3586, 512, 256)
    rebuild(path, torch.nn.Linear(2, 2), contract=current)
    current["model"]["parameters"] = {"dim": 192}
    with pytest.raises(ValueError, match="语义冲突"):
        rebuild(path, torch.nn.Linear(2, 2), contract=current)


def test_model_restore_contract_drops_sampling_counts():
    left = _model(sampling=_sampling(64, 8, 16))
    right = _model(sampling=_sampling(3586, 512, 256))
    assert model_restore_contract(left) == model_restore_contract(right)
    right["parameters"]["dim"] = 192
    assert model_restore_contract(left) != model_restore_contract(right)
