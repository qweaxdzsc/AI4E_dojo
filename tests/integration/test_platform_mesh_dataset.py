"""平台 PT、VTKHDF、资产解析与内容摘要契约。"""

import json
from pathlib import Path

import numpy as np
import pytest
import torch
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf
from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.data.source.physical import PhysicalView
from ai4e_core.applications.aero_cfd.rawprep.physical import SavePhysical


def platform_dataset(tmp_path: Path) -> Path:
    """创建一个带规范网格资产的最小平台数据集。"""
    sample = tmp_path / "train" / "sample"
    sample.mkdir(parents=True)
    points = torch.tensor([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
    pressure = torch.arange(4, dtype=torch.float32)[:, None]
    torch.save(points, sample / "position.pt")
    torch.save(pressure, sample / "pressure.pt")
    mesh = vtk.vtkPolyData()
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(points.numpy(), deep=True))
    mesh.SetPoints(vtk_points)
    cells = vtk.vtkCellArray()
    cells.SetCells(1, numpy_to_vtkIdTypeArray(np.array([4, 0, 1, 2, 3]), deep=True))
    mesh.SetPolys(cells)
    write_vtkhdf(sample / "surface.vtkhdf", mesh)
    (sample / "field-identities.json").write_text(
        json.dumps({"position": {"entity_ids": [0, 1, 2, 3]}})
    )
    fields = {
        "position": {"shape": [4, 3], "dtype": "torch.float32", "state": "physical"},
        "pressure": {"shape": [4, 1], "dtype": "torch.float32", "state": "physical"},
    }
    manifest = {
        "version": 1,
        "state": "physical",
        "partitions": {"train": ["sample"]},
        "physical_layout": {
            "domains": {"surface": {"position": "position", "fields": {"pressure": "pressure"}}},
            "conditions": {},
        },
        "samples": [
            {
                "partition": "train",
                "sample": "sample",
                "path": "train/sample",
                "written": True,
                "filemap": {"position": "position.pt", "pressure": "pressure.pt"},
                "fields": fields,
                "assets": ["surface.vtkhdf", "field-identities.json"],
                "identity_assets": ["field-identities.json"],
                "meshes": {"surface": "surface.vtkhdf"},
            }
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    return path


def test_manifest_resolves_only_declared_mesh_and_physical_view_exposes_it(tmp_path):
    manifest = platform_dataset(tmp_path)
    index = ManifestIndex(manifest)
    assert index.resolve_asset("train", 0, "surface").name == "surface.vtkhdf"
    with pytest.raises(ValueError, match="未声明"):
        index.resolve_asset("train", 0, "old.vtkhdf")
    sample = PhysicalView(manifest).read("train", 0)
    assert Path(sample["domains"]["surface"]["mesh"]).name == "surface.vtkhdf"
    assert sample["domains"]["surface"]["ids"].tolist() == [0, 1, 2, 3]


@pytest.mark.parametrize("relative", ["pressure.pt", "surface.vtkhdf", "field-identities.json"])
def test_manifest_digest_covers_tensor_mesh_and_identity_assets(tmp_path, relative):
    manifest = platform_dataset(tmp_path)
    index = ManifestIndex(manifest)
    original = index.content_digest()
    asset = tmp_path / "train/sample" / relative
    payload = asset.read_bytes()
    asset.write_bytes(payload + b"changed")
    changed = ManifestIndex(manifest).content_digest()
    assert changed != original


def test_nasa_save_physical_builds_vtkhdf_from_connectivity(tmp_path):
    """NASA 平台交付把官方连接固化为样本网格，不依赖后续原文件读取。"""
    from types import SimpleNamespace

    import h5py

    from ai4e_contrib.application.datasets import nasa_crm

    connectivity = tmp_path / "connectivity.h5"
    with h5py.File(connectivity, "w") as stream:
        group = stream.create_group("Connectivity")
        for index, neighbors in enumerate(([1, 3], [0, 2], [1, 3], [0, 2])):
            group.create_dataset(str(index), data=np.asarray(neighbors, dtype=np.int64))
    points = np.asarray(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        dtype=np.float32,
    )
    arrays = {
        "points": points,
        "normals": np.tile([[0.0, 0.0, 1.0]], (4, 1)).astype(np.float32),
        "labels": np.zeros((4, 4), dtype=np.float32),
        "area": np.ones(4, dtype=np.float32),
        "conditions": np.zeros(6, dtype=np.float32),
        "global_targets": np.zeros(3, dtype=np.float64),
    }
    raw = SimpleNamespace(sources={"training": {"path": "train.h5"}, "test": {"path": "test.h5"}})
    config = {
        "rawprep": {"formats": ["pt"], "vtkhdf": True},
        "dataset": {"connectivity_h5": str(connectivity)},
    }
    save = SavePhysical(raw, nasa_crm, config)
    result = save(
        {
            "partition": "train",
            "sample_id": "sample",
            "arrays": arrays,
            "physical_fields": nasa_crm.physical_fields(arrays),
            "overwrite": False,
            "dry_run": False,
        },
        output={"root": str(tmp_path / "published")},
    )
    record = result
    assert record["meshes"] == {"surface": "surface.vtkhdf"}
    mesh = tmp_path / "published/train/sample/surface.vtkhdf"
    assert mesh.is_file()
    connectivity.unlink()
    loaded = vtk.vtkHDFReader()
    loaded.SetFileName(str(mesh))
    loaded.Update()
    assert loaded.GetOutput().GetNumberOfPoints() == 4
    assert loaded.GetOutput().GetNumberOfCells() == 1
