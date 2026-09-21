"""MeshGraphNet 多步推理连接。"""

from __future__ import annotations

import torch

from ai4e_contrib.application.datasets.cylinder_flow.adapter import graph_sample
from ai4e_core.abilities.geometry.mesh_graph import edge_features
from ai4e_core.abilities.inference.rollout import rollout


def evaluation_rollout_input(
    sample: dict, requested_steps: int | str
) -> tuple[dict, torch.Tensor, int]:
    """按 DeepMind ``add_targets`` 后的 CFD 评价窗口装配 rollout 输入。

    完整轨迹使用原始帧 ``1..T-2``；第一帧既是 rollout 初态也是评价中排除的
    初始帧。物理帧小样本可以显式提供 ``target_trajectory``。
    """
    velocity = sample["velocity"]
    if velocity.ndim == 3:
        target = velocity[1:-1]
        graph = graph_sample(
            {
                "position": sample["position"],
                "cells": sample["cells"],
                "node_type": sample["node_type"],
                "velocity": target[0],
                "sample_id": sample.get("sample_id", "trajectory"),
            }
        )
    else:
        graph = sample
        target = sample.get("target_trajectory")
        if target is None:
            available = int(requested_steps) if requested_steps != "all" else 1
            target = velocity.unsqueeze(0).repeat(available + 1, 1, 1)
    available = target.shape[0] - 1
    steps = available if requested_steps == "all" else int(requested_steps)
    if steps < 0:
        raise ValueError("infer.steps 不能为负")
    if steps > available:
        raise ValueError("infer.steps 超过目标轨迹可用时间长度")
    return graph, target[: steps + 1], steps


def rollout_prediction(
    model, graph: dict[str, torch.Tensor], steps: int, *, preserve: torch.Tensor | None = None
) -> torch.Tensor:
    """以速度增量作为模型输出执行 CylinderFlow 轨迹 rollout。"""
    position = graph["position"]
    node_type = graph["node_type"]
    initial = graph["velocity"]
    if preserve is None:
        preserve = (node_type != 0) & (node_type != 5)

    def advance(state: torch.Tensor, _step: int) -> torch.Tensor:
        one_hot = torch.nn.functional.one_hot(node_type, 9).to(state.dtype)
        node_features = torch.cat([state, one_hot], dim=-1)
        edges = graph["edge_index"]
        with torch.no_grad():
            delta = model(node_features, edge_features(position, edges), edges)
            delta = model.inverse_output(delta)
        return state + delta

    return rollout(initial, steps, advance, preserve=preserve)
