"""读取 VTK 数据结构并保留块、点场、单元场和几何归属。"""

from pathlib import Path


def _read(path: Path, reader: str | None = None):
    import vtk

    readers = {
        ".vtk": vtk.vtkDataSetReader,
        ".vtp": vtk.vtkXMLPolyDataReader,
        ".vtu": vtk.vtkXMLUnstructuredGridReader,
        ".vtkhdf": vtk.vtkHDFReader,
        ".vtkh5": vtk.vtkHDFReader,
        ".h5": vtk.vtkHDFReader,
        ".hdf5": vtk.vtkHDFReader,
        ".vti": vtk.vtkXMLImageDataReader,
        ".vts": vtk.vtkXMLStructuredGridReader,
        ".vtr": vtk.vtkXMLRectilinearGridReader,
        ".vtm": vtk.vtkXMLMultiBlockDataReader,
        "vtkhdf": vtk.vtkHDFReader,
    }
    factory = readers.get(reader or path.suffix.lower())
    if not factory:
        raise ValueError("unsupported_mesh_format")
    reader = factory()
    reader.SetFileName(str(path))
    if path.suffix.lower() == ".vtk":
        reader.ReadAllScalarsOn()
        reader.ReadAllVectorsOn()
    reader.Update()
    data = reader.GetOutput()
    if data is None:
        raise ValueError("empty_or_invalid_mesh")
    return data


def _leaves(data):
    iterator = data.NewIterator()
    iterator.InitTraversal()
    leaves = []
    while not iterator.IsDoneWithTraversal():
        current = iterator.GetCurrentDataObject()
        if current is not None:
            leaves.append(current)
        iterator.GoToNextItem()
    return leaves


def read_mesh(path: Path, block: int | None = None, reader: str | None = None):
    """多块文件必须明确选择块，不默认合并不同物理域。"""
    mesh = _read(path, reader)
    if mesh.IsA("vtkCompositeDataSet"):
        leaves = _leaves(mesh)
        if block is None:
            raise ValueError("multiblock_requires_block_selection")
        if not 0 <= int(block) < len(leaves):
            raise ValueError("invalid_block_selection")
        mesh = leaves[int(block)]
    if not hasattr(mesh, "GetNumberOfPoints") or mesh.GetNumberOfPoints() == 0:
        raise ValueError("empty_or_invalid_mesh")
    return mesh


def _describe(mesh, prefix=""):
    fields = [
        {
            "id": prefix + "geometry:points",
            "field_id": prefix + "geometry:points",
            "name": "points",
            "association": "geometry",
            "shape": [mesh.GetNumberOfPoints(), 3],
            "dtype": "float",
            "components": 3,
            "unit": None,
        }
    ]
    for association, data in [
        ("point", mesh.GetPointData()),
        ("cell", mesh.GetCellData()),
        ("global", mesh.GetFieldData()),
    ]:
        for i in range(data.GetNumberOfArrays()):
            a = data.GetArray(i)
            if a is None:
                continue
            name = a.GetName() or f"array_{i}"
            fields.append(
                {
                    "id": f"{prefix}{association}:{name}",
                    "field_id": f"{prefix}{association}:{name}",
                    "name": name,
                    "association": association,
                    "shape": [a.GetNumberOfTuples(), a.GetNumberOfComponents()],
                    "dtype": a.GetDataTypeAsString(),
                    "components": a.GetNumberOfComponents(),
                    "unit": None,
                }
            )
    return {
        "kind": "mesh",
        "points": mesh.GetNumberOfPoints(),
        "cells": mesh.GetNumberOfCells(),
        "bounds": list(mesh.GetBounds()),
        "dataset_type": mesh.GetClassName(),
        "fields": fields,
    }


def inspect_mesh(path: Path, reader: str | None = None) -> dict:
    """检查实际字段和块目录；未知单位不猜测。"""
    mesh = _read(path, reader)
    if mesh.IsA("vtkCompositeDataSet"):
        blocks = [
            {"block": i, **_describe(part, f"block:{i}:")} for i, part in enumerate(_leaves(mesh))
        ]
        return {
            "kind": "mesh",
            "dataset_type": mesh.GetClassName(),
            "blocks": blocks,
            "fields": [],
            "requires_block_selection": True,
        }
    if not hasattr(mesh, "GetNumberOfPoints") or mesh.GetNumberOfPoints() == 0:
        raise ValueError("empty_or_invalid_mesh")
    return _describe(mesh)
