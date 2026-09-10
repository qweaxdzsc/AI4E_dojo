"""组件布局与最小模型协议验收，不替代真实网络前向。"""

import pytest
import torch

from ai4e_core.abilities.modeling.requirements import validate_inputs
from ai4e_core.abilities.training.batch import concatenate_geometry, stack
from ai4e_spec.components.model import ModelRequirements


def test_sparse_offsets_and_dense_failure():
    batch = concatenate_geometry(
        [torch.zeros(3, 3), torch.zeros(5, 3)], [torch.tensor([0, 2]), torch.tensor([1, 4])]
    )
    assert batch["indices"].tolist() == [0, 2, 4, 7]
    assert batch["batch"].tolist() == [0, 0, 0, 1, 1, 1, 1, 1]
    with pytest.raises(ValueError):
        stack([torch.zeros(2, 3), torch.zeros(3, 3)])


def test_model_requirements():
    requirements = ModelRequirements(("positions",), 1)
    validate_inputs(requirements, {"positions": None}, 1)
    with pytest.raises(ValueError):
        validate_inputs(requirements, {"positions": None, "target": None}, 1)
    with pytest.raises(ValueError):
        validate_inputs(requirements, {"positions": None}, 2)


@pytest.mark.parametrize("bad", ["batch", "volume_batch", "rank", "indices", "extra", "missing"])
def test_real_component_rejects_bad_inputs_before_forward(bad):
    from ai4e_contrib.ability.model.abupt.model import predict
    from tests.integration.test_abupt_multidomain import inputs as make_inputs
    from tests.integration.test_abupt_multidomain import make_model

    model = make_model()
    inputs = make_inputs()
    if bad == "batch":
        inputs["domain_anchor_positions"]["surface"] = torch.zeros(2, 2, 3)
    elif bad == "volume_batch":
        inputs["domain_anchor_positions"]["volume"] = torch.zeros(2, 3, 3)
    elif bad == "rank":
        inputs["domain_anchor_positions"]["surface"] = torch.zeros(2, 3)
    elif bad == "indices":
        inputs["geometry_supernode_idx"] = torch.tensor([100])
    elif bad == "extra":
        inputs["target"] = torch.zeros(1)
    else:
        del inputs["geometry_position"]

    def never(**kwargs):
        pytest.fail("非法输入不应进入前向")

    with pytest.raises(ValueError):
        predict(model, inputs)


def test_contribution_batch_keeps_targets_outside_inputs():
    from ai4e_contrib.ability.model.abupt.batch import collate
    from ai4e_contrib.ability.model.abupt.model import INPUTS

    samples = [
        {
            "inputs": {
                "geometry_position": torch.zeros(n, 3),
                "geometry_supernode_idx": torch.tensor([0, n - 1]),
                "domain_anchor_positions": {
                    "surface": torch.zeros(2, 3),
                    "volume": torch.zeros(3, 3),
                },
            },
            "targets": {"surface_pressure_target": torch.ones(2, 1)},
            "metadata": {"sample": str(n)},
        }
        for n in [3, 5]
    ]
    batch = collate(samples)
    assert set(batch["inputs"]) == set(INPUTS)
    assert batch["inputs"]["geometry_supernode_idx"].tolist() == [0, 2, 3, 7]
    assert batch["targets"]["surface_pressure_target"].shape == (2, 2, 1)
