"""Darcy 的文件、字段、采样与目标绑定；计算由 core 提供。"""

from functools import partial

from ai4e_contrib.application.datasets.darcy_flow import DarcySource
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample
from ai4e_core.abilities.sampling.structured_grid import grid_faces, grid_indices
from ai4e_core.abilities.transform.field_encoding import (
    decode_scalar_field,
    encode_scalar_grid,
    preserve_geometry,
    scalar_statistics,
)

FIELDS = ["solution"]
UNITS = ["benchmark"]
TIMES = [0.0]
INPUT_NAMES = ("local_embedding", "geometry")
EVALUATION = "test"


def source(path):
    """公开 smooth1 前1000与 smooth2 前200。"""
    return DarcySource(path)


def extract(path, *, stride=5):
    """绑定 coeff/sol；共享实体索引连接坐标、输入和目标。"""
    record = read_mesh_sample(path)
    ids, shape = grid_indices(tuple(record["metadata"]["grid_shape"]), (stride, stride))
    return {
        "coeff": record["fields"]["point"]["coeff"][ids, None],
        "sol": record["fields"]["point"]["sol"][ids, None],
        "coordinates": record["points"][ids, :2],
        "entity_ids": record["point_ids"][ids],
        "faces": grid_faces(shape),
    }


def statistics(arrays):
    """选择参考的全局标量统计。"""
    return scalar_statistics(arrays, names=("coeff", "sol"))


def transform(arrays, stats):
    """选择坐标+系数输入、解目标和可复制几何。"""
    return preserve_geometry(
        encode_scalar_grid(
            arrays, stats, input_name="coeff", target_name="sol", coordinate_name="coordinates"
        ),
        arrays,
    )


def decoder(stats, *, physical):
    """Darcy 损失和评价均选物理空间解码。"""
    return partial(decode_scalar_field, stats=stats["sol"], physical=physical)


def objective_binding(stats):
    """目标字段身份，供公开训练步骤连接。"""
    return decoder(stats, physical=True), "physical_target"
