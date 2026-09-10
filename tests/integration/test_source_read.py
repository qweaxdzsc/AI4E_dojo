"""数据读取：按路径统一返回 VTK 内存对象，验证结构和数组可恢复。"""

from __future__ import annotations

import gc
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.util.vtkConstants import VTK_TRIANGLE
from vtkmodules.vtkCommonCore import (
    vtkDoubleArray,
    vtkFloatArray,
    vtkIdList,
    vtkIntArray,
    vtkPoints,
)
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkDataObject,
    vtkDataSet,
    vtkPolyData,
    vtkUnstructuredGrid,
)
from vtkmodules.vtkIOHDF import vtkHDFWriter
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridWriter
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter, vtkXMLUnstructuredGridWriter

from ai4e_core.abilities.data.source import read as read_mod
from ai4e_core.abilities.data.source.read import read_file, read_many, read_tree
from tests.support import SHAPENET_SAMPLES


def _add_arrays(dataset: vtkDataSet) -> None:
    """给测试网格增加 point、cell 和 field 三类原始数组。"""
    pressure = vtkDoubleArray()
    pressure.SetName("pressure")
    for value in (1.0, 2.0, 3.0):
        pressure.InsertNextValue(value)

    marker = vtkIntArray()
    marker.SetName("marker")
    for value in (7, 8, 9):
        marker.InsertNextValue(value)

    velocity = vtkFloatArray()
    velocity.SetName("velocity")
    velocity.SetNumberOfComponents(3)
    for value in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)):
        velocity.InsertNextTuple(value)

    point_data = dataset.GetPointData()
    point_data.SetScalars(pressure)
    point_data.AddArray(marker)
    point_data.SetVectors(velocity)
    alternate = vtkFloatArray()
    alternate.DeepCopy(velocity)
    alternate.SetName("alternate_velocity")
    alternate.SetTuple3(1, 2.0, 3.0, 4.0)
    point_data.AddArray(alternate)

    region = vtkIntArray()
    region.SetName("region")
    region.InsertNextValue(11)
    dataset.GetCellData().AddArray(region)

    case_id = vtkIntArray()
    case_id.SetName("case_id")
    case_id.InsertNextValue(42)
    dataset.GetFieldData().AddArray(case_id)


def _make_unstructured_grid() -> vtkUnstructuredGrid:
    """构造一个包含完整关联数据的三角形非结构网格。"""
    points = vtkPoints()
    for point in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        points.InsertNextPoint(point)

    point_ids = vtkIdList()
    for point_id in range(3):
        point_ids.InsertNextId(point_id)

    grid = vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.InsertNextCell(VTK_TRIANGLE, point_ids)
    _add_arrays(grid)
    return grid


def _make_poly_data() -> vtkPolyData:
    """构造一个包含完整关联数据的三角形 PolyData。"""
    points = vtkPoints()
    for point in ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)):
        points.InsertNextPoint(point)

    polygon = vtkIdList()
    for point_id in range(3):
        polygon.InsertNextId(point_id)
    polygons = vtkCellArray()
    polygons.InsertNextCell(polygon)

    data = vtkPolyData()
    data.SetPoints(points)
    data.SetPolys(polygons)
    _add_arrays(data)
    return data


def _write_unstructured(path: Path) -> Path:
    """按扩展名用 VTK 官方 writer 写出非结构网格。"""
    grid = _make_unstructured_grid()
    if path.suffix == ".vtk":
        writer = vtkUnstructuredGridWriter()
    elif path.suffix == ".vtu":
        writer = vtkXMLUnstructuredGridWriter()
    elif path.suffix in {".vtkhdf", ".vtkh5"}:
        writer = vtkHDFWriter()
    else:
        raise ValueError(f"测试不支持写出该格式: {path}")
    writer.SetFileName(str(path))
    writer.SetInputData(grid)
    assert writer.Write() == 1
    return path


def _write_poly(path: Path) -> Path:
    """用 VTK 官方 writer 写出 PolyData。"""
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(str(path))
    writer.SetInputData(_make_poly_data())
    assert writer.Write() == 1
    return path


