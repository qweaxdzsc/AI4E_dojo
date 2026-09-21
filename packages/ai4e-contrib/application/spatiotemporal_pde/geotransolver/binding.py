"""保险杠时间、工况顺序和五通道语义连接，计算实现在 core。"""

from functools import partial

import numpy as np

from ai4e_contrib.application.datasets.bumper_beam import BumperSource
from ai4e_core.abilities.data.extract.time_series import mesh_trajectory
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample
from ai4e_core.abilities.transform.field_encoding import (
    decode_position_trajectory,
    encode_position_trajectory,
    position_statistics,
    preserve_geometry,
)

FIELDS = ["x", "y", "z", "effective_plastic_strain", "stress_vm"]
UNITS = ["mm", "mm", "mm", "1", "kg/(mm ms^2)"]
TIMES = list(range(10, 101, 10))
INPUT_NAMES = ("local_embedding", "local_positions", "geometry", "global_embedding")
EVALUATION = "validation"


def source(path):
    """选择公开124训练/7验证原始分片。"""
    return BumperSource(path)


def extract(path):
    """选择共同11帧，保留原文件额外帧，仅模型准备取共同窗口。"""
    record = read_mesh_sample(path, mesh=True)
    mesh = record["mesh"]
    positions, dynamic = mesh_trajectory(
        mesh,
        displacement_prefix="displacement_t",
        cell_prefixes=("cell_effective_plastic_strain_t", "cell_stress_vm_t"),
        requested=list(range(0, 101, 10)),
        zero_initial_displacement=True,
    )
    return {
        "positions": positions,
        "dynamic": dynamic,
        "conditions": np.asarray(record["metadata"]["global_values"], dtype=np.float32),
        "entity_ids": record["point_ids"],
        "faces": np.asarray(mesh.faces),
    }


def statistics(arrays):
    """选择参考的逐样本平方矩坐标统计。"""
    return position_statistics(arrays, name="positions")


def transform(arrays, stats):
    """绑定归一化坐标与未缩放的应变/应力。"""
    return preserve_geometry(
        encode_position_trajectory(
            arrays,
            stats,
            position_name="positions",
            dynamic_name="dynamic",
            condition_name="conditions",
        ),
        arrays,
    )


def decoder(stats, *, physical):
    """绑定10帧五通道，前三通道为需加回初态的位置。"""
    return partial(
        decode_position_trajectory,
        frames=10,
        channels=5,
        position_stats=stats["positions"],
        physical=physical,
    )


def objective_binding(stats):
    """MSE 在参考的归一化位置及原动态场空间计算。"""
    return decoder(stats, physical=False), "target"
