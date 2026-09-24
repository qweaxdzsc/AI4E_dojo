"""经典案例的真实单元插值、字段身份、训练统计与可搬移准备；不训练模型。"""

import json
import shutil
from functools import partial
from pathlib import Path

import h5py
import numpy as np
import pytest
import pyvista as pv
import torch
from scipy.io import savemat

from ai4e_contrib.application.classic_networks import (
    binding,
    darcy,
    double_cylinder,
    prediction,
    preparation,
    shapenet_volume,
)
from ai4e_core.abilities.data.extract.mesh_probe import (
    probe_fields,
    probe_regular,
    regular_coordinates,
)
from ai4e_core.abilities.data.save.array_manifest import read_arrays
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_dataset
from ai4e_core.applications.parametric_pde.rawprep import prepare_named_fields


class DirectSamples:
    """测试中同步执行真实单样本计算，不替换数值或数据保存能力。"""

    def execute_samples(self, samples, operation, *, stage):
        return [operation(sample) for sample in samples]


def affine(points):
    """独立闭式向量场，每个分量使用不同系数以发现轴/分量错位。"""
    matrix = np.array([[2.0, -3.0, 4.0], [-1.0, 5.0, 2.0], [3.0, 2.0, -2.0]])
    return np.asarray(points) @ matrix.T + np.array([7.0, 11.0, 13.0])


def tetrahedron(offset=0.0):
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    mesh = pv.UnstructuredGrid(np.array([4, 0, 1, 2, 3]), np.array([pv.CellType.TETRA]), points)
    mesh.point_data["point_vectors"] = affine(points) + offset
    mesh.point_data["surface_distance"] = 1.0 + points @ np.array([1.0, 2.0, 3.0])
    return mesh


def test_affine_probe_uses_cells_and_preserves_invalid():
    mesh = tetrahedron()
    points = np.array([[0.1, 0.2, 0.3], [0.0, 0.0, 0.0], [0.8, 0.8, 0.8], [2.0, 0.0, 0.0]])
    arrays, valid = probe_fields(mesh, points, ("point_vectors", "surface_distance"))
    np.testing.assert_array_equal(valid, [True, True, False, False])
    np.testing.assert_allclose(arrays["point_vectors"][valid], affine(points[valid]), atol=1e-10)
    np.testing.assert_allclose(
        arrays["surface_distance"][valid], 1 + points[valid] @ np.array([1.0, 2.0, 3.0])
    )
    np.testing.assert_array_equal(arrays["point_vectors"][~valid], 0)


def test_regular_probe_preserves_axes_and_requires_valid_support():
    coordinates = regular_coordinates((0, 2, 0, 3, 0, 4), (3, 4, 5))
    np.testing.assert_array_equal(coordinates[2, 3, 4], [2, 3, 4])
    values = affine(coordinates)
    valid = np.ones((3, 4, 5), dtype=bool)
    points = np.array([[1.5, 2.5, 3.5], [0.5, 0.5, 0.5], [3.0, 1.0, 1.0]])
    output, supported = probe_regular(coordinates, values, valid, points)
    np.testing.assert_array_equal(supported, [True, True, False])
    np.testing.assert_allclose(output[:2], affine(points[:2]), atol=1e-10)
    valid[0, 0, 0] = False
    output, supported = probe_regular(coordinates, values, valid, points)
    np.testing.assert_array_equal(supported, [True, False, False])
    np.testing.assert_array_equal(output[~supported], 0)


def test_regular_probe_rejects_near_boundary_invalid_support():
    coordinates = regular_coordinates((0, 1, 0, 1, 0, 1), (2, 2, 2))
    valid = np.ones((2, 2, 2), dtype=bool)
    valid[1, :, :] = False
    _, supported = probe_regular(
        coordinates, affine(coordinates), valid, np.array([[1e-11, 0.5, 0.5]])
    )
    # 查询在单元内部，x=1 面的无效顶点具有正权重，不能用近似为一隐藏无效支撑。
    assert not supported[0]