def _write_npy(path: Path) -> Path:
    """写出保留 dtype 与 shape 的 NPY 夹具。"""
    np.save(path, np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int16))
    return path


def _assert_arrays_preserved(dataset: vtkDataSet) -> None:
    """断言 reader 没有丢失、改名或重分配原始数组。"""
    assert dataset.GetNumberOfPoints() == 3
    assert dataset.GetNumberOfCells() == 1
    np.testing.assert_array_equal(
        vtk_to_numpy(dataset.GetPoints().GetData()),
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    )
    assert dataset.GetCellType(0) == VTK_TRIANGLE
    ids = dataset.GetCell(0).GetPointIds()
    assert [ids.GetId(i) for i in range(ids.GetNumberOfIds())] == [0, 1, 2]

    point_data = dataset.GetPointData()
    assert point_data.GetScalars().GetName() == "pressure"
    assert point_data.GetVectors().GetName() == "velocity"
    assert point_data.GetArray("pressure").GetDataTypeAsString() == "double"
    assert point_data.GetArray("pressure").GetTuple1(1) == 2.0
    assert point_data.GetArray("marker").GetTuple1(2) == 9.0
    assert point_data.GetArray("velocity").GetTuple3(1) == (0.0, 1.0, 0.0)
    assert point_data.GetArray("alternate_velocity").GetTuple3(1) == (2.0, 3.0, 4.0)
    assert dataset.GetCellData().GetArray("region").GetTuple1(0) == 11.0
    assert dataset.GetFieldData().GetArray("case_id").GetTuple1(0) == 42.0


@pytest.mark.parametrize(
    ("suffix", "expected_type"),
    [
        (".vtk", vtkUnstructuredGrid),
        (".vtp", vtkPolyData),
        (".vtu", vtkUnstructuredGrid),
        (".vtkhdf", vtkUnstructuredGrid),
        (".vtkh5", vtkUnstructuredGrid),
    ],
)
def test_read_vtk_family_as_native_object(
    tmp_path: Path,
    suffix: str,
    expected_type: type[vtkDataSet],
) -> None:
    """各 VTK 家族格式返回对应原生对象并保留完整数据。"""
    path = tmp_path / f"mesh{suffix}"
    if suffix == ".vtp":
        _write_poly(path)
    else:
        _write_unstructured(path)

    dataset = read_file(path)

    assert isinstance(dataset, expected_type)
    _assert_arrays_preserved(dataset)

    del path
    gc.collect()
    _assert_arrays_preserved(dataset)


def test_read_npy_as_vtk_field_data(tmp_path: Path) -> None:
    """NPY 的 VTK FieldData 可恢复原始 dtype、shape 和值。"""
    dataset = read_file(_write_npy(tmp_path / "press.npy"))
    array = _restore_npy(dataset)
    assert array.dtype == np.int16
    assert array.shape == (2, 3)
    assert array.tolist() == [[1, 2, 3], [4, 5, 6]]


def test_missing_file_does_not_call_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """文件不存在时不进入格式适配器。"""
    called = {"vtk": False}

    def boom(_path: Path) -> object:
        called["vtk"] = True
        raise AssertionError("不应打开适配器")

    monkeypatch.setitem(read_mod.ADAPTERS, "vtk", boom)

    with pytest.raises(FileNotFoundError):
        read_file(tmp_path / "missing.vtk")
    assert called["vtk"] is False


def test_unknown_format_does_not_open_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """未知扩展名在适配前失败。"""
    mystery = tmp_path / "notes.txt"
    mystery.write_text("not a mesh", encoding="utf-8")
    called = {"any": False}

    def boom(_path: Path) -> object:
        called["any"] = True
        raise AssertionError("不应打开适配器")

    monkeypatch.setitem(read_mod.ADAPTERS, "vtk", boom)

    with pytest.raises(ValueError, match="不认识的文件格式"):
        read_file(mystery)
    assert called["any"] is False


