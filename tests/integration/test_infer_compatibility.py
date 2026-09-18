"""推理配置的路径、冲突和旧接口边界。"""

import json
from copy import deepcopy

import pytest
import torch

from ai4e_core.applications.aero_cfd.infer import inspect_checkpoint, resolve_infer
from ai4e_core.applications.aero_cfd.infer.configuration import inference_parameters


def test_infer_parameters_isolate_training_and_legacy_values():
    cfg = {
        "train": {"device": "cuda", "preparation": "old.json"},
        "post": {"checkpoint": "old.pt", "query_chunk_size": 1},
        "infer": {
            "checkpoint": "new.pt",
            "device": "cpu",
            "preparation": "new.json",
            "samples": ["a"],
        },
    }
    before = deepcopy(cfg)
    actual = inference_parameters(cfg)
    assert actual["post"]["checkpoint"] == "new.pt"
    assert actual["train"]["preparation"] == "new.json"
    assert actual["post"]["query_chunk_size"] == 16384
    assert cfg == before


@pytest.mark.parametrize(
    "settings",
    [
        {"samples": ["a", "a"]},
        {"query_chunk_size": 0},
        {"query_chunk_size": True},
        {"samples": "a"},
        {"typo": 1},
        {"save_predictions": False, "export_vtk": True},
    ],
)
def test_invalid_settings_are_rejected(settings):
    with pytest.raises(ValueError):
        resolve_infer({"infer": settings})


def test_metadata_never_exports_tensors_and_does_not_change_rng(tmp_path):
    path = tmp_path / "last.pt"
    torch.save(
        {
            "version": 2,
            "model": {"weights": torch.ones(4)},
            "epoch": 3,
            "updates": 6,
            "contract": {"component": {"name": "test"}, "preparation": "abc"},
            "effective_config": {"train": {"device": "cpu"}},
        },
        path,
    )
    state = torch.get_rng_state().clone()
    result = inspect_checkpoint(path)
    assert result["epoch"] == 3 and "weights" not in json.dumps(result)
    assert torch.equal(state, torch.get_rng_state())
    result = inspect_checkpoint(path, preparation=tmp_path / "missing.json")
    assert result["compatibility"]["status"] == "invalid"


def comparison_report(tmp_path):
    from ai4e_core.abilities.data.validate.fingerprint import fingerprint

    metric = {
        "count": 2,
        "squared_error": 2.0,
        "absolute_error": 2.0,
        "truth_squared": 8.0,
        "mse": 1.0,
        "mae": 1.0,
        "relative_l2": 0.5,
    }
    protocol = {
        "dataset": "data1",
        "preparation": "prep1",
        "model": "m1",
        "samples": ["a"],
        "split": "test",
        "execution": {"device": "cpu", "precision": "fp32"},
    }
    protocol["digest"] = fingerprint(protocol)
    metadata = {
        "identity": {"sample": "a"},
        "domains": {"surface": {"targets": {"p": "surface.p"}, "units": {"p": "Pa"}}},
        "metrics": {"surface.p": metric},
        "protocol": protocol["digest"],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(metadata))
    return {
        "version": 1,
        "status": "succeeded",
        "protocol": protocol,
        "metrics": metadata["metrics"],
        "results": [{"sample": "a", "manifest": str(path), "metrics": metadata["metrics"]}],
    }


@pytest.mark.parametrize(
    "change,expected",
    [
        (None, "comparable"),
        ("partial", "insufficient"),
        ("samples", "insufficient"),
        ("device", "incompatible"),
        ("aggregate", "incompatible"),
        ("missing", "insufficient"),
    ],
)
def test_comparison_rejects_incomplete_or_changed_protocol(tmp_path, change, expected):
    from ai4e_core.abilities.data.validate.fingerprint import fingerprint
    from ai4e_core.applications.aero_cfd.infer import compare_results

    left = comparison_report(tmp_path)
    right = deepcopy(left)
    if change == "partial":
        right["status"] = "failed"
    elif change == "samples":
        right["protocol"]["samples"] = ["a", "b"]
        right["protocol"]["digest"] = fingerprint(
            {k: v for k, v in right["protocol"].items() if k != "digest"}
        )
    elif change == "device":
        right["protocol"]["execution"]["device"] = "mps"
        right["protocol"]["digest"] = fingerprint(
            {k: v for k, v in right["protocol"].items() if k != "digest"}
        )
    elif change == "aggregate":
        right["metrics"] = deepcopy(right["metrics"])
        right["metrics"]["surface.p"]["mse"] = 20
    elif change == "missing":
        del right["protocol"]["dataset"]
    assert compare_results([left, right])["status"] == expected


def test_infer_paths_are_resolved_without_mutating_train(tmp_path):
    from tests.integration.test_dataset_recipe import load_configuration, setup_case

    folder, _ = setup_case(tmp_path)
    cfg = load_configuration(
        folder / "config.yaml",
        {
            "infer.checkpoint": "../weight.pt",
            "infer.preparation": "../prep.json",
            "infer.results": "../result.json",
            "post.results": "../result.json",
        },
    )
    assert cfg.infer.checkpoint == str(tmp_path / "weight.pt")
    assert cfg.infer.preparation == str(tmp_path / "prep.json")
    assert cfg.infer.results == str(tmp_path / "result.json")
    assert cfg.post.results == str(tmp_path / "result.json")