def test_probe_rejects_missing_point_field_and_degenerate_grid():
    with pytest.raises(ValueError, match="点场"):
        probe_fields(tetrahedron(), np.zeros((1, 3)), ("absent",))
    with pytest.raises(ValueError, match="非退化"):
        regular_coordinates((0, 0, 0, 1, 0, 1), (2, 2, 2))


def test_darcy_source_and_stride_keep_field_entity_identity(tmp_path):
    root = tmp_path / "mat"
    root.mkdir()
    row, column = np.meshgrid(np.arange(9), np.arange(9), indexing="ij")
    coeff = 10 * row + column + 1.0
    solution = -2 * row + 7 * column + 3.0
    for suffix, offset in (("smooth1", 0), ("smooth2", 1000)):
        savemat(
            root / f"piececonst_r421_N1024_{suffix}.mat",
            {
                "coeff": np.stack((coeff + offset, coeff + offset + 100)),
                "sol": np.stack((solution + offset, solution + offset + 200)),
            },
        )
    dataset = {"case": "darcy", "train_count": 2, "test_count": 1, "stride": 2}
    source = darcy.source(root, dataset)
    physical = prepare_named_fields(
        source.samples(), source.read, tmp_path / "physical", session=DirectSamples(), metadata={}
    )
    records = read_mesh_dataset(physical)
    assert [item["split"] for item in records] == ["train", "train", "test"]
    sample = darcy.extract(records[0]["path"], dataset)
    np.testing.assert_array_equal(sample["entity_ids"], np.arange(81).reshape(9, 9)[::2, ::2])
    np.testing.assert_allclose(sample["input"][..., 0], column[::2, ::2] / 8)
    np.testing.assert_allclose(sample["input"][..., 1], row[::2, ::2] / 8)
    np.testing.assert_array_equal(sample["input"][..., 2], coeff[::2, ::2])
    np.testing.assert_array_equal(sample["target"][..., 0], solution[::2, ::2])
    assert sample["valid"].all()


def test_shapenet_official_selection_ignores_directory_name(tmp_path):
    source = shapenet_volume.ShapeNetSource(
        tmp_path / "training_data", {"train_count": 8, "test_count": 2}
    )
    rows = source.samples()
    assert [row["split"] for row in rows] == ["train"] * 8 + ["test"] * 2
    train = {row["source_id"] for row in rows if row["split"] == "train"}
    test = {row["source_id"] for row in rows if row["split"] == "test"}
    assert train.isdisjoint(test)
    assert [row["source_id"] for row in rows[:8]] == sorted(train)


def test_preparation_uses_train_valid_only_and_is_movable(tmp_path):
    samples = [
        {"id": "train_a", "split": "train", "offset": 0},
        {"id": "train_b", "split": "train", "offset": 20},
        {"id": "test_a", "split": "test", "offset": 1000},
    ]
    physical = prepare_named_fields(
        samples,
        lambda sample: (tetrahedron(sample["offset"]), {}),
        tmp_path / "physical",
        session=DirectSamples(),
        metadata={},
    )
    dataset = {"case": "shapenet_volume", "grid_size": 4}
    prepared = preparation.prepare(physical, tmp_path / "prepared", dataset, DirectSamples())
    record, train = preparation.read_prepared(prepared, "train")
    _, test = preparation.read_prepared(prepared, "test")
    stats = record["metadata"]["statistics"]
    assert stats["fit_ids"] == ["train_a", "train_b"]
    assert stats["feature_count"] == 4
    mask = train["valid"]
    assert mask.any() and not mask.all()
    physical_inputs = train["physical_input"][..., :4][mask]
    physical_targets = train["physical_target"][mask]
    np.testing.assert_allclose(stats["input"]["mean"], physical_inputs.mean(0), rtol=1e-6)
    np.testing.assert_allclose(stats["target"]["mean"], physical_targets.mean(0), rtol=1e-6)
    np.testing.assert_allclose(stats["target"]["scale"], physical_targets.std(0), rtol=1e-6)
    np.testing.assert_array_equal(train["input"][..., -1], mask)
    assert np.abs(test["target"][test["valid"]]).mean() > 10
    expected = {name: np.array(value) for name, value in test.items()}
    copy = tmp_path / "relocated"
    shutil.copytree(Path(prepared).parent, copy)
    Path(prepared).parent.rename(tmp_path / "original-hidden")
    Path(physical).parent.rename(tmp_path / "physical-hidden")
    _, restored = preparation.read_prepared(copy / "manifest.json", "test")
    for name, value in expected.items():
        np.testing.assert_array_equal(restored[name], value)
    index = json.loads((copy / "manifest.json").read_text())
    index["splits"]["test"] = "../outside/manifest.json"
    (copy / "manifest.json").write_text(json.dumps(index))
    with pytest.raises(ValueError, match="越界"):
        preparation.read_prepared(copy / "manifest.json", "test")


