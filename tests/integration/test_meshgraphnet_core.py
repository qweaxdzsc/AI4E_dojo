"""MeshGraphNet core-first 能力的合成图契约。"""

import pytest
import torch
from torch import nn

from ai4e_contrib.ability.model.meshgraphnet import MeshGraphNet
from ai4e_contrib.application.datasets.cylinder_flow.adapter import graph_sample
from ai4e_core.abilities.constraint.masked import masked_mse
from ai4e_core.abilities.eval.trajectory import horizon_mse
from ai4e_core.abilities.geometry.mesh_graph import edge_features
from ai4e_core.abilities.inference.rollout import rollout
from ai4e_core.abilities.modeling.modules.graph_message_passing import GraphMessagePassingBlock
from ai4e_core.abilities.training.graph_batch import concatenate_graphs
from ai4e_core.abilities.transform.noise import add_gaussian_noise
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer


def sample(nodes=4):
    position = torch.tensor([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])[:nodes]
    cells = torch.tensor([[0, 1, 2], [0, 2, 3]])
    velocity = torch.zeros(nodes, 2)
    node_type = torch.tensor([0, 1, 5, 2])[:nodes]
    return {"position": position, "cells": cells, "velocity": velocity, "node_type": node_type}


def test_graph_edges_features_and_variable_batch():
    graph = graph_sample(sample())
    assert graph["edge_index"].shape == (2, 10)
    assert graph["node_features"].shape == (4, 11)
    assert edge_features(graph["position"], graph["edge_index"]).shape == (10, 3)
    source, target = graph["edge_index"][:, 0]
    expected = graph["position"][source] - graph["position"][target]
    assert torch.equal(graph["edge_features"][0, :2], expected)
    batched = concatenate_graphs([graph, graph])
    assert batched["node_features"].shape == (8, 11)
    assert batched["edge_index"].max().item() == 7
    assert batched["node_batch"].tolist() == [0, 0, 0, 0, 1, 1, 1, 1]


def test_core_mask_noise_and_rollout():
    prediction = torch.ones(3, 2)
    target = torch.zeros(3, 2)
    assert masked_mse(prediction, target, torch.tensor([True, False, True])).item() == 1
    assert (
        masked_mse(
            prediction, target, torch.tensor([True, False, True]), feature_reduction="sum"
        ).item()
        == 2
    )
    noisy = add_gaussian_noise(target, 0.0)
    assert torch.equal(noisy, target)
    states = rollout(torch.zeros(2, 1), 2, lambda value, _: value + 1)
    assert states[:, 0, 0].tolist() == [0.0, 1.0, 2.0]
    metrics = horizon_mse(states.unsqueeze(0), torch.zeros_like(states).unsqueeze(0), (1, 2))
    assert metrics == {"mse_1_steps": 1.0, "mse_2_steps": 2.5}


def test_running_normalizer_matches_reference_std_epsilon_and_roundtrip():
    normalizer = RunningNormalizer(2)
    values = torch.tensor([[1.0, 4.0], [3.0, 4.0]])
    normalized = normalizer(values, accumulate=True)
    assert torch.allclose(normalized[:, 0], torch.tensor([-1.0, 1.0]))
    assert torch.equal(normalized[:, 1], torch.zeros(2))
    assert torch.allclose(normalizer.inverse(normalized), values)
    _, std = normalizer.statistics(values)
    assert std[1].item() == pytest.approx(normalizer.epsilon)


def test_meshgraphnet_forward_is_model_specific_but_core_graph_is_neutral():
    graph = graph_sample(sample())
    model = MeshGraphNet(hidden_dim=16, processor_layers=2)
    output = model(graph["node_features"], graph["edge_features"], graph["edge_index"])
    assert output.shape == (4, 2)
    assert torch.isfinite(output).all()


def test_message_passing_updates_edges_before_node_aggregation():
    block = GraphMessagePassingBlock(1, 1, 1, aggregation="sum")

    class EdgeUpdate(nn.Module):
        def forward(self, value):
            return torch.ones((value.shape[0], 1))

    class NodeUpdate(nn.Module):
        def forward(self, value):
            return value[:, 1:]

    block.edge_update = EdgeUpdate()
    block.node_update = NodeUpdate()
    nodes = torch.tensor([[2.0], [3.0]])
    edges = torch.tensor([[4.0]])
    updated_nodes, updated_edges = block(nodes, edges, torch.tensor([[0], [1]]))
    assert updated_edges.tolist() == [[5.0]]
    assert updated_nodes.tolist() == [[2.0], [8.0]]
