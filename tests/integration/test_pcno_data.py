"""发布数据准入：拒绝缺字段、错维、坏数值及井标签错配。"""

import pytest
import torch

from ai4e_contrib.application.datasets.geothermal_cmg.adapter import (
    inspect_chunk as installed_inspect,
)
from tools.verification.pcno.data_audit import inspect_chunk


@pytest.fixture
def chunk():
    spatial = torch.zeros(1, 2, 2, 2, 3, 14)
    spatial[:, 0, 0, :, :, 2] = 1
    spatial[:, 1, 1, :, :, 2] = -1
    return {
        "pres": torch.zeros(1, 2, 2, 2, 3),
        "temp": torch.ones(1, 2, 2, 2, 3),
        "spatial_params": spatial,
        "global_params": torch.zeros(1, 4),
        "Temp_wh": [torch.ones(1, 2)],
        "Heat_wh": [torch.ones(1, 2)],
        "P_inj": [torch.ones(1, 2)],
    }


def inspect(chunk):
    actual = installed_inspect(chunk, "chunk", count=1, grid=(2, 2, 2, 3))
    assert actual == inspect_chunk(chunk, "chunk", count=1, grid=(2, 2, 2, 3))
    return actual


def test_identity_and_no_renormalization(chunk):
    before = {key: value.clone() for key, value in chunk.items() if isinstance(value, torch.Tensor)}
    result = inspect(chunk)
    assert result[0]["production_wells"] == result[0]["injection_wells"] == 1
    assert result == inspect(chunk)
    for key, value in before.items():
        assert torch.equal(value, chunk[key])
    chunk["global_params"][0, 0] = 1
    assert result[0]["input_sha256"] != inspect(chunk)[0]["input_sha256"]


@pytest.mark.parametrize(
    "error", ["missing", "shape", "nan", "well_count", "well_time", "well_marker"]
)
def test_reject_invalid_data(chunk, error):
    if error == "missing":
        del chunk["temp"]
    elif error == "shape":
        chunk["pres"] = chunk["pres"][..., 0]
    elif error == "nan":
        chunk["global_params"][0, 0] = float("nan")
    elif error == "well_count":
        chunk["P_inj"] = [torch.ones(2, 2)]
    elif error == "well_time":
        chunk["spatial_params"][0, 0, 0, 0, 1, 2] = 0
    elif error == "well_marker":
        chunk["spatial_params"][0, 0, 0, 0, :, 2] = 2
    with pytest.raises(ValueError):
        inspect(chunk)
