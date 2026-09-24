"""完整交互网络可拆装、排列/批次隔离和检查点读回；不训练。"""

import copy

import pytest
import torch
from torch import nn

from ai4e_core.abilities.geometry.grid_graph import grid_edges
from ai4e_core.abilities.geometry.mesh_graph import edge_features
from ai4e_core.abilities.modeling.models.gnn import GraphNetwork
from ai4e_core.abilities.modeling.models.transformer import PatchTransformer
from ai4e_core.abilities.modeling.modules.patch_embedding import patch_centers
from tools.verification.classic_networks import reference_interactions as reference


@pytest.mark.parametrize("shape,patch,channels", [((7, 9), (5, 5), 3), ((5, 6, 7), (4, 4, 4), 5)])
def test_patch_transformer_recomposition_and_checkpoint(tmp_path, shape, patch, channels):
    model = PatchTransformer(
        channels, 1, patch_shape=patch, dim=16, num_heads=4, num_layers=2, feed_forward_dim=32
    ).double()
    x = torch.randn(2, *shape, channels, dtype=torch.float64, requires_grad=True)
    valid = torch.ones(2, *shape, dtype=torch.bool)
    valid[(0, *([0] * len(shape)))] = False
    output = model(x, valid)
    tokens, mask, info = model.embedding(x, valid)
    positions = model.position_encoding(patch_centers(info, device=x.device, dtype=x.dtype)).to(
        tokens.dtype
    )
    independent = tokens + positions
    for block in model.encoder.blocks:
        independent = reference.encoder_block(block, independent, key_padding_mask=mask)
    expected = model.reconstruction(independent, info).masked_fill(~valid.unsqueeze(-1), 0)
    torch.testing.assert_close(output, expected, atol=1e-10, rtol=1e-8)
    assert output.shape == (2, *shape, 1) and torch.isfinite(output).all()
    output.square().sum().backward()
    assert torch.isfinite(x.grad).all()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    path = tmp_path / "state.pt"
    torch.save(model.state_dict(), path)
    clone = copy.deepcopy(model)
    clone.load_state_dict(torch.load(path, weights_only=True), strict=True)
    torch.testing.assert_close(clone(x, valid), output, atol=0, rtol=0)


@pytest.mark.parametrize("aggregation", ["sum", "mean"])
def test_graph_network_independent_recomposition_permutation_and_batch(aggregation, tmp_path):
    model = GraphNetwork(
        3, 3, 2, hidden_dim=8, processor_layers=3, aggregation=aggregation
    ).double()
    index = grid_edges((2, 3))
    positions = torch.cartesian_prod(torch.arange(2), torch.arange(3)).double()
    edges = edge_features(positions, index)
    nodes = torch.randn(6, 3, dtype=torch.float64)
    output = model(nodes, edges, index)
    expected = reference.graph_network(model, nodes, edges, index)
    torch.testing.assert_close(output, expected, atol=1e-10, rtol=1e-8)
    encoded_n, encoded_e = model.encoder(nodes, edges)
    processed_n, _ = model.processor(encoded_n, encoded_e, index)
    torch.testing.assert_close(model.readout(processed_n), output, atol=0, rtol=0)
    permutation = torch.tensor([4, 1, 3, 5, 0, 2])
    inverse = torch.argsort(permutation)
    changed = model(nodes[permutation], edges, inverse[index])
    torch.testing.assert_close(changed[inverse], output, atol=1e-10, rtol=1e-8)
    batched = model(
        torch.cat((nodes, nodes + 10)), torch.cat((edges, edges)), torch.cat((index, index + 6), 1)
    )
    torch.testing.assert_close(batched[:6], output, atol=1e-10, rtol=1e-8)
    torch.testing.assert_close(batched[6:], model(nodes + 10, edges, index), atol=1e-10, rtol=1e-8)
    output.sum().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    path = tmp_path / "graph.pt"
    torch.save(model.state_dict(), path)
    clone = copy.deepcopy(model)
    clone.load_state_dict(torch.load(path, weights_only=True), strict=True)
    torch.testing.assert_close(clone(nodes, edges, index), output, atol=0, rtol=0)


def test_graph_empty_edges_and_readout_replacement():
    model = GraphNetwork(2, 3, 1, hidden_dim=8, processor_layers=1)
    nodes, edges, index = torch.randn(4, 2), torch.empty(0, 3), torch.empty(2, 0, dtype=torch.long)
    assert model(nodes, edges, index).shape == (4, 1)
    model.readout = nn.Linear(8, 2)
    assert model(nodes, edges, index).shape == (4, 2)


def test_reference_scope_is_explicit():
    assert reference.SOURCE_IDENTITY["paper_reproduction"] is False
    assert (
        reference.SOURCE_IDENTITY["graph_variant"]
        == "aggregate_residual_updated_edges_then_residual_node_update"
    )


@pytest.mark.parametrize("kind", ["patch2d", "patch3d", "graph"])
def test_complete_independent_reference_adapter_parameter_and_input_gradients(kind):
    torch.manual_seed(402)
    if kind.startswith("patch"):
        shape, patch = ((3, 5), (2, 3)) if kind == "patch2d" else ((3, 3, 3), (2, 2, 2))
        model = PatchTransformer(
            3, 2, patch_shape=patch, dim=12, num_heads=3, num_layers=1, feed_forward_dim=16
        ).double()
        x = torch.randn(1, *shape, 3, dtype=torch.float64, requires_grad=True)
        valid = torch.ones(1, *shape, dtype=torch.bool)
        valid[(0, *([0] * len(shape)))] = False
        inputs = (x, valid)
        ref_inputs = (x.detach().clone().requires_grad_(), valid)
    else:
        model = GraphNetwork(3, 2, 2, hidden_dim=8, processor_layers=2).double()
        x = torch.randn(4, 3, dtype=torch.float64, requires_grad=True)
        edges = torch.randn(3, 2, dtype=torch.float64)
        index = torch.tensor([[0, 1, 2], [1, 2, 3]])
        inputs, ref_inputs = (x, edges, index), (x.detach().clone().requires_grad_(), edges, index)
    independent = reference.reference_model(model)
    assert model.state_dict().keys() == independent.state_dict().keys()
    output, expected = model(*inputs), independent(*ref_inputs)
    torch.testing.assert_close(output, expected, atol=1e-10, rtol=1e-8)
    output.square().sum().backward()
    expected.square().sum().backward()
    torch.testing.assert_close(x.grad, ref_inputs[0].grad, atol=1e-10, rtol=1e-8)
    for parameter, other in zip(model.parameters(), independent.parameters(), strict=True):
        torch.testing.assert_close(parameter.grad, other.grad, atol=1e-10, rtol=1e-8)
