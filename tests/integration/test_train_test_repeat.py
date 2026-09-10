"""第 32 项：官方 test 重复评估长度为 1000 且独立采样。"""

from functools import partial
from pathlib import Path

import torch
from omegaconf import OmegaConf

from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs as prepare

_template = OmegaConf.to_container(
    OmegaConf.load(Path(__file__).parents[2] / "recipes/aero_cfd/config.yaml"), resolve=True
)
prepare_inputs = partial(
    prepare, data_specs=_template["model"]["data_specs"], bindings=_template["trainprep"]
)
from ai4e_core.abilities.data.source.split import load_split_lists
from ai4e_core.applications.aero_cfd.trainprep.dataset import repeated_samples

PARTITION = (
    Path(__file__).resolve().parents[2]
    / "packages/ai4e-contrib/application/datasets/shapenet_car/partition.yaml"
)


def test_official_test_repeat_length_and_independent_sampling():
    splits = load_split_lists(PARTITION)
    assert len(splits["test"]) == 100
    pairs = list(repeated_samples(splits["test"], 10))
    assert len(pairs) == 1000
    assert pairs[0][2] == 0 and pairs[100][2] == 1
    fields = {
        "surface_position": torch.arange(32).reshape(32, 1).expand(32, 3).float(),
        "surface_pressure": torch.arange(32).reshape(32, 1).float(),
        "surface_normals": torch.ones(32, 3),
        "volume_position": torch.arange(16).reshape(16, 1).expand(16, 3).float(),
        "volume_velocity": torch.ones(16, 3),
        "volume_sdf": torch.zeros(16, 1),
        "volume_normals": torch.ones(16, 3),
    }
    config = {
        "seed": 42,
        "train_randomness": "per_epoch",
        "evaluation_randomness": "fixed",
        "geometry": {
            "method": "uniform",
            "max_points": 16,
            "replacement": False,
            "keep_order_when_all": True,
        },
        "supernodes": {"method": "uniform", "num_points": 4, "insufficient": "error"},
        "domains": {
            "surface": {"anchor": {"method": "uniform", "num_points": 8, "insufficient": "error"}},
            "volume": {"anchor": {"method": "uniform", "num_points": 4, "insufficient": "error"}},
        },
    }
    first = prepare_inputs(
        fields, {**config, "seed": 42}, sample=splits["test"][0], evaluation=True
    )
    second = prepare_inputs(
        fields, {**config, "seed": 43}, sample=splits["test"][0], evaluation=True
    )
    fixed = prepare_inputs(fields, config, sample=splits["test"][0], evaluation=True)
    assert not torch.equal(
        first["metadata"]["domain_rows"]["surface"]["anchor"],
        second["metadata"]["domain_rows"]["surface"]["anchor"],
    )
    assert torch.equal(
        first["metadata"]["domain_rows"]["surface"]["anchor"],
        fixed["metadata"]["domain_rows"]["surface"]["anchor"],
    )
