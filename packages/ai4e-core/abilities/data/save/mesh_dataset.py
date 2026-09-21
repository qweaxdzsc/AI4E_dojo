"""物理网格样本逐场 PT、VTKHDF、实体身份与可搬移清单。"""

import json
from pathlib import Path

import numpy as np
import torch

from .array_manifest import digest
from .arrays import save_json
from .store import write_named_tensors
from .vtkhdf import write_vtkhdf


def save_mesh_sample(directory, mesh, *, metadata: dict):
    """原子提交完整网格与原始 point/cell 字段；不转换字段关联。"""
    directory = Path(directory)
    payloads = {
        "points": torch.from_numpy(np.asarray(mesh.points).copy()),
        "point_ids": torch.arange(mesh.n_points),
        "cell_ids": torch.arange(mesh.n_cells),
    }
    fields = {}
    vtk_mesh = mesh.copy(deep=True)
    vtk_mesh.clear_data()
    for association, attributes, count in (
        ("point", mesh.point_data, mesh.n_points),
        ("cell", mesh.cell_data, mesh.n_cells),
    ):
        for name in attributes:
            values = np.asarray(attributes[name])
            if (
                len(values) != count
                or values.dtype.kind not in "biuf"
                or not np.isfinite(values).all()
            ):
                raise ValueError(f"非法物理场 {name}")
            key = f"field_{len(fields):04d}"
            payloads[key] = torch.from_numpy(values.copy())
            fields[key] = {
                "name": name,
                "vtk_name": key,
                "association": association,
                "shape": list(values.shape),
            }
            getattr(vtk_mesh, association + "_data")[key] = values
    filemap = {key: key + ".pt" for key in payloads}
    write_named_tensors(
        directory,
        payloads,
        filemap,
        extra_writers={"mesh.vtkhdf": lambda path: write_vtkhdf(path, vtk_mesh)},
    )
    record = {
        "kind": "named-mesh-sample-v1",
        "metadata": metadata,
        "fields": fields,
        "files": {
            key: {"path": name, "sha256": digest(directory / name)} for key, name in filemap.items()
        },
        "mesh": {"path": "mesh.vtkhdf", "sha256": digest(directory / "mesh.vtkhdf")},
    }
    save_json(directory / "manifest.json", record)
    return str(directory / "manifest.json")


def read_mesh_sample(path, *, mesh=False):
    """核验逐场摘要与实体数量，返回原物理字段；需要时读网格。"""
    path = Path(path).resolve()
    record = json.loads(path.read_text())
    if record["kind"] != "named-mesh-sample-v1":
        raise ValueError("物理样本版本不匹配")
    arrays = {}
    for key, entry in {**record["files"], "mesh": record["mesh"]}.items():
        file = (path.parent / entry["path"]).resolve()
        if not file.is_relative_to(path.parent) or digest(file) != entry["sha256"]:
            raise ValueError("物理样本内容或路径改变")
        if key != "mesh":
            arrays[key] = torch.load(file, weights_only=True).numpy()
    fields = {"point": {}, "cell": {}}
    for key, info in record["fields"].items():
        values = arrays[key]
        if list(values.shape) != info["shape"] or len(values) != len(
            arrays[info["association"] + "_ids"]
        ):
            raise ValueError("物理场身份/数量不一致")
        fields[info["association"]][info["name"]] = values
    result = {
        "metadata": record["metadata"],
        "points": arrays["points"],
        "point_ids": arrays["point_ids"],
        "cell_ids": arrays["cell_ids"],
        "fields": fields,
    }
    if mesh:
        import pyvista as pv

        result["mesh"] = pv.read(path.parent / record["mesh"]["path"])
        # VTKHDF 不允许字段名含点/斜线；清单保留原名，按逐场 PT 恢复科学名称。
        result["mesh"].clear_data()
        for association, values in fields.items():
            for name, value in values.items():
                getattr(result["mesh"], association + "_data")[name] = value
    return result


def read_mesh_dataset(path):
    """解析相对样本引用并校验清单摘要，禁止跨目录引用。"""
    path = Path(path).resolve()
    record = json.loads(path.read_text())
    if record["kind"] != "named-mesh-dataset-v1":
        raise ValueError("物理数据集版本不匹配")
    entries = []
    for entry in record["samples"]:
        child = (path.parent / entry["path"]).resolve()
        if not child.is_relative_to(path.parent) or digest(child) != entry["sha256"]:
            raise ValueError("物理样本清单改变")
        entries.append({**entry, "path": str(child)})
    return entries
