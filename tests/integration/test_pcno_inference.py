"""联合预测的真值隔离及无效权重门禁。"""

import json

import pytest
import torch

from ai4e_contrib.application.geothermal.pcno import inference
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.applications.geothermal.inference import predict_fields


def test_joint_fields_only_consume_network_predictions():
    class Network:
        def __init__(self, value):
            self.value = value

        def __call__(self, x, g):
            return torch.full(x.shape[:-1], self.value)

    x = torch.zeros(1, 2, 2, 5, 3, 14)
    g = torch.zeros(1, 4)
    fields = predict_fields(
        {"pres": Network(2.0), "temp": Network(3.0)},
        x,
        g,
        {"pres_mean": 10.0, "pres_std": 2.0, "temp_mean": 100.0, "temp_std": 5.0},
    )
    assert torch.all(fields["pres"] == 14) and torch.all(fields["temp"] == 115)
    with pytest.raises(ValueError, match="压力和温度"):
        predict_fields({"pres": Network(2.0)}, x, g, {"pres_mean": 10.0, "pres_std": 2.0})


def test_invalid_author_weights_cannot_be_sanitized_into_predictions(tmp_path, monkeypatch):
    monkeypatch.setattr(inference, "read_bundle", lambda *a, **k: {"sha256": {}})
    p = tmp_path / "bad.pt"
    torch.save({"model": {"weight": torch.tensor(float("nan"))}}, p)
    record = {
        "version": 1,
        "branches": {b: {"file": p.name, "sha256": digest(p)} for b in ["pres", "temp"]},
    }
    m = tmp_path / "checkpoints.json"
    m.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="非有限权重"):
        inference.load_networks(
            {}, "unused", m, lambda **k: pytest.fail("invalid weights reached constructor")
        )
