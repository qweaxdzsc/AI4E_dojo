"""有序命名域、输出切片与错误输入门禁。"""

import copy

import pytest
import torch

from ai4e_contrib.ability.model.abupt.domains import DomainLayout
from tests.integration.test_abupt_multidomain import inputs, make_model, specs


def test_order_changes_signature_and_output_slices():
    data = specs(("solid",))
    data["domains"]["solid"]["output_dims"] = {"temperature": 1, "velocity": 3}
    first = DomainLayout(data)
    changed = copy.deepcopy(data)
    changed["domains"]["solid"]["output_dims"] = {"velocity": 3, "temperature": 1}
    assert first.signature != DomainLayout(changed).signature
    result = first.split("solid", torch.tensor([[[1.0, 2.0, 3.0, 4.0]]]))
    assert result["solid_temperature"].item() == 1
    assert result["solid_velocity"].tolist() == [[[2.0, 3.0, 4.0]]]


@pytest.mark.parametrize(
    "defect", ["unknown", "missing", "width", "feature", "query_only", "negative_index"]
)
def test_invalid_input_rejected(defect):
    data = specs(features=True)
    model = make_model(data)
    batch = inputs(data)
    if defect == "unknown":
        batch["domain_anchor_positions"]["unknown"] = torch.rand(1, 3, 3)
    if defect == "missing":
        del batch["domain_anchor_positions"]["surface"]
    if defect == "width":
        batch["domain_anchor_features"]["surface"] = torch.rand(1, 3, 4)
    if defect == "feature":
        del batch["domain_anchor_features"]
    if defect == "query_only":
        del batch["domain_anchor_positions"]
    if defect == "negative_index":
        batch["geometry_supernode_idx"][0] = -1
    with pytest.raises(ValueError):
        model(**batch)


def test_name_collision_and_single_cross_rejected():
    with pytest.raises(ValueError, match="冲突"):
        DomainLayout(
            {
                "position_dim": 3,
                "domains": {"a": {"output_dims": {"b_c": 1}}, "a_b": {"output_dims": {"c": 1}}},
            }
        )
    from ai4e_contrib.ability.model.abupt.model import construct

    with pytest.raises(ValueError, match="两个域"):
        construct(data_specs=specs(("only",)), blocks="pc")


def test_default_scale_constructs_only():
    from pathlib import Path

    from omegaconf import OmegaConf

    from ai4e_contrib.ability.model.abupt.model import construct

    cfg = OmegaConf.to_container(
        OmegaConf.load(Path(__file__).parents[2] / "recipes/aero_cfd/config.yaml"), resolve=True
    )
    model = construct(data_specs=cfg["model"]["data_specs"], **cfg["model"]["parameters"])
    assert model.readouts["surface"].out_features == 1
    assert model.readouts["volume"].out_features == 3
