"""将 VTK 显示数据写成带摘要的二进制资产，不将大数组装入 JSON。"""

import hashlib
import json
import sys
from pathlib import Path


def write_display(
    dataset, output_dir: Path, *, source: dict, pipeline: list, generated=False, field_metadata=None
):
    """表面化显示并保留原始点单元映射，原子发布完整清单。"""
    import numpy as np
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    output_dir.mkdir(parents=True, exist_ok=True)
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(dataset)
    surface.PassThroughPointIdsOn()
    surface.PassThroughCellIdsOn()
    surface.Update()
    mesh = surface.GetOutput()
    if mesh.GetNumberOfPoints() == 0 and dataset.GetNumberOfPoints():
        mesh = vtk.vtkPolyData()
        mesh.SetPoints(dataset.GetPoints())
        mesh.GetPointData().ShallowCopy(dataset.GetPointData())
    if mesh.GetNumberOfCells() == 0 and mesh.GetNumberOfPoints():
        vertices = vtk.vtkCellArray()
        for i in range(mesh.GetNumberOfPoints()):
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(i)
        mesh.SetVerts(vertices)
    total = 0

    def buffer(name, array):
        nonlocal total
        a = np.ascontiguousarray(array)
        total += a.nbytes
        if total > 128 * 1024 * 1024:
            raise ValueError("display_asset_budget_exceeded")
        payload = a.tobytes()
        filename = hashlib.sha256(name.encode()).hexdigest()[:16] + ".bin"
        (output_dir / filename).write_bytes(payload)
        return {
            "name": name,
            "path": filename,
            "dtype": str(a.dtype),
            "shape": list(a.shape),
            "byte_order": (
                sys.byteorder
                if a.dtype.byteorder == "="
                else "big"
                if a.dtype.byteorder == ">"
                else "little"
            ),
            "byte_length": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    positions = (
        vtk_to_numpy(mesh.GetPoints().GetData()) if mesh.GetNumberOfPoints() else np.empty((0, 3))
    )
    geometry = [buffer("points", positions)]
    topology = []
    for name, cells in [
        ("polys", mesh.GetPolys()),
        ("lines", mesh.GetLines()),
        ("verts", mesh.GetVerts()),
    ]:
        if cells.GetNumberOfCells():
            connections = vtk_to_numpy(cells.GetData())
            if connections.size and connections.max() > np.iinfo(np.uint32).max:
                raise ValueError("topology_index_exceeds_browser_limit")
            topology.append(buffer(name, connections.astype("uint32")))
    fields = []
    for association, attrs in [("point", mesh.GetPointData()), ("cell", mesh.GetCellData())]:
        for index in range(attrs.GetNumberOfArrays()):
            arr = attrs.GetArray(index)
            if arr is None or (arr.GetName() or "").startswith(("vtkOriginal", "__dojo_original_")):
                continue
            values = vtk_to_numpy(arr)
            finite = np.isfinite(values)
            valid = finite.all(axis=1) if values.ndim > 1 else finite
            finite_values = values[finite]
            fields.append(
                {
                    "field_id": f"{association}:{arr.GetName()}",
                    "name": arr.GetName(),
                    "association": association,
                    "components": arr.GetNumberOfComponents(),
                    "unit": (field_metadata or {}).get("unit"),
                    "entity_set": (field_metadata or {}).get("entity_set"),
                    "buffer": buffer(f"{association}:{arr.GetName()}", values),
                    "validity": buffer(
                        f"{association}:{arr.GetName()}:validity", valid.astype("uint8")
                    ),
                    "component_ranges": [
                        [float(v[np.isfinite(v)].min()), float(v[np.isfinite(v)].max())]
                        if np.isfinite(v).any()
                        else None
                        for v in (values.T if values.ndim > 1 else [values])
                    ],
                    "magnitude_range": [
                        float(np.linalg.norm(values[valid], axis=1).min()),
                        float(np.linalg.norm(values[valid], axis=1).max()),
                    ]
                    if values.ndim > 1 and valid.any()
                    else None,
                    "range": [float(finite_values.min()), float(finite_values.max())]
                    if finite_values.size
                    else None,
                }
            )
    mapping = {"generated_entities": generated}
    if not generated:
        for association, attrs in [("point", mesh.GetPointData()), ("cell", mesh.GetCellData())]:
            arr = attrs.GetArray("__dojo_original_" + association)
            if arr is None:
                arr = attrs.GetArray(
                    "vtkOriginalPointIds" if association == "point" else "vtkOriginalCellIds"
                )
            if arr is not None:
                mapping[association] = buffer(f"identity:{association}", vtk_to_numpy(arr))
    # 坐标长度单位与物理场单位独立，只读取显式来源声明。
    coordinate_space = None
    declaration = (field_metadata or {}).get("coordinate_space")
    if declaration is None:
        attributes = dataset.GetFieldData()
        space_id = attributes.GetAbstractArray("coordinate_space_id")
        unit = attributes.GetAbstractArray("coordinate_space_unit")
        if space_id is not None or unit is not None:
            if not isinstance(space_id, vtk.vtkStringArray) or not isinstance(
                unit, vtk.vtkStringArray
            ):
                raise ValueError("invalid_coordinate_space_declaration")
            if space_id.GetNumberOfValues() != 1 or unit.GetNumberOfValues() != 1:
                raise ValueError("invalid_coordinate_space_declaration")
            declaration = {"id": space_id.GetValue(0), "unit": unit.GetValue(0)}
    if declaration is not None:
        if not isinstance(declaration, dict) or not all(
            isinstance(declaration.get(key), str) and declaration[key].strip()
            for key in ("id", "unit")
        ):
            raise ValueError("invalid_coordinate_space_declaration")
        coordinate_space = {
            "id": declaration["id"],
            "unit": declaration["unit"],
            "evidence": "source-declaration",
            "source_refs": [source],
        }
    manifest = {
        "schema_version": 1,
        "source_refs": [source],
        "pipeline": pipeline,
        "dataset_type": mesh.GetClassName(),
        "bounds": list(mesh.GetBounds()) if mesh.GetNumberOfPoints() else [],
        "geometry_buffers": geometry,
        "topology_buffers": topology,
        "fields": fields,
        "entity_mapping": mapping,
        "statistics": {
            "points": mesh.GetNumberOfPoints(),
            "cells": mesh.GetNumberOfCells(),
            "bytes": total,
        },
        "provenance": {"converter": "ai4e-viz-v1", "generated_entities": generated},
    }
    if coordinate_space is not None:
        manifest["coordinate_space"] = coordinate_space
    temp = output_dir / "manifest.json.tmp"
    temp.write_text(json.dumps(manifest, allow_nan=False), encoding="utf-8")
    temp.replace(output_dir / "manifest.json")
    return {**manifest, "manifest_path": "manifest.json"}
