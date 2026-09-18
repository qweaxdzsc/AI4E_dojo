"""物理场图片、网格和采样表的原子文件输出，不写运行记录。"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np

from ai4e_core.abilities.data.save.arrays import atomic_path


def save_image(image: Any, path: str | Path) -> Path:
    """写出 RGB/RGBA PNG，拒绝错误尺寸、类型或后缀。"""
    from PIL import Image

    image = np.asarray(image)
    if image.ndim != 3 or image.shape[2] not in {3, 4} or image.dtype != np.uint8:
        raise ValueError("图片必须为 uint8 RGB/RGBA 数组")
    path = Path(path)
    if path.suffix.lower() != ".png":
        raise ValueError("图片输出只接受 PNG")
    with atomic_path(path) as temporary:
        Image.fromarray(image).save(temporary, format="PNG")
    return path


def save_mesh(mesh: Any, path: str | Path) -> Path:
    """以 VTP 或 VTU 保留数组和真实拓扑，禁止静默丢失体单元。"""
    from ai4e_core.abilities.postproc.visualization.fields import pyvista

    pv = pyvista()
    mesh, path = pv.wrap(mesh), Path(path)
    if path.suffix == ".vtp" and not isinstance(mesh, pv.PolyData):
        raise ValueError("VTP 只接受 PolyData，不能自动抽取体外壳")
    if path.suffix == ".vtu":
        mesh = mesh.cast_to_unstructured_grid()
    elif path.suffix != ".vtp":
        raise ValueError("网格输出只接受 VTP/VTU")
    # PyVista 按后缀选择 writer，因此临时名必须保留原文件后缀。
    with atomic_path(path) as temporary:
        import vtk

        writer = (
            vtk.vtkXMLPolyDataWriter()
            if path.suffix == ".vtp"
            else vtk.vtkXMLUnstructuredGridWriter()
        )
        writer.SetFileName(str(temporary))
        writer.SetInputData(mesh)
        if writer.Write() != 1 or not temporary.stat().st_size:
            raise OSError("物理网格保存失败")
    return path


def save_profile(profile: dict, path: str | Path) -> Path:
    """采样表保留域外点和完整分量，无效数据列留空。"""
    names, columns = [], []
    for name, values in profile["fields"].items():
        values = np.asarray(values)
        matrix = values[:, None] if values.ndim == 1 else values
        for component in range(matrix.shape[1]):
            names.append(name if matrix.shape[1] == 1 else f"{name}.{component}")
            columns.append(matrix[:, component])
    with (
        atomic_path(Path(path)) as temporary,
        temporary.open("w", newline="", encoding="utf-8") as stream,
    ):
        writer = csv.writer(stream)
        writer.writerow(["index", "x", "y", "z", "distance", "valid", *names])
        for i, point in enumerate(profile["positions"]):
            valid = bool(profile["valid"][i])
            writer.writerow(
                [
                    i,
                    *point,
                    profile.get("distance", [None] * len(profile["positions"]))[i],
                    valid,
                    *(column[i] if valid else None for column in columns),
                ]
            )
    return Path(path)
