"""NASA 原始表面转换为模型无关的具名物理张量。"""

import torch

from ai4e_core.abilities.data.source.physical import PhysicalView

LAYOUT = {
    "domains": {
        "surface": {
            "position": "surface_position",
            "ids": "surface_ids",
            "fields": {
                "pressure_coefficient": "surface_cp",
                "friction_coefficient": "surface_cf",
                "normals": "surface_normals",
                "area": "surface_area",
            },
        }
    },
    "conditions": {"conditions": 6},
}


def open_physical(config: dict) -> PhysicalView:
    """打开物理 PT；模型选择不影响数据布局。"""
    path = (config.get("train") or {}).get("manifest")
    if not path:
        raise ValueError("train.manifest: 需要已有物理数据清单")
    return PhysicalView(path, layout=LAYOUT)


def physical_fields(arrays: dict) -> dict[str, torch.Tensor]:
    """原始浮点转换沿用读取组件，标签拆分只改变逻辑视图。"""
    values = {
        "surface_position": arrays["points"],
        "surface_normals": arrays["normals"],
        "surface_cp": arrays["labels"][:, :1],
        "surface_cf": arrays["labels"][:, 1:],
        "surface_area": arrays["area"][:, None],
        "conditions": arrays["conditions"][None],
        "global_targets": arrays["global_targets"][None],
    }
    return {
        **{k: torch.from_numpy(v.copy()) for k, v in values.items()},
        "surface_ids": torch.arange(len(arrays["points"]), dtype=torch.int64),
    }


def comparison_mesh(config: dict, sample: str, domain: str, points):
    """按 NASA 官方连接关系创建表面；不创建体场。"""
    from pathlib import Path

    import numpy as np
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

    from .topology import reconstruct_surface_topology

    if domain != "surface":
        raise ValueError("NASA CRM 来源没有体积域")
    topology = reconstruct_surface_topology(Path(config["dataset"]["connectivity_h5"]))
    if len(points) != topology.point_count:
        raise ValueError("NASA 完整点数与拓扑不一致")
    faces = np.concatenate(
        [
            np.column_stack((np.full(len(v), v.shape[1], dtype=np.int64), v)).ravel()
            for v in (topology.triangles, topology.quads)
        ]
    )
    mesh = vtk.vtkPolyData()
    coords = vtk.vtkPoints()
    coords.SetData(numpy_to_vtk(points, deep=True))
    mesh.SetPoints(coords)
    cells = vtk.vtkCellArray()
    cells.SetCells(topology.face_count, numpy_to_vtkIdTypeArray(faces, deep=True))
    mesh.SetPolys(cells)
    return mesh


def read_physical_field(raw, partition: str, sample: str, name: str):
    """读取检查目录中明确选择的原始数值点字段，不猜测物理语义。"""
    import h5py
    import numpy as np

    source = raw.sources["test" if partition == "test" else "training"]["path"]
    with h5py.File(source, "r") as stream:
        if name not in stream[sample]:
            raise ValueError(f"NASA 来源字段不存在: {name}")
        values = np.asarray(stream[sample][name][:])
    if values.ndim != 1 or len(values) != raw.point_count or not np.isfinite(values).all():
        raise ValueError(f"NASA 点字段形状或数值非法: {name}")
    return torch.from_numpy(values.copy())


def comparison_metadata(config, sample, domain):
    """提供来源拓扑身份与已知物理单位，未知单位不猜测。"""
    from pathlib import Path

    from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint

    path = Path(config["dataset"]["connectivity_h5"])
    units = {"surface_cp": "1", "surface_cf": "1"}
    units.update(config["dataset"].get("field_units", {}))
    if not path.is_file():
        return {"topology": None, "entity_set": None, "units": units}
    topology = file_fingerprint(path)
    return {
        "topology": topology,
        "entity_set": fingerprint(
            {"path": str(path.resolve()), "sample": sample["identity"]["sample"], "domain": domain}
        ),
        "units": units,
    }