def test_corrupt_or_mismatched_vtk_fails(tmp_path: Path) -> None:
    """损坏内容和伪装扩展名不得返回空 VTK 对象。"""
    corrupt = tmp_path / "corrupt.vtu"
    corrupt.write_text("not vtk", encoding="utf-8")

    legacy = _write_unstructured(tmp_path / "legacy.vtk")
    mismatched = tmp_path / "legacy.vtp"
    shutil.copyfile(legacy, mismatched)

    for path in (corrupt, mismatched):
        with pytest.raises(ValueError, match=str(path)):
            read_file(path)


def test_read_many_and_tree_return_native_objects(tmp_path: Path) -> None:
    """多文件与目录入口统一返回 VTK 对象，并保持排序约定。"""
    writers = {
        "a.vtk": _write_unstructured,
        "b.vtp": _write_poly,
        "c.vtu": _write_unstructured,
        "d.vtkhdf": _write_unstructured,
        "e.vtkh5": _write_unstructured,
        "f.npy": _write_npy,
    }
    paths = [writer(tmp_path / name) for name, writer in writers.items()]
    (tmp_path / "readme.md").write_text("skip", encoding="utf-8")

    many = read_many([paths[-1], paths[2]])
    tree = read_tree(tmp_path, recursive=True)

    assert all(isinstance(item, vtkDataObject) for item in many)
    assert all(isinstance(item, vtkDataObject) for _, item in tree)
    assert isinstance(many[1], vtkUnstructuredGrid)
    assert [path.name for path, _data in tree] == sorted(writers)


def test_aero_pre_no_longer_exposes_configured_reading() -> None:
    """Aero CFD pre 不再暴露仅做配置式读取的旧入口；读抽洗走 extract_configured_sample。"""
    from ai4e_core.applications.aero_cfd import rawprep as pre

    assert not hasattr(pre, "read_configured_files")
    assert not hasattr(pre, "read_configured_tree")


@pytest.mark.local_data
@pytest.mark.parametrize("sample_relative", SHAPENET_SAMPLES)
def test_read_real_shapenet_car_sample(shapenet_raw: Path, sample_relative: Path) -> None:
    """真实样本统一返回 VTK 对象，NPY 与网格数值均与原始读取一致。"""
    sample = shapenet_raw / sample_relative
    if not sample.is_dir():
        pytest.skip(f"样本目录不存在: {sample}")

    surface = read_file(sample / "quadpress_smpl.vtk")
    volume = read_file(sample / "hexvelo_smpl.vtk")
    press = read_file(sample / "press.npy")

    assert isinstance(surface, vtkDataSet)
    assert isinstance(volume, vtkDataSet)
    restored = _restore_npy(press)
    original = np.load(sample / "press.npy", allow_pickle=False)
    np.testing.assert_array_equal(restored, original)
    assert restored.dtype == original.dtype
    assert surface.GetNumberOfPoints() == 3682
    assert surface.GetPointData().GetScalars().GetNumberOfTuples() == 3682
    assert volume.GetNumberOfPoints() == 29498
    assert volume.GetPointData().GetVectors().GetNumberOfTuples() == 29498
    assert restored.shape == (3682,)
    from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader

    for mesh, filename in ((surface, "quadpress_smpl.vtk"), (volume, "hexvelo_smpl.vtk")):
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(str(sample / filename))
        reader.Update()
        expected = reader.GetOutput()
        np.testing.assert_array_equal(
            vtk_to_numpy(mesh.GetPoints().GetData()),
            vtk_to_numpy(expected.GetPoints().GetData()),
        )
        np.testing.assert_array_equal(
            vtk_to_numpy(mesh.GetCells().GetConnectivityArray()),
            vtk_to_numpy(expected.GetCells().GetConnectivityArray()),
        )
        np.testing.assert_array_equal(
            vtk_to_numpy(mesh.GetCells().GetOffsetsArray()),
            vtk_to_numpy(expected.GetCells().GetOffsetsArray()),
        )
        for i in range(expected.GetPointData().GetNumberOfArrays()):
            array = expected.GetPointData().GetArray(i)
            np.testing.assert_array_equal(
                vtk_to_numpy(mesh.GetPointData().GetArray(array.GetName())),
                vtk_to_numpy(array),
            )


