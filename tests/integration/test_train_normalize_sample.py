"""归一化与采样的数值、梯度、行对齐和随机流回归。"""

from functools import partial
from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs as prepare

_template = OmegaConf.to_container(
    OmegaConf.load(Path(__file__).parents[2] / "recipes/aero_cfd/config.yaml"), resolve=True
)
prepare_inputs = partial(
    prepare, data_specs=_template["model"]["data_specs"], bindings=_template["trainprep"]
)
from ai4e_core.abilities.sampling.points import point_indices
from ai4e_core.abilities.transform.coordinate_normalization import CoordinateNormalization
from ai4e_core.abilities.transform.standardization import Standardization


def test_transform_roundtrip_and_gradient():
    x = torch.tensor([[2.0, 4.0, 8.0]], requires_grad=True)
    transform = Standardization((1.0, 2.0, 3.0), (2.0, 4.0, 5.0))
    y = transform.apply(x)
    torch.testing.assert_close(y, torch.tensor([[0.5, 0.5, 1.0]]))
    torch.testing.assert_close(transform.inverse(y), x)
    y.sum().backward()
    torch.testing.assert_close(x.grad, torch.tensor([[0.5, 0.25, 0.2]]))
    coordinate = CoordinateNormalization((0.0,), (10.0,))
    torch.testing.assert_close(coordinate.inverse(coordinate.apply(x)), x)
    with pytest.raises(ValueError):
        Standardization((0.0,), (0.0,))
    with pytest.raises(ValueError):
        coordinate.apply(torch.tensor([[-1.0, 0.0, 0.0]]))


def test_sampling_alignment_independence_and_target_copy():
    position = torch.arange(60).reshape(20, 3).float()
    fields = {
        "surface_position": position,
        "surface_pressure": position[:, :1],
        "volume_position": position,
        "volume_velocity": position.clone(),
    }
    config = {
        "seed": 42,
        "geometry": {"method": "uniform", "max_points": 30},
        "supernodes": {"method": "uniform", "num_points": 4},
        "domains": {
            "surface": {"anchor": {"method": "uniform", "num_points": 5}},
            "volume": {"anchor": {"method": "uniform", "num_points": 5}},
        },
    }
    first = prepare_inputs(fields, config, sample="car", evaluation=True)
    again = prepare_inputs(fields, config, sample="car", epoch=9, evaluation=True)
    torch.testing.assert_close(
        first["metadata"]["domain_rows"]["surface"]["anchor"],
        again["metadata"]["domain_rows"]["surface"]["anchor"],
    )
    assert first["metadata"]["geometry_rows"].tolist() == list(range(20))
    selected = first["fields"]
    torch.testing.assert_close(
        selected["surface_pressure"], first["inputs"]["domain_anchor_positions"]["surface"][:, :1]
    )
    first["targets"]["surface_pressure_target"].zero_()
    assert selected["surface_pressure"].count_nonzero() > 0
    config["supernodes"]["num_points"] = 6
    changed = prepare_inputs(fields, config, sample="car", evaluation=True)
    torch.testing.assert_close(
        first["metadata"]["domain_rows"]["surface"]["anchor"],
        changed["metadata"]["domain_rows"]["surface"]["anchor"],
    )
    changed = prepare_inputs(fields, config, sample="car", epoch=1)
    assert not torch.equal(
        first["metadata"]["domain_rows"]["surface"]["anchor"],
        changed["metadata"]["domain_rows"]["surface"]["anchor"],
    )
    with pytest.raises(ValueError):
        point_indices(2, 3, seed=0, sample="car", operation="anchors")


@pytest.mark.parametrize(
    "mean,std", [([float("nan")], [1]), ([0], [float("inf")]), ([0], [-1]), ([0, 1], [1])]
)
def test_invalid_statistics_rejected(mean, std):
    with pytest.raises(ValueError):
        Standardization(tuple(mean), tuple(std))


def test_coordinate_tolerance_disable_and_gradient():
    transform = CoordinateNormalization((0.0,), (1.0,))
    x = torch.tensor([[-5e-10, 0.5, 1.0]], dtype=torch.float64, requires_grad=True)
    result = transform.apply(x)
    assert result[0, 0] < 0
    result.sum().backward()
    torch.testing.assert_close(x.grad, torch.full_like(x, 1000))
    unchecked = CoordinateNormalization((0.0,), (1.0,), check_range=False)
    assert unchecked.apply(torch.tensor([[2.0, 0.0, 0.0]]))[0, 0] == 2000
    with pytest.raises(ValueError):
        CoordinateNormalization((0.0,), (0.0,))
    with pytest.raises(ValueError):
        Standardization((0.0,), (1.0,)).apply(torch.ones(2, 3))


def test_uniform_sampling_has_no_replacement():
    ids = point_indices(100, 30, seed=42, sample="a", operation="geometry")
    assert len(ids.unique()) == 30
    assert ids.min() >= 0 and ids.max() < 100
