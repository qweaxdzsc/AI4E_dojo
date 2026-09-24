"""ShapeNet体速度到规则格的领域绑定，保留原网格与有效回贴范围。"""

from pathlib import Path

import numpy as np
import yaml

from ai4e_contrib.application.datasets.shapenet_car.adapter import MANIFEST_PATH
from ai4e_core.abilities.data.extract.mesh_probe import (
    probe_fields,
    probe_regular,
    regular_coordinates,
)
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample
from ai4e_core.abilities.geometry.surface import require_surface_mesh

FIELDS = ["velocity_x", "velocity_y", "velocity_z"]
UNITS = ["m/s"] * 3


class ShapeNetSource:
    """按官方训练/测试名单稳定排序选样本，保留体网格完整字段。"""

    def __init__(self, root, dataset):
        self.root = Path(root)
        splits = yaml.safe_load(MANIFEST_PATH.with_name("partition.yaml").read_text())
        self.selected = [
            {"id": value.replace("/", "__"), "source_id": value, "split": split}
            for split in ("train", "test")
            for value in sorted(splits[split])[: dataset[split + "_count"]]
        ]

    def samples(self):
        """返回来源ID与分片；不会以文件夹名字推断训练身份。"""
        return self.selected

    def read(self, sample):
        """读取发布体网格与表面，计算仅基于几何的无符号面距离。"""
        import pyvista as pv

        directory = self.root / sample["source_id"]
        mesh = pv.read(directory / "hexvelo_smpl.vtk")
        surface = pv.read(directory / "quadpress_smpl.vtk")
        require_surface_mesh(surface)
        if "point_vectors" not in mesh.point_data or np.asarray(mesh["point_vectors"]).shape != (
            mesh.n_points,
            3,
        ):
            raise ValueError("来源体速度字段不符")
        # 几何距离仅依赖来源表面，不从目标速度产生输入。
        mesh.point_data["surface_distance"] = np.abs(
            pv.PolyData(mesh.points).compute_implicit_distance(surface.extract_surface())[
                "implicit_distance"
            ]
        )
        return mesh, {
            "source_id": sample["source_id"],
            "units": dict(zip(FIELDS, UNITS, strict=True)),
        }


def source(root, dataset):
    """建立具有明确官方分片的来源。"""
    return ShapeNetSource(root, dataset)


def extract(path, dataset):
    """真实单元插值至每例物理包围盒；返回单独mask与C-order格点身份。"""
    item = read_mesh_sample(path, mesh=True)
    shape = (dataset["grid_size"],) * 3
    coordinates = regular_coordinates(item["mesh"].bounds, shape)
    arrays, mask = probe_fields(
        item["mesh"], coordinates.reshape(-1, 3), ("point_vectors", "surface_distance")
    )
    valid = mask.reshape(shape)
    if not valid.any():
        raise ValueError("体网格没有可监督规则格点")
    return {
        "input": np.concatenate(
            (coordinates, arrays["surface_distance"].reshape(*shape, 1), valid[..., None]), -1
        ),
        "target": arrays["point_vectors"].reshape(*shape, 3),
        "valid": valid,
        "entity_ids": np.arange(mask.size).reshape(shape),
    }


def back_project(coordinates, prediction, valid, physical):
    """显式回贴原实体，未受全部有效格点支撑的原点不纳入误差。"""
    item = read_mesh_sample(physical)
    values, mask = probe_regular(coordinates, prediction, valid, item["points"])
    return {
        "prediction": values,
        "target": item["fields"]["point"]["point_vectors"],
        "valid": mask,
        "entity_ids": item["point_ids"],
        "coordinates": item["points"],
    }