def _restore_npy(dataset: vtkDataObject) -> np.ndarray:
    """测试侧按公开 FieldData 契约恢复 NPY，不依赖生产转换实现。"""
    assert type(dataset) is vtkDataObject
    fields = dataset.GetFieldData()
    assert fields.GetNumberOfArrays() == 2
    metadata_array = fields.GetAbstractArray("__ai4e_npy_metadata")
    assert metadata_array.GetNumberOfValues() == 1
    metadata = json.loads(metadata_array.GetValue(0))
    assert metadata["schema_version"] == 1
    assert metadata["order"] == "C"
    values = fields.GetArray("values")
    assert values.GetNumberOfComponents() == 1
    return (
        vtk_to_numpy(values)
        .astype(np.dtype(metadata["dtype"]))
        .reshape(metadata["shape"], order=metadata["order"])
    )


@pytest.mark.parametrize(
    "dtype",
    [
        np.bool_,
        np.int8,
        np.uint8,
        np.int16,
        np.uint16,
        np.int32,
        np.uint32,
        np.int64,
        np.uint64,
        np.float32,
        np.float64,
    ],
)
def test_npy_dtype_boundaries(tmp_path: Path, dtype: type) -> None:
    """整数极值、布尔和浮点特殊值不因 VTK 转换而改变。"""
    if np.issubdtype(dtype, np.integer):
        limits = np.iinfo(dtype)
        expected = np.array([limits.min, 0, limits.max], dtype=dtype)
    elif np.issubdtype(dtype, np.floating):
        limits = np.finfo(dtype)
        expected = np.array(
            [limits.min, -0.0, limits.tiny, limits.max, np.nan, np.inf, -np.inf], dtype=dtype
        )
    else:
        expected = np.array([False, True], dtype=dtype)
    path = tmp_path / "array.npy"
    np.save(path, expected)
    dataset = read_file(path)
    gc.collect()
    restored = _restore_npy(dataset)
    assert restored.dtype == expected.dtype
    np.testing.assert_array_equal(restored, expected)
    if np.issubdtype(dtype, np.floating):
        np.testing.assert_array_equal(np.signbit(restored), np.signbit(expected))


@pytest.mark.parametrize(
    "expected",
    [
        np.array(7, dtype=np.int16),
        np.empty((0,), dtype=np.float32),
        np.empty((2, 0, 3), dtype=np.float64),
        np.arange(24, dtype=np.int32).reshape(2, 3, 4),
        np.asfortranarray(np.arange(12, dtype=np.float64).reshape(3, 4)),
        np.arange(12, dtype=np.int16).reshape(3, 4)[:, ::2],
        np.array([[1, 256], [-2, 1000]], dtype=np.dtype("int32").newbyteorder("S")),
        np.array([1.25, -2.5, np.inf], dtype=np.dtype("float64").newbyteorder("S")),
    ],
)
def test_npy_shape_order_and_endian(tmp_path: Path, expected: np.ndarray) -> None:
    """标量、空数组、高维、不同布局与字节序均保持逻辑索引和原 dtype。"""
    path = tmp_path / "array.npy"
    np.save(path, expected)
    restored = _restore_npy(read_file(path))
    assert restored.shape == expected.shape
    assert restored.dtype.str == expected.dtype.str
    np.testing.assert_array_equal(restored, expected)


@pytest.mark.parametrize(
    "dtype",
    [
        "complex64",
        "complex128",
        "U3",
        "S3",
        "object",
        "float16",
        "datetime64[D]",
        "timedelta64[D]",
        [("x", "i4"), ("y", "f8")],
    ],
)
def test_npy_unsupported_dtype_fails(tmp_path: Path, dtype: object) -> None:
    """无法保留的 dtype 明确失败，不允许 pickle 或静默数值降级。"""
    path = tmp_path / "unsupported.npy"
    np.save(path, np.zeros(2, dtype=dtype))
    with pytest.raises(ValueError, match=str(path)):
        read_file(path)


