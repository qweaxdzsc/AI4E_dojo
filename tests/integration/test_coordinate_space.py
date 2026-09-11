"""坐标声明是显式来源意图，差值只继承一致声明。"""

import json
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.postproc.coordinate_space import coordinate_space
from ai4e_core.abilities.postproc.difference import compare_files


@pytest.mark.parametrize(
    "bad", [{}, {"id": "frame"}, {"id": "f", "unit": ""}, {"id": "f", "unit": "m", "guess": True}]
)
def test_coordinate_space_rejects_partial(bad):
    with pytest.raises(ValueError, match="coordinate_space"):
        coordinate_space(bad)


def test_difference_propagates_explicit_coordinate_space(tmp_path):
    records = []
    for name in ("left", "right"):
        path = tmp_path / (name + ".pt")
        meta = tmp_path / (name + ".json")
        torch.save(
            {"values": torch.ones(2, 1), "ids": torch.arange(2), "coordinates": torch.zeros(2, 3)},
            path,
        )
        meta.write_text(
            json.dumps(
                {
                    "unit": "Pa",
                    "entity_set": "mesh",
                    "topology": "same",
                    "association": "point",
                    "coordinate_space": {"id": "declared-frame", "unit": "m"},
                }
            )
        )
        records.append({"path": str(path), "metadata_path": str(meta)})
    output = tmp_path / "output"
    output.mkdir()
    result = compare_files(records, output, {})
    assert json.loads(Path(result["metadata_path"]).read_text())["coordinate_space"] == {
        "id": "declared-frame",
        "unit": "m",
    }
    meta = tmp_path / "right.json"
    data = json.loads(meta.read_text())
    data["coordinate_space"]["unit"] = "mm"
    meta.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="coordinate_space"):
        compare_files(records, output, {})
    del data["coordinate_space"]
    meta.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="coordinate_space"):
        compare_files(records, output, {})
    assert coordinate_space(None) is None


def test_public_configuration_rejects_bad_coordinate_declaration():
    from ai4e_core.applications.aero_cfd.inspection import normalize_config

    with pytest.raises(ValueError, match="coordinate_space"):
        normalize_config({"dataset": {"coordinate_space": {"id": "missing-unit"}}})
