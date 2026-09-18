"""锁定官方实际归一化器生成的数据，防止等价公式改变训练输入。"""

import json
from pathlib import Path

import torch

from ai4e_core.abilities.transform.normalization import Normalization
from ai4e_core.abilities.transform.standardization import Standardization


def test_actual_normalizer_float32_fixture():
    fixture = json.loads(
        (Path(__file__).parents[1] / "fixtures/abupt_inputs/normalization.json").read_text()
    )
    standard = fixture["standardization"]
    standardizer = Standardization(tuple(standard["mean"]), tuple(standard["std"]))
    coordinate = Normalization(
        {
            "version": 2,
            "fields": {
                "x": {
                    "method": "coordinate",
                    "parameters": {"minimum": [-4.5], "maximum": [6.0]},
                    "scale": 1000,
                }
            },
        }
    ).transforms["x"]
    for transform, values in [(standardizer, standard), (coordinate, fixture["coordinate"])]:
        actual = transform.apply(torch.tensor(values["input"]))
        torch.testing.assert_close(actual, torch.tensor(values["output"]), rtol=0, atol=0)
        torch.testing.assert_close(
            transform.inverse(actual), torch.tensor(values["inverse"]), rtol=0, atol=0
        )


def test_old_frozen_arithmetic_remains_explicit():
    from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization

    record = {
        "version": 1,
        "fields": {"x": {"method": "zscore", "parameters": {"mean": [0.0], "std": [1.361689]}}},
    }
    x = torch.tensor([[1.23]])
    torch.testing.assert_close(
        Normalization(record).apply({"x": x})["x"], x / 1.361689, rtol=0, atol=0
    )
    record["version"] = 2
    torch.testing.assert_close(
        Normalization(record).apply({"x": x})["x"],
        x * torch.tensor(1.361689).reciprocal(),
        rtol=0,
        atol=0,
    )
