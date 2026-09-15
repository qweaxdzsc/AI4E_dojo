"""C1：选择声明名单，身份由组件提供，空选择不会隐式执行整库。

页面只提交全部或指定样本；分片模式仅保留旧请求兼容。
"""

import pytest

from ai4e_core.applications.aero_cfd.rawprep.catalog import choose_samples, sample_key


def test_scope_and_same_named_samples():
    groups = {"train": ["same", "two"], "test": ["same"]}
    assert choose_samples(groups, {"mode": "all"}) == groups
    assert choose_samples(groups, {"mode": "partitions", "values": ["test"]}) == {"test": ["same"]}
    assert choose_samples(groups, {"mode": "samples", "values": [sample_key("test", "same")]}) == {
        "test": ["same"]
    }


@pytest.mark.parametrize(
    "scope",
    [
        {"mode": "samples", "values": []},
        {"mode": "partitions", "values": ["missing"]},
        {"mode": "samples", "values": ["same"]},
        {"mode": "typo"},
    ],
)
def test_invalid_scope(scope):
    with pytest.raises(ValueError):
        choose_samples({"train": ["same"]}, scope)
