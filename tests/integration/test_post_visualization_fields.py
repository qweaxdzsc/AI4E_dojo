"""物理字段选择、实体绑定与解析网格夹具。"""

import numpy as np
import pytest
import pyvista as pv

from ai4e_core.abilities.postproc.visualization import field_values
from ai4e_core.applications.aero_cfd.post import bind_mesh, read_fields


def grid():
    """线性标量与恒定矢量具有独立解析解。"""
    mesh = pv.ImageData(dimensions=(11, 11, 11), spacing=(0.1, 0.1, 0.1))
    mesh.point_data["p"] = mesh.points @ np.array([1.0, 2.0, 3.0])
    mesh.point_data["U"] = np.tile([1.0, 0.0, 0.0], (mesh.n_points, 1))
    mesh.cell_data["p"] = np.full(mesh.n_cells, 42.0)
    return mesh


def field_sample():
    """内存字段与原拓扑的显式交接，不构建模型。"""
    mesh = grid()
    fields = {
        "volume.position": mesh.points.copy(),
        "volume.ids": np.arange(mesh.n_points),
        "volume.velocity.prediction": mesh["U"].copy(),
        "volume.velocity.truth": mesh["U"].copy() * 0.9,
    }
    return {
        "metadata": {
            "identity": {"sample": "s"},
            "domains": {
                "volume": {
                    "position": "volume.position",
                    "ids": "volume.ids",
                    "targets": {"velocity": "volume.velocity"},
                    "identity_basis": "source",
                    "units": {"velocity": "m/s"},
                }
            },
        },
        "fields": fields,
        "source_meshes": {"volume": mesh},
        "origin": {"id": "test-source"},
    }


def test_point_cell_and_component_are_explicit():
    mesh = grid()
    assert field_values(mesh, "p", association="cell").tolist() == [42.0] * mesh.n_cells
    np.testing.assert_allclose(field_values(mesh, "U", component="magnitude"), 1.0)
    with pytest.raises(ValueError):
        field_values(mesh, "U")
    with pytest.raises(ValueError):
        field_values(mesh, "U", component=3)
    with pytest.raises(ValueError):
        field_values(mesh, "p", mask=np.ones(mesh.n_points))


def test_binding_identity_and_input_immutability():
    original = field_sample()
    sample = read_fields(original)
    mesh = bind_mesh(sample, domain="volume")
    assert mesh.n_cells == original["source_meshes"]["volume"].n_cells
    np.testing.assert_allclose(mesh["volume.velocity.vector_error"], 0.1)
    assert "volume.velocity.prediction" not in original["source_meshes"]["volume"].point_data
    sample["fields"]["volume.ids"][1] = 0
    with pytest.raises(ValueError, match="身份"):
        read_fields(sample)


def test_invalid_mask_and_missing_topology():
    original = field_sample()
    original["metadata"]["domains"]["volume"]["validity"] = "valid"
    original["fields"]["valid"] = np.zeros(len(original["fields"]["volume.ids"]), dtype=bool)
    original["fields"]["valid"][::2] = True
    original["fields"]["volume.velocity.prediction"][1::2] = np.nan
    sample = read_fields(original)
    sample.pop("source_meshes")
    with pytest.raises(ValueError, match="拓扑"):
        bind_mesh(sample, domain="volume")
