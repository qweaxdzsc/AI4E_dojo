"""分片身份与新旧请求边界，以及字段目录不猜测分量。"""

import pytest

from ai4e_core.applications.aero_cfd.infer.catalog import describe_fields
from ai4e_core.applications.aero_cfd.infer.configuration import resolve_infer
from ai4e_spec.artifacts import InferenceRequest


def test_cross_split_same_name_remains_two_identities():
    value = {
        "expected_revision": "r",
        "checkpoints": [{"id": "c", "revision": "h"}],
        "sample_selection": [
            {"split": "train", "sample": "same"},
            {"split": "test", "sample": "same"},
        ],
    }
    parsed = InferenceRequest.from_dict(value)
    assert len(parsed.selections()) == 2
    assert "samples" not in parsed.to_dict() and "split" not in parsed.to_dict()
    for extra in ({"samples": ["same"]}, {"split": "test"}):
        with pytest.raises(ValueError):
            InferenceRequest.from_dict({**value, **extra})
    with pytest.raises(ValueError):
        InferenceRequest.from_dict({**value, "fields": []})
    with pytest.raises(ValueError):
        resolve_infer({"infer": {"metrics": []}})


def test_missing_dimension_is_not_guessed():
    cfg = {"trainprep": {"domains": {"surface": {"targets": {"temperature": "unknown"}}}}}
    with pytest.raises(ValueError, match="分量声明"):
        describe_fields(cfg)
