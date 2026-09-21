"""多域坐标统计、身份与无目标泄漏的点场准备。"""

import hashlib
from copy import deepcopy

import pytest
import torch

from ai4e_core.abilities.data.stats.physical import freeze
from ai4e_core.abilities.transform.point_features import concatenate_fields


def test_shared_coordinates_fit_training_only():
    class View:
        def __init__(self):
            self.partitions = {"train": ["a"], "test": ["b"]}

        def describe(self):
            return {}

        def read(self, split, index):
            assert split == "train"
            return {
                "fields": {
                    "surface": torch.tensor([[0.0, 1.0, 2.0]]),
                    "volume": torch.tensor([[-4.0, 1.0, 8.0]]),
                }
            }

    spec = {"method": "coordinate", "coordinate_group": "space", "scale": 1}
    norm = freeze(
        View(),
        {
            "normalization": {
                "execute": True,
                "fields": {"surface": dict(spec), "volume": dict(spec)},
            }
        },
    )
    p = torch.tensor([[1.0, 2.0, 3.0]])
    values = norm.apply({"surface": p, "volume": p})
    torch.testing.assert_close(values["surface"], values["volume"], atol=0, rtol=0)
    assert norm.record["fields"]["surface"]["parameters"]["minimum"] == [-4.0]


def test_feature_identity_and_order():
    fields = {"a": torch.ones(3, 1), "b": torch.zeros(3, 2)}
    result = concatenate_fields(fields, ["b", "a"], ids=torch.tensor([9, 4, 2]))
    assert torch.equal(result[:, -1], torch.ones(3))
    with pytest.raises(ValueError, match="重复"):
        concatenate_fields(fields, ["a"], ids=torch.tensor([9, 9, 2]))


@pytest.mark.parametrize("dataset", ["shapenet_car", "nasa_crm"])
def test_real_layout_prepares_without_topology_or_targets_in_inputs(tmp_path, dataset):
    from ai4e_contrib.application.aero_cfd.configuration import (
        application_parameters,
        load_components,
        load_configuration,
    )
    from ai4e_core.applications.aero_cfd.trainprep import physical
    from tests.geotransolver_aero_assets import setup_case

    case, platform, _ = setup_case(tmp_path, dataset)
    original = {
        p: hashlib.sha256(p.read_bytes()).hexdigest() for p in platform.rglob("*") if p.is_file()
    }
    cfg = load_configuration(case / "config.yaml")
    config = application_parameters(cfg)
    components = load_components(cfg)
    data = physical.open_dataset(config, components.dataset, components.model, version=2)
    physical.bind_fields(data)
    physical.freeze_normalization(data)
    sample = data.view.read("train", 0)
    a = components.model.prepare_sample(sample, config, data.normalization)
    changed = deepcopy(sample)
    for binding in config["trainprep"]["domains"].values():
        for name in binding["targets"].values():
            changed["fields"][name] += 20
    b = components.model.prepare_sample(changed, config, data.normalization)
    for x, y in zip(a["inputs"]["local_embedding"], b["inputs"]["local_embedding"], strict=True):
        torch.testing.assert_close(x, y, atol=0, rtol=0)
    assert a["inputs"]["local_embedding"][0].shape[-1] == 6
    if dataset == "nasa_crm":
        assert a["inputs"]["global_embedding"].shape == (1, 1, 6)

    assert original == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in original}
    invalid = deepcopy(config)
    domain = next(iter(invalid["model"]["data_specs"]["domains"].values()))
    domain["feature_dim"]["normals"] = 2
    with pytest.raises(ValueError, match="宽度"):
        components.model.prepare_sample(sample, invalid, data.normalization)
