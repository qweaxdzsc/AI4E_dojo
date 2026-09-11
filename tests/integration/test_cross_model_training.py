"""真实模型算子的小规模跨字段测试，不代替正式网络实验。"""

import pytest
import torch

from ai4e_contrib.ability.model.transolver3 import component as transolver
from ai4e_core.abilities.transform.normalization import Normalization


@pytest.mark.parametrize("width,out", [(3, 3), (6, 1), (12, 4)])
def test_transolver_configurable_dimensions_update(width, out):
    torch.manual_seed(2)
    model = transolver.construct(
        space_dim=width,
        fun_dim=0,
        out_dim=out,
        n_hidden=16,
        n_layers=2,
        n_head=4,
        slice_num=4,
        mlp_ratio=2,
        unified_pos=False,
        gradient_checkpointing=True,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
    before = next(model.parameters()).detach().clone()
    prediction = transolver.predict(model, {"features": torch.randn(1, 20, width)})["fields"]
    assert prediction.shape == (1, 20, out)
    prediction.square().mean().backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    optimizer.step()
    assert not torch.equal(before, next(model.parameters()))
    with pytest.raises(ValueError, match=str(width)):
        transolver.predict(model, {"features": torch.ones(1, 20, width + 1)})


def test_abupt_sample_condition_field(tmp_path):
    from pathlib import Path

    import yaml

    from ai4e_contrib.ability.model.abupt import component

    config = yaml.safe_load(
        (
            Path(__file__).resolve().parents[2] / "examples/aero_cfd/nasa_crm_abupt/config.yaml"
        ).read_text()
    )
    config["sampling"] = config["model"].pop("sampling")
    config["normalization"] = config["trainprep"].pop("normalization")
    config["sampling"]["geometry"]["max_points"] = 12
    config["sampling"]["supernodes"]["num_points"] = 4
    config["sampling"]["domains"]["surface"]["anchor"]["num_points"] = 8
    config["model"]["parameters"].update(
        dim=24, geometry_depth=1, num_heads=3, blocks="ps", num_domain_decoder_blocks={"surface": 1}
    )
    norm = Normalization(
        {
            "version": 2,
            "fields": {
                name: {
                    "method": "identity",
                    "parameters": {},
                    "scope": "condition" if name == "conditions" else "point",
                }
                for name in [
                    "surface_position",
                    "surface_normals",
                    "surface_cp",
                    "surface_cf",
                    "conditions",
                ]
            },
        }
    )
    fields = {
        "surface_position": torch.rand(20, 3),
        "surface_normals": torch.randn(20, 3),
        "surface_cp": torch.randn(20, 1),
        "surface_cf": torch.randn(20, 3),
    }
    sample = {
        "fields": fields,
        "conditions": {"conditions": torch.randn(1, 6)},
        "identity": {"sample": "wing", "index": 0},
    }
    batch = component.prepare_sample(sample, config, norm)
    assert batch["inputs"]["conditioning_inputs"]["conditions"].shape == (1, 6)
    model = component.construct(**component.training_parameters(config))
    result = component.loss(model, batch, config)
    result["loss"].backward()
    assert torch.isfinite(result["loss"])


def test_prepared_dataset_preserves_error_identity():
    from types import SimpleNamespace

    from ai4e_core.applications.aero_cfd.workflow import PreparedSamples

    def fail(*args):
        raise ValueError("source missing")

    data = PreparedSamples(
        SimpleNamespace(partitions={"train": ["wing"]}, read=fail),
        SimpleNamespace(prepare_sample=fail),
        {},
        None,
    )
    with pytest.raises(ValueError) as caught:
        data[0]
    assert caught.value.dojo_context["samples"][0]["sample_id"] == "wing"
