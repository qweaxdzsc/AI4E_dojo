"""真实 Noether 参考生成的输入张量与新准备链对齐。"""

import hashlib
import json
from pathlib import Path

import pytest
import torch

from ai4e_contrib.ability.model.abupt.batch import collate
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization

ROOT = Path(__file__).parents[1] / "fixtures/abupt_inputs"


def case():
    ref = torch.load(ROOT / "reference.pt", weights_only=True)
    data = {
        "position_dim": 3,
        "domains": {
            "surface": {"output_dims": {"pressure": 1}, "feature_dim": {"normal": 3}},
            "volume": {"output_dims": {"velocity": 3}, "feature_dim": {"sdf": 1}},
        },
        "conditioning_dims": {"design": 2},
    }
    bindings = {
        "geometry_field": "wall_pos",
        "domains": {
            "surface": {
                "position": "wall_pos",
                "features": {"normal": "normal"},
                "targets": {"pressure": "pressure"},
                "query_targets": True,
            },
            "volume": {
                "position": "fluid_pos",
                "features": {"sdf": "sdf"},
                "targets": {"velocity": "velocity"},
                "query_targets": True,
            },
        },
        "conditioning": {"design": {"constant": [2.0, 4.0], "normalization": "design"}},
    }
    fields = {
        n: {
            "method": "zscore",
            "parameters": {"mean": m, "std": s},
            "scope": "condition" if n == "design" else "point",
        }
        for n, (m, s) in ref["parameters"].items()
    }
    fields.update(
        {
            n: {
                "method": "coordinate",
                "parameters": {"minimum": [0.0, 0.0, 0.0], "maximum": [1.0, 1.0, 1.0]},
            }
            for n in ["wall_pos", "fluid_pos"]
        }
    )
    fields["normal"] = {"method": "identity", "parameters": {}}
    normalization = Normalization({"version": 1, "fields": fields})
    sampling = {
        "seed": 42,
        "geometry": {"method": "uniform", "max_points": 6},
        "supernodes": {"method": "uniform", "num_points": 3},
        "domains": {
            d: {
                "anchor": {"num_points": len(ref["indices"][d + "_anchor"])},
                "query": {"num_points": 2},
            }
            for d in data["domains"]
        },
    }
    return ref, data, bindings, normalization, sampling


def test_reference_values_and_field_binding():
    ref, data, bindings, norm, sampling = case()
    metadata = json.loads((ROOT / "source.json").read_text())
    assert (
        metadata["fixture_sha256"]
        == hashlib.sha256((ROOT / "reference.pt").read_bytes()).hexdigest()
    )
    physical = {k: v for k, v in ref["physical"].items() if k != "design"}
    normalized = norm.apply(physical)
    for name, value in normalized.items():
        torch.testing.assert_close(value, ref["normalized"][name], rtol=1e-6, atol=1e-6)
    sample = prepare_inputs(
        normalized,
        sampling,
        sample="car",
        data_specs=data,
        bindings=bindings,
        normalization=norm,
        indices=ref["indices"],
    )
    batch = collate([sample])

    def compare(a, b):
        if isinstance(a, dict):
            assert set(a) == set(b)
            for k in a:
                compare(a[k], b[k])
        else:
            torch.testing.assert_close(a, b, rtol=1e-6, atol=1e-6)

    compare(batch["inputs"], ref["inputs"])
    for name, value in batch["targets"].items():
        assert not any(name in d for d in batch["inputs"] if isinstance(d, dict))
    torch.testing.assert_close(
        norm.inverse("pressure", normalized["pressure"]), physical["pressure"]
    )


@pytest.mark.parametrize("query_domains", [[], ["surface"], ["volume"], ["surface", "volume"]])
def test_query_subsets_and_condition_files(tmp_path, query_domains):
    ref, data, bindings, norm, sampling = case()
    path = tmp_path / "conditions.json"
    path.write_text(json.dumps({"car": {"design": [2.0, 4.0]}}))
    bindings["conditioning"]["design"] = {"path": str(path), "normalization": "design"}
    for domain in sampling["domains"]:
        if domain not in query_domains:
            sampling["domains"][domain]["query"]["num_points"] = 0
    sample = prepare_inputs(
        norm.apply({k: v for k, v in ref["physical"].items() if k != "design"}),
        sampling,
        sample="car",
        data_specs=data,
        bindings=bindings,
        normalization=norm,
    )
    assert set(sample["inputs"].get("domain_query_positions", {})) == set(query_domains)
    with pytest.raises(ValueError, match="条件缺样本"):
        prepare_inputs(
            norm.apply(ref["physical"]),
            sampling,
            sample="missing",
            data_specs=data,
            bindings=bindings,
            normalization=norm,
        )


def test_explicit_geometry_condition_and_transform_coverage():
    ref, data, bindings, norm, sampling = case()
    bindings["geometry_conditioning"] = {
        "shape": {"constant": [2.0, 4.0], "normalization": "design"}
    }
    normalized = norm.apply({k: v for k, v in ref["physical"].items() if k != "design"})
    sample = prepare_inputs(
        normalized,
        sampling,
        sample="car",
        data_specs=data,
        bindings=bindings,
        normalization=norm,
        geometry_conditioning_dims={"shape": 2},
    )
    torch.testing.assert_close(
        sample["inputs"]["geometry_conditioning_inputs"]["shape"], torch.tensor([1.0, 2.0])
    )
    del norm.transforms["normal"]
    with pytest.raises(ValueError, match="声明变换"):
        prepare_inputs(
            normalized,
            sampling,
            sample="car",
            data_specs=data,
            bindings=bindings,
            normalization=norm,
            geometry_conditioning_dims={"shape": 2},
        )


def test_fixed_indices_and_target_identity():
    ref, data, bindings, norm, sampling = case()
    normalized = norm.apply({k: v for k, v in ref["physical"].items() if k != "design"})
    sample = prepare_inputs(
        normalized,
        sampling,
        sample="car",
        data_specs=data,
        bindings=bindings,
        normalization=norm,
        indices=ref["indices"],
    )
    for d, field in [("surface", "pressure"), ("volume", "velocity")]:
        for kind in ["anchor", "query"]:
            rows = sample["metadata"]["domain_rows"][d][kind]
            assert rows.tolist() == ref["indices"][d + "_" + kind]
            target = ("query_" if kind == "query" else "") + d + "_" + field + "_target"
            torch.testing.assert_close(sample["targets"][target], normalized[field][rows])
    bad = {**ref["indices"], "geometry": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]}
    with pytest.raises(ValueError, match="整数"):
        prepare_inputs(
            normalized,
            sampling,
            sample="car",
            data_specs=data,
            bindings=bindings,
            normalization=norm,
            indices=bad,
        )
