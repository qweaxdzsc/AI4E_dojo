"""Darcy静态系数到解场的来源、同实体采样与监督字段绑定。"""

import numpy as np

from ai4e_contrib.application.datasets.darcy_flow import DarcySource
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample
from ai4e_core.abilities.sampling.structured_grid import grid_indices

FIELDS = ["solution"]
UNITS = ["benchmark"]


def source(root, dataset):
    """固定smooth1训练/smooth2测试，计数显式传入。"""
    return DarcySource(
        root, train_count=dataset["train_count"], evaluation_count=dataset["test_count"]
    )


def extract(path, dataset):
    """按相同C-order原ID取坐标、系数和解，85²保留边界。"""
    item = read_mesh_sample(path)
    ids, shape = grid_indices(tuple(item["metadata"]["grid_shape"]), (dataset["stride"],) * 2)
    x = np.concatenate((item["points"][ids, :2], item["fields"]["point"]["coeff"][ids, None]), -1)
    return {
        "input": x.reshape(*shape, 3),
        "target": item["fields"]["point"]["sol"][ids].reshape(*shape, 1),
        "valid": np.ones(shape, bool),
        "entity_ids": ids.reshape(shape),
    }
