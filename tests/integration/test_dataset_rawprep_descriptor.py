"""A1/A2：数据集声明与默认配置同源，无数据绑定也能读取。"""

from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from ai4e_contrib.application.datasets import nasa_crm, shapenet_car
from ai4e_core.applications.aero_cfd.rawprep.descriptor import (
    merge_defaults,
    resolve_rawprep,
    validate_rawprep,
)

_SOURCE_DESCRIPTOR = (
    Path(__file__).resolve().parents[2]
    / "packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py"
)
_SPEC = spec_from_file_location("rawprep_descriptor_source", _SOURCE_DESCRIPTOR)
_SOURCE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SOURCE)


@pytest.mark.parametrize("component", [shapenet_car, nasa_crm])
def test_description_without_input(component):
    profile = component.describe_rawprep()
    assert profile["outputs"] and profile["binding"]["slots"]
    if component is shapenet_car:
        manifest = Path(component.__file__).with_name("manifest.yaml")
        source_profile = _SOURCE.load_description(manifest)
        assert source_profile["source_files"] == {
            "surface": "quadpress_smpl.vtk",
            "volume": "hexvelo_smpl.vtk",
        }
        pressure = next(
            item for item in source_profile["outputs"] if item["name"] == "surface_pressure"
        )
        assert pressure["filename"] == "quadpress_smpl.vtk"
        assert pressure["raw_field"] == "surface/point/point_scalars"
        if "source_files" in profile:
            assert profile["source_files"] == source_profile["source_files"]
            assert next(item["filename"] for item in profile["outputs"] if item["name"] == "surface_pressure") == "quadpress_smpl.vtk"
    config = resolve_rawprep({"components": {"dataset": component.__name__}, "rawprep": {}})
    assert config["rawprep"] == profile["defaults"]
    validate_rawprep(config["rawprep"], profile)
    changed = deepcopy(config)
    changed["rawprep"]["geometry"] = []
    changed["rawprep"]["filters"] = {}
    assert resolve_rawprep(changed)["rawprep"]["geometry"] == []
    assert resolve_rawprep(changed)["rawprep"]["filters"] == {}


def test_legacy_volume_normals_promoted_from_nearest_vertex():
    profile = shapenet_car.describe_rawprep()
    raw = deepcopy(profile["defaults"])
    raw["geometry"] = ["nearest_vertex", "surface_normals", "exterior_mask"]
    cfg = resolve_rawprep({"components": {"dataset": shapenet_car.__name__}, "rawprep": raw})
    assert "volume_normals" in cfg["rawprep"]["geometry"]
    validate_rawprep(cfg["rawprep"], profile)


def test_explicit_empty_and_false_not_replaced():
    assert merge_defaults({"x": [1], "y": {"z": 1}, "v": True}, {"x": [], "y": {}, "v": False}) == {
        "x": [],
        "y": {},
        "v": False,
    }


def test_user_formats_do_not_inherit_default_format():
    profile = shapenet_car.describe_rawprep()
    assert "format" not in profile["defaults"]
    assert profile["defaults"]["formats"] == ["pt"]
    cfg = resolve_rawprep(
        {"components": {"dataset": shapenet_car.__name__}, "rawprep": {"formats": ["pt", "zarr"]}},
        validate=True,
    )
    assert cfg["rawprep"]["formats"] == ["pt", "zarr"]
    assert "format" not in cfg["rawprep"]
    only_old = resolve_rawprep(
        {"components": {"dataset": shapenet_car.__name__}, "rawprep": {"format": "zarr"}},
        validate=True,
    )
    assert only_old["rawprep"]["format"] == "zarr"
    assert "formats" not in only_old["rawprep"]
    overwritten = resolve_rawprep(
        {
            "components": {"dataset": shapenet_car.__name__},
            "rawprep": {"format": "pt", "formats": ["zarr"]},
        },
        validate=True,
    )
    assert overwritten["rawprep"]["formats"] == ["zarr"]
    assert "format" not in overwritten["rawprep"]


def test_empty_formats_rejected_and_dual_formats_recorded():
    profile = shapenet_car.describe_rawprep()
    raw = {**deepcopy(profile["defaults"]), "formats": []}
    with pytest.raises(ValueError, match="formats"):
        validate_rawprep(raw, profile)
    both = {**deepcopy(profile["defaults"]), "formats": ["pt", "zarr"]}
    both.pop("format", None)
    validate_rawprep(both, profile)
    from ai4e_core.applications.aero_cfd.rawprep.dataset import encode
    from ai4e_core.applications.base.dataset import Dataset

    encoded = encode(
        Dataset(
            root=Path("."),
            samples=("a",),
            partitions={"train": ("a",)},
            metadata={},
            options={"output": {"filemap": {"surface_pressure": "surface_pressure.pt"}}},
        ),
        formats=["pt", "zarr"],
    )
    maps = encoded.options["output"]["format_filemaps"]
    assert maps["pt"]["surface_pressure"].endswith(".pt")
    assert maps["zarr"]["surface_pressure"].endswith(".zarr")
    assert encoded.options["output"]["filemap"]["surface_pressure"].endswith(".pt")


def test_saved_task_keeps_case_defaults_and_empty_values(tmp_path):
    from pathlib import Path

    import ai4e_task as task

    project = tmp_path / "project"
    task.create_project(project)
    recipe = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
    record = task.new_task(
        project,
        "case",
        source=recipe,
        configuration={
            "output_format": "pt",
            "rawprep": {"vtkhdf": True, "format": "${output_format}"},
        },
    )
    first = task.describe_rawprep(project, record["id"])
    assert first["profile"]["defaults"]["vtkhdf"] is True
    cfg = task.read_configuration(project, record["id"])
    assert cfg["config"]["rawprep"]["format"] == "${output_format}"
    raw = {**first["rawprep"], "vtkhdf": False, "geometry": [], "filters": {}}
    task.save_configuration(
        project,
        record["id"],
        {"rawprep": raw},
        revision=cfg["revision"],
        replace_sections=("rawprep",),
    )
    actual = task.describe_rawprep(project, record["id"])
    assert actual["rawprep"]["geometry"] == [] and actual["rawprep"]["filters"] == {}
    assert actual["profile"]["defaults"]["vtkhdf"] is True
    assert len(task.get_lineage(project)) == 1
