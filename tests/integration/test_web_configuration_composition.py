"""平台编辑契约：删除、切换和未编辑研究参数的保存语义。"""

from copy import deepcopy

import pytest
from ai4e_server.modules.stages import compose_configuration


def test_explicit_values_and_literal_field_names():
    original = {
        "trainprep": {
            "domains": {"surface": {"features": {"p.mean": "p", "q": "q"}}},
            "normalization": {"materialize": True},
        },
        "research": {"keep": [1, 2]},
    }
    before = deepcopy(original)
    values = {
        "domains": {"surface": {"features": {"q": "new"}}},
        "normalization": {"materialize": False},
    }
    result = compose_configuration(
        original,
        "trainprep",
        values,
        edited_paths=[["domains", "surface", "features", "q"], ["normalization", "materialize"]],
        removed_paths=[["domains", "surface", "features", "p.mean"]],
    )
    assert result["trainprep"]["domains"]["surface"]["features"] == {"q": "new"}
    assert result["trainprep"]["normalization"]["materialize"] is False
    assert result["research"] == before["research"]
    assert original == before


@pytest.mark.parametrize("value", [None, False, 0, [], {}])
def test_explicit_empty_values_replace(value):
    result = compose_configuration(
        {"model": {"parameters": {"x": {"old": 1}, "keep": 3}}},
        "model",
        {"parameters": {"x": value}},
        edited_paths=[["parameters", "x"]],
    )
    assert result["model"]["parameters"] == {"x": value, "keep": 3}


def test_no_edits_does_not_materialize_display_defaults():
    assert compose_configuration(
        {"train": {"learning_rate": 1}},
        "train",
        {"learning_rate": 2, "weight_decay": 0},
        edited_paths=[],
    ) == {"train": {"learning_rate": 1}}


def test_method_change_cleans_old_parameters_not_extension():
    original = {
        "trainprep": {
            "normalization": {
                "fields": {
                    "p": {
                        "method": "custom",
                        "parameters": {"old": 1},
                        "statistics_keys": {"mean": "old"},
                        "target": "user.fn",
                        "extension": "keep",
                    }
                }
            }
        }
    }
    result = compose_configuration(
        original,
        "trainprep",
        {"normalization": {"fields": {"p": {"method": "minmax"}}}},
        edited_paths=[["normalization", "fields", "p", "method"]],
    )
    assert result["trainprep"]["normalization"]["fields"]["p"] == {
        "method": "minmax",
        "extension": "keep",
    }


def test_aliases_only_clean_when_edited():
    original = {"rawprep": {"format": "pt"}, "model": {}, "trainprep": {"sampling": {"seed": 0}}}
    result = compose_configuration(
        original, "rawprep", {"formats": ["pt", "zarr"]}, edited_paths=[["formats"]]
    )
    assert result["rawprep"] == {"formats": ["pt", "zarr"]}
    assert result["trainprep"] == original["trainprep"]
    result = compose_configuration(
        result, "model", {"sampling": {"seed": 1}}, edited_paths=[["sampling"]]
    )
    assert "sampling" not in result["trainprep"]


@pytest.mark.parametrize(
    "edited,removed",
    [
        ([["parameters"], ["parameters", "x"]], []),
        ([["parameters"]], [["parameters"]]),
        ([["initial_weights"]], []),
        ([[]], []),
        ([["parameters", "absent"]], []),
    ],
)
def test_invalid_requests_rejected(edited, removed):
    with pytest.raises(ValueError):
        compose_configuration(
            {"model": {}}, "model", {"parameters": {}}, edited_paths=edited, removed_paths=removed
        )


def test_legacy_patch_preserves_unknown_fields():
    result = compose_configuration(
        {"train": {"learning_rate": 1, "research": 2}}, "train", {"learning_rate": 3}
    )
    assert result["train"] == {"learning_rate": 3, "research": 2}


def test_rawprep_dependencies_are_resolved_on_server():
    """客户端只提交几何选择时，服务端也清理互斥项、筛选和统计依赖。"""
    original = {
        "rawprep": {
            "geometry": {"old": {}},
            "save_fields": ["p", "normal"],
            "statistics": {"fields": ["p", "normal"]},
            "filters": {"surface": ["valid"]},
        }
    }
    profile = {
        "geometry": [{"id": "new", "conflicts": ["old"]}],
        "outputs": [{"name": "normal", "requires": ["old"]}],
        "filters": [{"domain": "surface", "id": "valid", "requires": ["old"]}],
    }
    result = compose_configuration(
        original,
        "rawprep",
        {"geometry": {"new": {}}},
        edited_paths=[["geometry", "new"]],
        rawprep_profile=profile,
    )["rawprep"]
    assert result["geometry"] == {"new": {}}
    assert result["save_fields"] == ["p"]
    assert result["statistics"]["fields"] == ["p"]
    assert result["filters"]["surface"] == []


def test_edit_legacy_sampling_preserves_unedited_budget():
    original = {
        "model": {},
        "trainprep": {"sampling": {"seed": 2, "geometry": {"max_points": 123}}},
    }
    result = compose_configuration(
        original, "model", {"sampling": {"seed": 3}}, edited_paths=[["sampling", "seed"]]
    )
    assert result["model"]["sampling"] == {"seed": 3, "geometry": {"max_points": 123}}
    assert "sampling" not in result["trainprep"]


def test_training_split_is_an_allowed_train_edit():
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2] / "packages/ai4e-server/modules/stages/configuration.py"
    )
    spec = importlib.util.spec_from_file_location("dojo_source_stage_configuration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.compose_configuration(
        {"train": {"learning_rate": 1}},
        "train",
        {"training_split": "test"},
        edited_paths=[["training_split"]],
    )
    assert result["train"]["training_split"] == "test"
    assert result["train"]["learning_rate"] == 1


def test_legacy_method_switch_keeps_new_explicit_custom_parameters():
    original = {"trainprep": {"normalization": {"fields": {"p": {"method": "identity"}}}}}
    custom = {"method": "custom", "target": "research.normalize", "parameters": {"factor": 2}}
    result = compose_configuration(
        original, "trainprep", {"normalization": {"fields": {"p": custom}}}
    )
    assert result["trainprep"]["normalization"]["fields"]["p"] == custom
