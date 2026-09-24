"""图原子能力的独立公式、拓扑及旧权重兼容测试，不更新优化器。"""

import copy

import pytest
import torch

from ai4e_core.abilities.geometry.grid_graph import grid_edges
from ai4e_core.abilities.geometry.mesh_graph import induced_subgraph
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.modules.graph_encoding import GraphEncoder, GraphReadout
from ai4e_core.abilities.modeling.modules.graph_message_passing import (
    GraphInteraction,
    GraphMessagePassingBlock,
    aggregate_messages,
)
from tools.verification.classic_networks import reference_interactions as reference


@pytest.mark.parametrize("reduction", ["sum", "mean"])
def test_graph_update_independent_forward_and_gradients(reduction):
    model = GraphInteraction(3, 4, 5, aggregation=reduction).double()
    other = copy.deepcopy(model)
    nodes = torch.randn(5, 3, dtype=torch.float64, requires_grad=True)
    edges = torch.randn(4, 4, dtype=torch.float64, requires_grad=True)
    nr, er = nodes.detach().clone().requires_grad_(), edges.detach().clone().requires_grad_()
    index = torch.tensor([[0, 1, 2, 3], [2, 2, 3, 1]])
    actual = model(nodes, edges, index)
    expected = reference.graph_interaction(other, nr, er, index)
    for a, b in zip(actual, expected, strict=True):
        torch.testing.assert_close(a, b, atol=1e-10, rtol=1e-8)
    sum(a.square().sum() for a in actual).backward()
    sum(a.square().sum() for a in expected).backward()
    for a, b in [
        (nodes, nr),
        (edges, er),
        *zip(model.parameters(), other.parameters(), strict=True),
    ]:
        torch.testing.assert_close(a.grad, b.grad, atol=1e-10, rtol=1e-8)


def test_graph_public_aggregation_and_injected_update():
    messages = torch.tensor([[1.0, 3.0], [3.0, 5.0]])
    target = torch.tensor([1, 1])
    assert aggregate_messages(messages, target, 3, reduction="mean").tolist() == [
        [0.0, 0.0],
        [2.0, 4.0],
        [0.0, 0.0],
    ]
    block = GraphInteraction(
        2, 2, 3, edge_update=lambda n, e, ix: e + 1, node_update=lambda n, m: n + m
    )
    nodes, edges = block(torch.zeros(3, 2), messages, torch.tensor([[0, 2], [1, 1]]))
    assert nodes.tolist() == [[0.0, 0.0], [6.0, 10.0], [0.0, 0.0]]
    assert edges.tolist() == [[2.0, 4.0], [4.0, 6.0]]


def test_graph_encoder_readout_empty_edges_and_public_feedforward():
    encoder = GraphEncoder(3, 2, 8).double()
    readout = GraphReadout(8, 1).double()
    nodes, edges = encoder(
        torch.randn(4, 3, dtype=torch.float64), torch.empty(0, 2, dtype=torch.float64)
    )
    assert nodes.shape == (4, 8) and edges.shape == (0, 8)
    readout(nodes).sum().backward()
    assert isinstance(encoder.nodes[0], FeedForward)
    assert isinstance(readout.network, FeedForward)


def test_old_graph_block_weight_keys_and_current_explicit_formula():
    old = GraphMessagePassingBlock(3, 4, 5).double()
    assert list(old.state_dict()) == [
        f"{side}.{index}.{field}"
        for side in ("edge_update", "node_update")
        for index in (0, 2, 4, 5)
        for field in ("weight", "bias")
    ]
    clone = GraphMessagePassingBlock(3, 4, 5).double()
    clone.load_state_dict(old.state_dict(), strict=True)
    n, e = torch.randn(4, 3, dtype=torch.float64), torch.randn(3, 4, dtype=torch.float64)
    index = torch.tensor([[0, 1, 2], [1, 2, 1]])
    new_edges = e + reference.dense(old.edge_update, torch.cat((n[index[0]], n[index[1]], e), -1))
    new_nodes = n + reference.dense(
        old.node_update, torch.cat((n, reference.aggregate(new_edges, index[1], 4)), -1)
    )
    actual = clone(n, e, index)
    torch.testing.assert_close(actual[0], new_nodes, atol=1e-10, rtol=1e-8)
    torch.testing.assert_close(actual[1], new_edges, atol=1e-10, rtol=1e-8)


@pytest.mark.parametrize("shape", [(2, 3), (2, 3, 4), (1, 1), (1, 2, 1)])
def test_grid_edges_exact_discrete_neighbors_and_induced_validity(shape):
    edges = grid_edges(shape)
    coordinates = torch.cartesian_prod(*(torch.arange(n) for n in shape))
    expected = {
        (i, j)
        for i, a in enumerate(coordinates)
        for j, b in enumerate(coordinates)
        if int((a - b).abs().sum()) == 1
    }
    assert set(map(tuple, edges.t().tolist())) == expected
    assert edges.shape[1] == len(expected)
    count = len(coordinates)
    ids = torch.arange(0, count, 2)
    local, mapping = induced_subgraph(edges, ids, node_count=count)
    assert torch.equal(mapping, ids)
    if local.numel():
        assert all(int(i) in ids for i in mapping[local].flatten())


@pytest.mark.parametrize("reduction", ["sum", "mean"])
def test_slot_reference_matches_independent_enumeration_values_and_gradients(reduction):
    target = torch.tensor([3, 1, 3, 1, 4, 3, 1, 0])
    messages = torch.randn(len(target), 7, dtype=torch.float64, requires_grad=True)
    other = messages.detach().clone().requires_grad_()
    layout = reference.adjacency_slots(target, 6)
    actual = reference.aggregate(messages, target, 6, reduction, layout=layout)
    expected = reference.aggregate_enumerated(other, target, 6, reduction)
    torch.testing.assert_close(actual, expected, atol=1e-10, rtol=1e-8)
    actual.square().sum().backward()
    expected.square().sum().backward()
    torch.testing.assert_close(messages.grad, other.grad, atol=1e-10, rtol=1e-8)
    assert layout[0].tolist()[3] == [0, 2, 5]
    assert layout[1].tolist() == [1, 3, 0, 3, 1, 0]
    empty = reference.aggregate(torch.empty(0, 7), torch.empty(0, dtype=torch.long), 3)
    assert empty.shape == (3, 7) and torch.equal(empty, torch.zeros(3, 7))
