# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""确定性半径查询；保留 PhysicsNeMo torch 回退的距离、排序及零填充语义。"""

from __future__ import annotations

import torch
from torch import nn


def radius_indices(
    points: torch.Tensor,
    queries: torch.Tensor,
    radius: float,
    max_points: int,
    *,
    chunk_size: int = 256,
):
    """返回 [B,Q,K] 索引和有效性；MPS 查询显式在 CPU 执行。

    为对照兼容，N<K 的补位与参考相同，索引零且距离零（视作有效）。
    不把距离超界与有效的第零号点混淆。查询不参与坐标梯度。
    """
    if points.ndim != 3 or queries.ndim != 3 or points.shape[0] != queries.shape[0]:
        raise ValueError("坐标须为相同批次的 [B,N,3]/[B,Q,3]")
    if points.shape[-1] != 3 or queries.shape[-1] != 3 or points.shape[1] == 0:
        raise ValueError("坐标末轴须为3且来源非空")
    if radius < 0 or max_points < 1 or chunk_size < 1 or queries.shape[1] == 0:
        raise ValueError("半径、邻居数、查询数或分块非法")
    if not torch.isfinite(points).all() or not torch.isfinite(queries).all():
        raise ValueError("坐标非有限")
    device = points.device
    p, q = points.detach(), queries.detach()
    if device.type == "mps":
        p, q = p.cpu(), q.cpu()
    indices, masks = [], []
    for start in range(0, q.shape[1], chunk_size):
        d = torch.cdist(
            p, q[:, start : start + chunk_size], compute_mode="donot_use_mm_for_euclid_dist"
        )
        v, i = torch.topk(d, min(max_points, p.shape[1]), dim=1, largest=False)
        if p.shape[1] < max_points:
            pad = (0, 0, 0, max_points - p.shape[1])
            v = torch.nn.functional.pad(v, pad)
            i = torch.nn.functional.pad(i, pad)
        valid = v <= radius
        indices.append(torch.where(valid, i, 0).transpose(1, 2))
        masks.append(valid.transpose(1, 2))
    return torch.cat(indices, 1).to(device), torch.cat(masks, 1).to(device)


def gather_neighbors(points: torch.Tensor, indices: torch.Tensor, valid: torch.Tensor):
    """按索引取邻域坐标并屏蔽超界点；保留来源坐标的梯度。"""
    batch = torch.arange(points.shape[0], device=points.device)[:, None, None]
    return points[batch, indices] * valid[..., None]


class BallQuery(nn.Module):
    """按参考方向查询；缓存由调用方按身份校验后显式注入，不进入权重。"""

    def __init__(
        self, radius: float = 0.25, neighbors_in_radius: int = 10, *, chunk_size: int = 256
    ):
        super().__init__()
        self.radius, self.neighbors_in_radius = radius, neighbors_in_radius
        self.chunk_size = chunk_size
        self.lookup = None

    def forward(self, x: torch.Tensor, p_grid: torch.Tensor, reverse_mapping: bool = True):
        """返回索引和邻域坐标；reverse_mapping=True 时从 x 查 p_grid。"""
        if p_grid.ndim not in (3, 4, 5):
            raise ValueError("查询网格维数须为3、4或5")
        p_grid = p_grid.reshape(p_grid.shape[0], -1, p_grid.shape[-1])
        points, queries = (x, p_grid) if reverse_mapping else (p_grid, x)
        if self.lookup is None:
            indices, valid = radius_indices(
                points, queries, self.radius, self.neighbors_in_radius, chunk_size=self.chunk_size
            )
        else:
            indices, valid = self.lookup(points, queries, self.radius, self.neighbors_in_radius)
        return indices, gather_neighbors(points, indices, valid)


def coordinate_digest(value):
    """固定 float32 坐标身份，用于与可搬移邻域缓存匹配。"""
    import hashlib

    import numpy as np

    if isinstance(value, torch.Tensor):
        value = value.detach().cpu().numpy()
    array = np.ascontiguousarray(value, dtype=np.float32)
    return hashlib.sha256(array.tobytes()).hexdigest()


def build_radius_cache_arrays(coordinates, *, radii, neighbors):
    """对每个来源点集预计算自查询索引与有效性，缓存不含学习特征。"""
    import numpy as np

    if len(radii) != len(neighbors):
        raise ValueError("半径/邻居数不一致")
    result = {}
    result["neighbor_identity"] = np.stack(
        [np.frombuffer(bytes.fromhex(coordinate_digest(x)), dtype=np.uint8) for x in coordinates]
    )
    for scale, (radius, k) in enumerate(zip(radii, neighbors, strict=True)):
        entries = [
            radius_indices(
                torch.from_numpy(x.copy())[None], torch.from_numpy(x.copy())[None], radius, k
            )
            for x in coordinates
        ]
        result[f"neighbor_indices_{scale}"] = torch.cat([i for i, _ in entries]).numpy()
        result[f"neighbor_valid_{scale}"] = torch.cat([v for _, v in entries]).numpy()
    return result


def install_prepared_queries(model, arrays, *, radii, neighbors, cache_spec):
    """给普通 BallQuery 注入具身份的准备索引；坐标或参数不匹配明确报错。"""
    import numpy as np

    specs = list(zip(radii, neighbors, strict=True))
    stored = list(zip(cache_spec["radii"], cache_spec["neighbors"], strict=True))
    if specs != stored:
        raise ValueError("邻域缓存参数身份不匹配")
    shape = arrays["local_positions"].shape[:2]
    for scale, (_, count) in enumerate(specs):
        indices = arrays[f"neighbor_indices_{scale}"]
        valid = arrays[f"neighbor_valid_{scale}"]
        if indices.shape != (*shape, count) or valid.shape != indices.shape:
            raise ValueError("邻域缓存形状不匹配")
        if indices.dtype.kind not in "iu" or np.any(indices < 0) or np.any(indices >= shape[1]):
            raise ValueError("邻域缓存索引越界")
    keys = [coordinate_digest(x) for x in arrays["local_positions"]]
    for index, key in enumerate(keys):
        if bytes(np.asarray(arrays["neighbor_identity"][index])).hex() != key:
            raise ValueError("邻域坐标身份不匹配")
    lookup = {key: i for i, key in enumerate(keys)}

    def query(points, queries, radius, k):
        if not torch.equal(points, queries):
            raise ValueError("该缓存仅为同一点集的自查询")
        scale = specs.index((radius, k))
        indices = [lookup[coordinate_digest(x)] for x in points]
        i = torch.from_numpy(np.array(arrays[f"neighbor_indices_{scale}"][indices], copy=True)).to(
            points.device
        )
        v = torch.from_numpy(np.array(arrays[f"neighbor_valid_{scale}"][indices], copy=True)).to(
            points.device
        )
        return i, v

    for module in model.modules():
        if isinstance(module, BallQuery):
            if (module.radius, module.neighbors_in_radius) not in specs:
                raise ValueError("邻域参数与模型不匹配")
            module.lookup = query
