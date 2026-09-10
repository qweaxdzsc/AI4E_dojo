"""比较目的与证据门禁：不能把不同点、不同数据或未知历史标成数值等价。"""

from copy import deepcopy

import pytest

from tools.verification.comparison_protocol import assess


def protocol():
    return {
        "version": 1,
        "inference": {"query_chunk_size": 16384},
        "dataset": "data-sha",
        "partitions": {"test": ["car"]},
        "normalization": {"mean": 1},
        "layout": ["surface"],
        "model": {"dim": 192},
        "initialization": "initial-sha",
        "sampling": {"seed": 42},
        "bindings": {"geometry": "pos"},
        "weights": "weights-sha",
        "training": {"epochs": 2},
        "inputs": {"mesh": [{"digest": "geometry-and-anchor-and-query-sha"}]},
        "source": {"core": "source-sha", "model": "model-sha", "entrypoint": "script-sha"},
        "execution": {
            "device": "mps:0",
            "precision": "fp32",
            "torch": "2.14.0",
            "python": "3.12",
            "entrypoint": "pipeline.py",
            "constructor": "construct",
        },
    }


@pytest.mark.parametrize("mode", ["contract", "inference", "training"])
def test_matching_protocols(mode):
    result = assess(protocol(), protocol(), mode)
    assert result["status"] == ("contract_only" if mode == "contract" else "comparable")


@pytest.mark.parametrize(
    "key",
    [
        "dataset",
        "partitions",
        "normalization",
        "layout",
        "model",
        "sampling",
        "bindings",
        "weights",
        "inputs",
    ],
)
def test_inference_mismatch_is_not_comparable(key):
    a, b = protocol(), protocol()
    b[key] = "different"
    result = assess(a, b, "inference")
    assert result["status"] == "not_comparable"
    assert any(key in reason for reason in result["reasons"])


def test_independent_training_does_not_require_final_weights_equal():
    a, b = protocol(), protocol()
    b["weights"] = "independently-trained"
    assert assess(a, b, "training")["status"] == "comparable"
    b["initialization"] = "different-start"
    assert assess(a, b, "training")["status"] == "not_comparable"


def test_unknown_history_only_allows_contract():
    assert assess(None, None, "contract")["status"] == "contract_only"
    assert assess(protocol(), None, "inference")["status"] == "not_comparable"


@pytest.mark.parametrize("field", ["device", "precision", "torch"])
def test_cross_execution_is_separate_experiment(field):
    a, b = protocol(), protocol()
    b["execution"][field] = "different"
    result = assess(a, b, "training")
    assert result["status"] == "not_comparable"
    assert "execution" in result["provenance_differences"]


def test_source_changes_are_visible_not_assumed_equal():
    a, b = protocol(), deepcopy(protocol())
    b["source"]["core"] = "another-framework"
    result = assess(a, b, "inference")
    assert result["status"] == "comparable"
    assert result["provenance_differences"]["source"]["reference"] == b["source"]
    del b["execution"]["entrypoint"]
    assert assess(a, b, "inference")["status"] == "not_comparable"


@pytest.mark.parametrize("group", ["conditioning", "geometry_conditioning"])
def test_dataset_fingerprint_tracks_external_condition_content(tmp_path, group):
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.model.protocol import dataset_fingerprint

    path = tmp_path / "conditions.json"
    path.write_text('{"car": {"speed": [1]}}')
    config = {
        "trainprep": {"geometry_field": "pos", "domains": {}, group: {"speed": {"path": str(path)}}}
    }
    index = SimpleNamespace(partitions={"test": ["car"]}, read=lambda *_: {"pos": [0, 1, 2]})
    before = dataset_fingerprint(index, config)
    path.write_text('{"car": {"speed": [2]}}')
    assert dataset_fingerprint(index, config) != before
