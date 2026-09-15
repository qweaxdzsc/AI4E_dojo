"""选定原Neumann/Advection的来源、单步、数据和迁移门禁。"""

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.model.pibsnet import component, source_cases
from ai4e_contrib.application.datasets.parametric import component as generator
from ai4e_core.applications.parametric_pde.model import build_model
from tests.integration.test_pibsnet_training import configuration


def test_parameter_derivatives_are_explicit_and_old_data_rejected():
    cfg = configuration.defaults("neumann_diffusion")
    cfg["model"].update(control_points=[6, 6], degree=3, hidden_dim=8)
    sample = generator("neumann_diffusion").make_sample(
        np.random.RandomState(42), {"nx": 9, "nt": 7}, index=0, split="train"
    )
    sample.update(id="train-0", case="neumann_diffusion")
    model = build_model(cfg, component)
    prepared = component.prepare(sample, cfg)
    values = component.predictions(model, prepared, cfg)
    assert "parameter_x" in values and "u_x" not in values
    assert torch.count_nonzero(prepared["grid_bases"][1][1][-1]) == 0
    sample.pop("numerical_protocol")
    with pytest.raises(ValueError, match="重新独立生成"):
        component.prepare(sample, cfg)


def test_advection_first_row_is_source_interpolation():
    cfg = configuration.defaults("advection")
    cfg["train"]["device"] = "cpu"
    cfg["model"].update(control_points=[8, 8], degree=3, hidden_dim=8)
    sample = generator("advection").make_sample(
        np.random.RandomState(42), {"nx": 9, "nt": 7}, index=0, split="train"
    )
    sample.update(id="train-0", case="advection")
    model = build_model(cfg, component)
    batch = component.prepare(sample, cfg)
    output = component.predictions(model, batch, cfg)["u"]
    loss = component.step(model, batch, cfg)["loss"]
    loss.backward()
    assert torch.count_nonzero(model.fc3.weight.grad[:8]) == 0
    assert not torch.equal(output[0], sample["u"][0])
    # 值与原插值控制行一致；不再宣称解析初值逐点严格满足。
    row = torch.tensor(
        np.interp(np.linspace(0, 8, 8), np.arange(9), sample["u"][0].numpy()), dtype=torch.float32
    )
    expected = torch.zeros(8, 8)
    expected[0] = row
    torch.testing.assert_close(
        output[0],
        (batch["grid_bases"][0][0] @ expected @ batch["grid_bases"][1][0].T)[0],
        rtol=0,
        atol=0,
    )


def test_neumann_original_initialization_consumption():
    torch.manual_seed(42)
    source_cases.consume_neumann_initialization()
    expected = source_cases.NeumannNet(40, 40, 128)
    cfg = configuration.defaults("neumann_diffusion")
    cfg["train"]["device"] = "cpu"
    actual = build_model(cfg, component)
    for key, value in expected.state_dict().items():
        torch.testing.assert_close(value, actual.state_dict()[key], rtol=0, atol=0)


def test_all_source_configuration_entrypoints(tmp_path):
    import yaml

    cfg = {
        "case": "advection",
        "model": {
            "sampling": {"supervised": {"method": "random_without_replacement", "num_points": 12}}
        },
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    loaded = configuration.load_configuration(path, ["train.device=cpu"])
    assert loaded["model"]["sampling"]["supervised"]["num_points"] == 12
    assert loaded["train"]["device"] == "cpu"
    loaded["model"]["hard_initial"] = False
    with pytest.raises(ValueError, match="插值"):
        component.build(loaded)


@pytest.mark.parametrize("case", ["neumann_diffusion", "advection"])
def test_full_source_migration_artifacts(case, monkeypatch):
    import os
    from pathlib import Path

    root = os.environ.get("DOJO_SOURCE_ALIGNMENT_ROOT")
    if not root:
        pytest.skip("需要实际完整预算产物；跳过不代表精度验收")
    monkeypatch.syspath_prepend(
        str(Path(__file__).resolve().parents[2] / "tools/verification/pibsnet")
    )
    from source_dojo import report

    result = report(Path(root) / case)
    assert result["weights_history_predictions_exact"]
    assert np.isfinite(result["mean_relative_l2"])
