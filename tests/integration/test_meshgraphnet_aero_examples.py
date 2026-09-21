"""静态外流 MeshGraphNet 两个可复制案例的合成闭环验收。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
import vtk
import yaml
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf

REPOSITORY = Path(__file__).resolve().parents[2]


def _mesh(path: Path, points: torch.Tensor, cell: list[int], cell_type: int) -> None:
    mesh = vtk.vtkUnstructuredGrid()
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(points.numpy(), deep=True))
    mesh.SetPoints(vtk_points)
    cells = vtk.vtkCellArray()
    cells.SetCells(
        1,
        numpy_to_vtkIdTypeArray(np.asarray([len(cell), *cell], dtype=np.int64), deep=True),
    )
    mesh.SetCells(cell_type, cells)
    write_vtkhdf(path, mesh)


def _record(root: Path, split: str, name: str, fields: dict, meshes: dict) -> dict:
    destination = root / split / name
    destination.mkdir(parents=True)
    filemap = {key: f"{key}.pt" for key in fields}
    for key, value in fields.items():
        torch.save(value, destination / filemap[key])
    for mesh_name, (points, cell, cell_type) in meshes.items():
        _mesh(destination / f"{mesh_name}.vtkhdf", points, cell, cell_type)
    return {
        "partition": split,
        "sample": name,
        "path": str(destination.relative_to(root)),
        "written": True,
        "filemap": filemap,
        "fields": {
            key: {"shape": list(value.shape), "dtype": str(value.dtype), "state": "physical"}
            for key, value in fields.items()
        },
        "assets": [f"{key}.vtkhdf" for key in meshes],
        "meshes": {key: f"{key}.vtkhdf" for key in meshes},
    }


def setup_meshgraphnet_case(tmp_path: Path, case_name: str) -> tuple[Path, Path]:
    """复制案例并生成只含平台 PT、VTKHDF 和 manifest 的小数据集。"""
    case = tmp_path / "case"
    shutil.copytree(REPOSITORY / "examples/aero_cfd" / case_name, case)
    platform = tmp_path / "platform"
    surface = torch.tensor([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]])
    volume = torch.tensor(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    partitions = {
        "train": ["train-a", "train-b"] if case_name == "nasa_crm_meshgraphnet" else ["train-a"],
        "test": ["test-a"],
    }
    records = []
    for split, names in partitions.items():
        for index, name in enumerate(names):
            offset = float(index + (2 if split == "test" else 0))
            if case_name == "shapenet_car_meshgraphnet":
                fields = {
                    "surface_position": surface,
                    "surface_normals": torch.tensor([[0.0, 0.0, 1.0]] * 4),
                    "surface_pressure": torch.arange(4.0)[:, None] + offset,
                    "volume_position": volume,
                    "volume_sdf": torch.arange(8.0)[:, None],
                    "volume_normals": torch.tensor([[0.0, 0.0, 1.0]] * 8),
                    "volume_velocity": torch.arange(24.0).reshape(8, 3) / 10 + offset,
                }
                meshes = {
                    "surface": (surface, list(range(4)), vtk.VTK_QUAD),
                    "volume": (volume, list(range(8)), vtk.VTK_HEXAHEDRON),
                }
            else:
                fields = {
                    "surface_position": surface,
                    "surface_normals": torch.tensor([[0.0, 0.0, 1.0]] * 4),
                    "surface_cp": torch.arange(4.0)[:, None] + offset,
                    "surface_cf": torch.arange(12.0).reshape(4, 3) / 10 + offset,
                    "conditions": torch.arange(6.0)[None] + offset,
                    "surface_ids": torch.arange(4),
                }
                meshes = {"surface": (surface, list(range(4)), vtk.VTK_QUAD)}
            records.append(_record(platform, split, name, fields, meshes))
    layout = (
        {
            "domains": {
                "surface": {
                    "position": "surface_position",
                    "fields": {"pressure": "surface_pressure", "normals": "surface_normals"},
                },
                "volume": {
                    "position": "volume_position",
                    "fields": {
                        "velocity": "volume_velocity",
                        "distance": "volume_sdf",
                        "normals": "volume_normals",
                    },
                },
            },
            "conditions": {},
        }
        if case_name == "shapenet_car_meshgraphnet"
        else {
            "domains": {
                "surface": {
                    "position": "surface_position",
                    "ids": "surface_ids",
                    "fields": {
                        "pressure_coefficient": "surface_cp",
                        "friction_coefficient": "surface_cf",
                        "normals": "surface_normals",
                    },
                }
            },
            "conditions": {"conditions": 6},
        }
    )
    manifest = {
        "version": 1,
        "state": "physical",
        "partitions": partitions,
        "samples": records,
        "physical_layout": layout,
    }
    (platform / "manifest.json").write_text(json.dumps(manifest))
    config = yaml.safe_load((case / "config.yaml").read_text())
    config["pipeline"]["stages"] = ["trainprep", "train", "infer", "post"]
    config["data_root"] = str(tmp_path / "data")
    config["run_root"] = str(tmp_path / "runs")
    config["inputs"]["trainprep"]["dataset"] = str(platform / "manifest.json")
    config["model"]["parameters"] = {"hidden_dim": 8, "processor_layers": 2}
    domain = "volume" if case_name == "shapenet_car_meshgraphnet" else "surface"
    for role in ("train", "infer"):
        config["model"]["sampling"]["domains"][domain][role] = {
            "method": "core_halo",
            "core_nodes": 4 if domain == "volume" else 2,
            "halo_hops": 2,
        }
    config["train"].update(max_epochs=1, device="cpu", evaluation_enabled=False)
    config["infer"].update(
        samples=["test-a"], split="test", device="cpu", export_vtk=False, export_mesh=False
    )
    config["post"]["analysis_enabled"] = False
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    return case, platform


def run_case(case: Path) -> Path:
    """从复制目录执行公开 pipeline，并返回唯一运行目录。"""
    completed = subprocess.run(
        [sys.executable, str(case / "pipeline.py")],
        cwd=case.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    config = yaml.safe_load((case / "config.yaml").read_text())
    runs = sorted(Path(config["run_root"]).iterdir())
    assert len(runs) == 1
    return runs[0]


@pytest.mark.parametrize(
    "case_name,expected_fields",
    [
        ("shapenet_car_meshgraphnet", {"surface.pressure", "volume.velocity"}),
        ("nasa_crm_meshgraphnet", {"surface.cp", "surface.cf"}),
    ],
)
def test_copied_graph_case_short_train_full_infer_and_fixed_post(
    tmp_path, case_name, expected_fields
):
    """复制后的两个案例完成准备、更新、完整拼回、五指标与固定 post。"""
    case, _platform = setup_meshgraphnet_case(tmp_path, case_name)
    run = run_case(case)
    assert (run / "artifacts/preparation.json").is_file()
    assert (run / "checkpoints/last.pt").is_file()
    result = json.loads((run / "artifacts/physical-predictions.json").read_text())
    assert result["status"] == "succeeded"
    assert set(result["results"][0]["metrics"]) >= expected_fields
    for record in result["results"][0]["metric_records"]:
        assert set(record["values"]) == {
            "relative_l2",
            "mae",
            "rmse",
            "max_abs_error",
            "r2",
        }