def test_moved_preparation_back_projection_and_fixed_original_mesh_post(tmp_path):
    samples = [
        {"id": "train_a", "split": "train", "offset": 0},
        {"id": "train_b", "split": "train", "offset": 20},
        {"id": "test_b", "split": "test", "offset": 3},
        {"id": "test_a", "split": "test", "offset": 7},
    ]
    physical = prepare_named_fields(
        samples,
        lambda sample: (tetrahedron(sample["offset"]), {}),
        tmp_path / "physical",
        session=DirectSamples(),
        metadata={},
    )
    prepared = preparation.prepare(
        physical,
        tmp_path / "prepared",
        {"case": "shapenet_volume", "grid_size": 4},
        DirectSamples(),
    )
    relocated = tmp_path / "relocated"
    shutil.copytree(Path(prepared).parent, relocated)
    Path(prepared).parent.rename(tmp_path / "old-prepared-hidden")
    Path(physical).parent.rename(tmp_path / "old-physical-hidden")
    manifest = relocated / "manifest.json"
    record, arrays = preparation.read_prepared(manifest, "test")
    identities = record["metadata"]["ids"]
    assert identities == ["test_b", "test_a"]
    originals = preparation.original_samples(manifest, "test", identities)
    assert all(Path(path).is_relative_to(relocated / "physical") for path in originals)
    assert preparation.original_samples(manifest, "test", identities[::-1]) == originals[::-1]
    with pytest.raises(ValueError, match="身份"):
        preparation.original_samples(manifest, "test", ["test_b", "wrong"])

    # 用闭式系数设置模型，将归一化输入映射为不含样本偏移的解析场；无优化器更新。
    stats = record["metadata"]["statistics"]
    matrix = np.array([[2.0, -3.0, 4.0], [-1.0, 5.0, 2.0], [3.0, 2.0, -2.0]])
    bias = np.array([7.0, 11.0, 13.0])
    target_scale = np.asarray(stats["target"]["scale"])
    network = torch.nn.Linear(5, 3)
    with torch.no_grad():
        network.weight.zero_()
        network.weight[:, :3].copy_(
            torch.as_tensor(
                matrix * np.asarray(stats["input"]["scale"][:3]) / target_scale[:, None]
            )
        )
        network.bias.copy_(
            torch.as_tensor(
                (
                    matrix @ np.asarray(stats["input"]["mean"][:3])
                    + bias
                    - np.asarray(stats["target"]["mean"])
                )
                / target_scale
            )
        )
    model = binding.FieldModel(network, "mlp", 3)
    fixed = prediction.predict_fields(
        model,
        arrays,
        record,
        partial(binding.batch, arrays, device="cpu", case="shapenet_volume"),
        tmp_path / "fixed",
        originals=originals,
    )
    _, saved = read_arrays(fixed, kind="classic-results-v1")
    np.testing.assert_array_equal(saved["original_offsets"], [0, 4, 8])
    points = np.asarray(tetrahedron().points)
    np.testing.assert_array_equal(saved["original_coordinates"], np.tile(points, (2, 1)))
    np.testing.assert_array_equal(saved["original_entity_ids"], np.tile(np.arange(4), 2))
    np.testing.assert_array_equal(saved["original_valid"], [True, False, False, False] * 2)
    np.testing.assert_allclose(saved["original_target"][:4], affine(points) + 3)
    np.testing.assert_allclose(saved["original_target"][4:], affine(points) + 7)
    np.testing.assert_allclose(
        saved["original_prediction"][[0, 4]], affine(points)[[0, 0]], atol=3e-6
    )
    np.testing.assert_array_equal(saved["original_prediction"][~saved["original_valid"]], 0)
    portable = tmp_path / "portable-results"
    shutil.copytree(Path(fixed).parent, portable)
    Path(fixed).parent.rename(tmp_path / "old-fixed-hidden")
    relocated.rename(tmp_path / "relocated-hidden")

    def forbidden(*args, **kwargs):
        raise AssertionError("固定原网格后处理不得重新运行模型")

    model.forward = forbidden
    report = prediction.evaluate(portable / "manifest.json", tmp_path / "post")
    rows = report["original_mesh"]["rows"]
    assert [row["id"] for row in rows] == identities
    assert [row["total_count"] for row in rows] == [4, 4]
    assert [row["valid_count"] for row in rows] == [1, 1]
    assert [row["coverage"] for row in rows] == [0.25, 0.25]
    np.testing.assert_allclose(
        [row["component_mse"] for row in rows], [[9] * 3, [49] * 3], atol=5e-5
    )
    assert (
        json.loads((tmp_path / "post/metrics.json").read_text())["original_mesh"]
        == report["original_mesh"]
    )