def test_npy_corrupt_and_disguised_archive_fail(tmp_path: Path) -> None:
    """损坏文件及伪装为 NPY 的 NPZ 不能被返回为数据对象。"""
    path = tmp_path / "corrupt.npy"
    path.write_bytes(b"not a numpy file")
    with pytest.raises(ValueError, match=str(path)):
        read_file(path)
    with path.open("wb") as stream:
        np.savez(stream, values=np.arange(3))
    with pytest.raises(ValueError, match=str(path)):
        read_file(path)


def test_npy_vtk_owns_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """源数组改变或释放均不影响 VTK 自有数据副本。"""
    from ai4e_core.abilities.data.source.adapter import npy

    path = _write_npy(tmp_path / "array.npy")
    original = np.array([10, 20], dtype=np.int64)
    monkeypatch.setattr(npy.np, "load", lambda *args, captured=original, **kwargs: captured)
    dataset = read_file(path)
    original[:] = -1
    monkeypatch.undo()
    del original
    gc.collect()
    np.testing.assert_array_equal(_restore_npy(dataset), [10, 20])


def test_adapter_must_return_vtk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """拒绝违反统一契约的 adapter，错误包含路径和格式。"""
    path = _write_npy(tmp_path / "array.npy")
    monkeypatch.setitem(read_mod.ADAPTERS, "npy", lambda _: np.zeros(2))
    for invoke in (
        lambda: read_file(path),
        lambda: read_many([path]),
        lambda: read_tree(tmp_path),
    ):
        with pytest.raises(TypeError, match="未返回 vtkDataObject") as error:
            invoke()
        assert str(path) in str(error.value)
        assert "(npy)" in str(error.value)


def test_read_tree_filters_and_explicit_format(tmp_path: Path) -> None:
    """保留递归开关、格式过滤、显式格式与输入顺序行为。"""
    top = _write_npy(tmp_path / "top.npy")
    folder = tmp_path / "nested"
    folder.mkdir()
    nested = _write_npy(folder / "nested.npy")
    _write_unstructured(tmp_path / "mesh.vtu")
    assert [p for p, _ in read_tree(tmp_path, recursive=False, format="npy")] == [top]
    assert [p for p, _ in read_tree(tmp_path, format="npy")] == sorted([top, nested])
    unknown = tmp_path / "array.bin"
    shutil.copyfile(top, unknown)
    _restore_npy(read_file(unknown, format="npy"))


def test_legacy_multiple_scalar_vector_arrays(tmp_path: Path) -> None:
    """Legacy 同类数组必须全部读取，且首个激活字段保持不变。"""
    path = tmp_path / "multiple.vtk"
    path.write_text("""# vtk DataFile Version 3.0
multiple arrays
ASCII
DATASET UNSTRUCTURED_GRID
POINTS 3 float
0 0 0 1 0 0 0 1 0
CELLS 1 4
3 0 1 2
CELL_TYPES 1
5
POINT_DATA 3
SCALARS pressure double 1
LOOKUP_TABLE default
1 2 3
SCALARS temperature double 1
LOOKUP_TABLE default
10 20 30
VECTORS velocity float
1 0 0 0 1 0 0 0 1
VECTORS auxiliary float
2 3 4 5 6 7 8 9 10
CELL_DATA 1
SCALARS material int 1
LOOKUP_TABLE default
7
SCALARS zone int 1
LOOKUP_TABLE default
9
""")
    mesh = read_file(path)
    gc.collect()
    points = mesh.GetPointData()
    assert points.GetScalars().GetName() == "pressure"
    assert points.GetVectors().GetName() == "velocity"
    np.testing.assert_array_equal(vtk_to_numpy(points.GetArray("temperature")), [10, 20, 30])
    np.testing.assert_array_equal(
        vtk_to_numpy(points.GetArray("auxiliary")), [[2, 3, 4], [5, 6, 7], [8, 9, 10]]
    )
    assert mesh.GetCellData().GetScalars().GetName() == "material"
    np.testing.assert_array_equal(vtk_to_numpy(mesh.GetCellData().GetArray("zone")), [9])
