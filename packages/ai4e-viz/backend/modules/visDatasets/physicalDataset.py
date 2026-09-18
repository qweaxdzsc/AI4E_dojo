"""完整网格、显式点云和时间数据读取；不使用预览抽稀结果计算。"""

import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

from modules.dataAssets import resolve_external

# 命名块清单只随文件身份变化；工作台每次刷新都问一次，不能每次从盘重读整网。
_NAMED_BLOCK_CACHE: dict[tuple, list[dict]] = {}


def _named_block_cache_key(path, reader: str | None):
    """路径、阅读器和修改时间共同决定缓存项，内容变了必须重新列出。"""
    resolved = Path(path)
    try:
        stat = resolved.stat()
        stamp = (stat.st_mtime_ns, stat.st_size)
    except OSError:
        stamp = (None, None)
    return (str(resolved), reader or "", stamp)


def source_times(binding: dict) -> list[float]:
    """读取明确时间清单，静态数据不虚构时间。"""
    path = Path(binding["path"])
    if path.suffix.lower() == ".pvd":
        return sorted({float(e.attrib["timestep"]) for e in ET.parse(path).iter("DataSet")})
    return sorted(float(x["time"]) for x in binding.get("frames", []))


def load_physical(source: dict, bindings: list[dict], time: float | None = None):
    """精确选择时间和块，数组必须声明几何与实体身份。"""
    binding = resolve_external(source, bindings)
    path = binding["path"]
    times = source_times(binding)
    if times:
        selected = times[0] if time is None else float(time)
        if selected not in times:
            raise ValueError("missing_time_frame")
        if path.suffix.lower() == ".pvd":
            entries = [
                e for e in ET.parse(path).iter("DataSet") if float(e.attrib["timestep"]) == selected
            ]
            part = source.get("part", 0)
            if part >= len(entries):
                raise ValueError("invalid_time_part")
            from infrastructure.storage.atomic import contained

            path = contained(path.parent, entries[part].attrib["file"])
        else:
            frame = next(f for f in binding["frames"] if float(f["time"]) == selected)
            path = Path(frame["path"])
            from modules.dataAssets import source_fingerprint

            if source_fingerprint(path) != frame["revision"]:
                raise ValueError("source_revision_mismatch")
    if source.get("geometry"):
        from ai4e_viz.pipeline.tensor_points import read_tensor_points

        mesh = read_tensor_points(path, source["geometry"])
    else:
        from ai4e_viz.inspect.mesh import read_mesh

        mesh = read_mesh(path, source.get("block"), source.get("reader"))
    for count, attributes in [
        (mesh.GetNumberOfPoints(), mesh.GetPointData()),
        (mesh.GetNumberOfCells(), mesh.GetCellData()),
    ]:
        for i in range(attributes.GetNumberOfArrays()):
            array = attributes.GetArray(i)
            if array is not None and array.GetNumberOfTuples() != count:
                raise ValueError("physical_field_entity_count_mismatch")
    return mesh, times


def describe_physical(mesh) -> dict:
    """按 VTK 修改时间复用画像，返回副本避免表单污染后续读取。"""
    stamp = mesh.GetMTime()
    cached = getattr(mesh, "_vis_profile", None)
    if cached is not None and cached[0] == stamp:
        return deepcopy(cached[1])
    fields = []
    for association, arrays in [("point", mesh.GetPointData()), ("cell", mesh.GetCellData())]:
        for i in range(arrays.GetNumberOfArrays()):
            a = arrays.GetArray(i)
            if a:
                fields.append(
                    {
                        "name": a.GetName(),
                        "association": association,
                        "components": a.GetNumberOfComponents(),
                        "range": list(a.GetRange(-1)),
                    }
                )
    profile = {
        "points": mesh.GetNumberOfPoints(),
        "cells": mesh.GetNumberOfCells(),
        "bounds": list(mesh.GetBounds()),
        "dimension": max(
            (mesh.GetCell(i).GetCellDimension() for i in range(mesh.GetNumberOfCells())), default=0
        ),
        "fields": fields,
    }
    mesh._vis_profile = (stamp, profile)
    return deepcopy(profile)


def list_named_blocks(path, reader: str | None = None) -> list[dict]:
    """只列出带名称的二维块，不把多块合并进显示网格。"""
    key = _named_block_cache_key(path, reader)
    cached = _NAMED_BLOCK_CACHE.get(key)
    if cached is not None:
        return [dict(item) for item in cached]

    from pathlib import Path

    import vtk
    from ai4e_viz.inspect.mesh import _read

    mesh = _read(Path(path), reader)
    if not mesh.IsA("vtkCompositeDataSet"):
        _NAMED_BLOCK_CACHE[key] = []
        return []
    iterator = mesh.NewIterator()
    iterator.InitTraversal()
    surfaces = []
    index = 0
    while not iterator.IsDoneWithTraversal():
        part = iterator.GetCurrentDataObject()
        meta = iterator.GetCurrentMetaData()
        name = ""
        if meta is not None and meta.Has(vtk.vtkCompositeDataSet.NAME()):
            name = meta.Get(vtk.vtkCompositeDataSet.NAME()) or ""
        iterator.GoToNextItem()
        current = index
        index += 1
        if part is None or not name or not hasattr(part, "GetNumberOfCells"):
            continue
        dimension = max(
            (part.GetCell(i).GetCellDimension() for i in range(part.GetNumberOfCells())),
            default=0,
        )
        if dimension > 2 or part.GetNumberOfPoints() <= 0:
            continue
        surfaces.append(
            {
                "block": current,
                "name": name,
                "dimension": dimension,
                "points": part.GetNumberOfPoints(),
                "cells": part.GetNumberOfCells(),
            }
        )
    _NAMED_BLOCK_CACHE[key] = [dict(item) for item in surfaces]
    return surfaces


def list_named_surfaces(path, mesh=None, reader: str | None = None) -> list[dict]:
    """授权文件中的命名二维块，以及当前网格上的文字分区。"""
    from modules.visEngine import list_named_regions

    items = []
    if path:
        for block in list_named_blocks(path, reader):
            items.append(
                {
                    "kind": "block",
                    "name": block["name"],
                    "index": block["block"],
                    "text": f"{block['name']}（网格块）",
                    "value": f"block:{block['block']}:{block['name']}",
                }
            )
    if mesh is not None:
        for region in list_named_regions(mesh):
            items.append(
                {
                    "kind": "patch",
                    "name": region["name"],
                    "text": f"{region['name']}（分区）",
                    "value": f"patch:{region['name']}",
                }
            )
    return items