def write_cylinder(path, offset):
    """压缩夹具保留真实来源轴，数值编码时间与字段，避免把像素当时间。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as stream:
        stream["metadata/grid/times"] = np.arange(1000)
        stream["metadata/grid/x_coordinates"] = np.arange(130)
        stream["metadata/grid/y_coordinates"] = np.arange(130)
        for field, name in enumerate(double_cylinder.FIELDS):
            values = stream.create_dataset(
                "data/" + name,
                shape=(1000, 130, 130),
                chunks=(1, 130, 130),
                dtype="f4",
                compression="gzip",
                fillvalue=-999,
            )
            for time in range(0, 1000, 10):
                values[time] = offset + 1000 * field + time


def test_cylinder_windows_preserve_real_time_and_official_val(tmp_path):
    source = tmp_path / "source"
    write_cylinder(source / "train/fluid_simulation_segment_00.h5", 0)
    write_cylinder(source / "train/fluid_simulation_segment_04.h5", 10000)
    write_cylinder(source / "val/fluid_simulation_segment_05.h5", 50000)
    outputs = double_cylinder.prepare_source(
        source, tmp_path / "windows", {"train_count": 2, "test_count": 1}, DirectSamples()
    )
    record, train = read_arrays(outputs["train"], kind="classic-physical-windows-v1")
    validation_record, validation = read_arrays(outputs["test"], kind="classic-physical-windows-v1")
    assert len(record["metadata"]["ids"]) == 66
    assert len(validation_record["metadata"]["ids"]) == 8
    assert validation_record["metadata"]["source_files"] == ["fluid_simulation_segment_05.h5"]
    np.testing.assert_array_equal(train["times"][:, 0], np.tile(np.arange(0, 961, 30), 2))
    np.testing.assert_array_equal(validation["times"][:, 0], np.arange(0, 841, 120))
    np.testing.assert_array_equal(train["times"][32], [960, 970, 980, 990])
    np.testing.assert_array_equal(train["input"][32, :, 0, 0, 0], [960, 970, 980])
    assert train["target"][32, 0, 0, 0] == 990
    np.testing.assert_allclose(train["input"][0, :, 0, 0, 3], [30, 30.1, 30.2])
    assert validation["target"][0, 0, 0, 0] == 50030
    assert not np.isin(validation_record["metadata"]["ids"], record["metadata"]["ids"]).any()
