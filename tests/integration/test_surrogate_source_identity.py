"""NASA跨分片身份反例；小属性表准备不执行任何代理拟合或建树。"""

import json
import shutil
from pathlib import Path

import h5py
import numpy as np
import pytest

from ai4e_contrib.application.datasets.nasa_crm.constants import (
    CONDITION_FIELDS,
    GLOBAL_TARGET_FIELDS,
)
from ai4e_contrib.application.surrogate_modeling.preparation import prepare_nasa, read_prepared


def _write(path, x, y, *, prefix="sample"):
    with h5py.File(path, "w") as stream:
        for index, (inputs, targets) in enumerate(zip(x, y, strict=True)):
            group = stream.create_group(f"{prefix}_{index:03d}")
            for name, value in zip(CONDITION_FIELDS, inputs, strict=True):
                group.attrs[name] = value
            for name, value in zip(GLOBAL_TARGET_FIELDS, targets, strict=True):
                group.attrs[name] = value


def _values():
    x = np.arange(36.0).reshape(6, 6) / 10
    y = np.arange(18.0).reshape(6, 3) / 7
    return x, y


def test_nasa_copied_file_is_not_an_independent_split(tmp_path):
    x, y = _values()
    train, test = tmp_path / "train.h5", tmp_path / "copy.h5"
    _write(train, x, y)
    shutil.copyfile(train, test)
    with pytest.raises(ValueError, match="属性表内容完全相同"):
        prepare_nasa(train, test, tmp_path / "prepared")
    assert not (tmp_path / "prepared").exists()


def test_nasa_renamed_groups_and_partial_duplicate_are_rejected(tmp_path):
    x, y = _values()
    train, test = tmp_path / "train.h5", tmp_path / "test.h5"
    _write(train, x, y)
    _write(test, np.vstack((x[2], x[3] + 10)), np.vstack((y[2], y[3] + 10)), prefix="renamed")
    with pytest.raises(ValueError, match="1 条完全相同"):
        prepare_nasa(train, test, tmp_path / "prepared")


def test_nasa_same_conditions_distinct_responses_are_diagnosed_not_rejected(tmp_path):
    x, y = _values()
    train, test = tmp_path / "train.h5", tmp_path / "test.h5"
    _write(train, x, y)
    _write(test, np.vstack((x[1], x[1], x[4] + 20)), np.vstack((y[1] + 1, y[1] + 2, y[4] + 20)))
    path = prepare_nasa(train, test, tmp_path / "prepared")
    diagnostics = json.loads(Path(path).read_text())["diagnostics"]
    assert diagnostics["shared_input_condition_count"] == 1
    assert diagnostics["shared_input_distinct_response_pair_count"] == 2
    record, arrays = read_prepared(path, "test")
    assert record["metadata"]["input_fields"] == list(CONDITION_FIELDS)
    assert record["metadata"]["fields"] == list(GLOBAL_TARGET_FIELDS)
    np.testing.assert_array_equal(arrays["physical_input"][0], x[1])
    np.testing.assert_array_equal(arrays["physical_target"][0, 0], y[1] + 1)
    np.testing.assert_allclose(record["metadata"]["statistics"]["input"]["mean"], x.mean(0))
