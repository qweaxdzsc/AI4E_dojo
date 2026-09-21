"""时间、实体、MAT、原始网格及可搬移数据交接。"""

import numpy as np
import pytest
import pyvista as pv
from scipy.io import savemat

from ai4e_core.abilities.data.extract.time_series import extract_time_series
from ai4e_core.abilities.data.save.indexed_cache import read_indexed_cache, save_indexed_cache
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample, save_mesh_sample
from ai4e_core.abilities.data.source.matlab import read_matlab
from ai4e_core.abilities.data.validate.time_series import validate_time_series
from ai4e_core.abilities.sampling.structured_grid import grid_indices
from ai4e_core.abilities.transform.mesh_fields import cell_fields_to_points


def test_mat_preserves_precision_and_named_fields(tmp_path):
    a = np.arange(24, dtype="float64").reshape(2, 3, 4)
    path = tmp_path / "fields.mat"
    savemat(path, {"field": a})
    result = read_matlab(path, ("field",))["field"]
    assert result.dtype == a.dtype
    np.testing.assert_array_equal(result, a)
    with pytest.raises(KeyError):
        read_matlab(path, ("missing",))


def test_numeric_times_and_alignment():
    data = {
        "u_t100": np.ones((3, 1)) * 100,
        "u_t10": np.ones((3, 1)) * 10,
        "u_t0": np.zeros((3, 1)),
    }
    times, values = extract_time_series(data, lambda n: n.startswith("u_t"), lambda n: float(n[3:]))
    np.testing.assert_array_equal(times, [0, 10, 100])
    validate_time_series(times, {"u": values}, np.arange(3), expected_times=[0, 10, 100])
    with pytest.raises(ValueError):
        validate_time_series(times, {"u": values}, np.array([[0, 1, 2], [1, 0, 2], [0, 1, 2]]))
    with pytest.raises(ValueError):
        validate_time_series(times, {"u": values}, np.arange(3), expected_times=[0, 10, 20])
    data["u_t10.0"] = data["u_t10"]
    with pytest.raises(ValueError):
        extract_time_series(data, lambda n: True, lambda n: float(n[3:]))


def test_mesh_pt_vtkhdf_and_conversion(tmp_path):
    mesh = pv.Plane(i_resolution=2, j_resolution=2)
    mesh.cell_data["stress"] = np.arange(mesh.n_cells, dtype=float)
    original = mesh.cell_data["stress"].copy()
    fields, _points, _cells = cell_fields_to_points(mesh, ("stress",))
    np.testing.assert_allclose(
        fields["stress"], mesh.cell_data_to_point_data().point_data["stress"]
    )
    np.testing.assert_array_equal(original, mesh.cell_data["stress"])
    path = save_mesh_sample(tmp_path / "physical", mesh, metadata={"id": "a"})
    restored = read_mesh_sample(path, mesh=True)
    assert restored["mesh"].n_cells == mesh.n_cells
    np.testing.assert_array_equal(restored["fields"]["cell"]["stress"], original)
    assert restored["point_ids"].tolist() == list(range(mesh.n_points))


def test_cache_and_grid_identity(tmp_path):
    ids, shape = grid_indices((421, 421), (5, 5))
    assert shape == (85, 85)
    assert ids[-1] == 421 * 421 - 1
    indices = np.zeros((1, 3, 2), dtype=np.int64)
    valid = np.ones_like(indices, dtype=bool)
    path = save_indexed_cache(
        tmp_path / "cache", indices, valid, identity={"radius": 1, "coordinates": "abc"}
    )
    read_indexed_cache(path, identity={"radius": 1, "coordinates": "abc"})
    with pytest.raises(ValueError):
        read_indexed_cache(path, identity={"radius": 2})


def test_vtkhdf_time_field_names_are_reversible(tmp_path):
    mesh = pv.Plane(i_resolution=1, j_resolution=1)
    values = np.arange(mesh.n_points * 3, dtype="float32").reshape(-1, 3)
    mesh.point_data["displacement_t10.000"] = values
    path = save_mesh_sample(tmp_path / "sample", mesh, metadata={})
    result = read_mesh_sample(path, mesh=True)
    np.testing.assert_array_equal(result["mesh"].point_data["displacement_t10.000"], values)
