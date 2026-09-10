"""正式多域网络的前向、反向与多样本隔离验收。"""

import copy

import pytest
import torch

from ai4e_contrib.ability.model.abupt.model import construct, predict


def specs(domains=("surface", "volume"), features=False, conditions=False):
    return {
        "position_dim": 3,
        "domains": {
            d: {"output_dims": {"value": i + 1}, "feature_dim": {"sdf": 1} if features else {}}
            for i, d in enumerate(domains)
        },
        "conditioning_dims": {"design": 2} if conditions else {},
    }


def make_model(data_specs=None, **kwargs):
    data_specs = data_specs or specs()
    return construct(
        data_specs=data_specs,
        dim=24,
        num_heads=3,
        geometry_depth=1,
        blocks="psc" if len(data_specs["domains"]) > 1 else "ps",
        num_domain_decoder_blocks={d: 1 for d in data_specs["domains"]},
        **kwargs,
    )


def inputs(data_specs=None, batch=1, queries=True):
    data_specs = data_specs or specs()
    positions = [torch.rand(8 + i, 3) for i in range(batch)]
    offsets, indices, offset = [], [], 0
    for i, pos in enumerate(positions):
        offsets.append(torch.full((len(pos),), i, dtype=torch.long))
        indices.append(torch.tensor([0, 2, 4, 6]) + offset)
        offset += len(pos)
    result = {
        "geometry_position": torch.cat(positions),
        "geometry_supernode_idx": torch.cat(indices),
        "geometry_batch_idx": torch.cat(offsets),
        "domain_anchor_positions": {
            d: torch.rand(batch, 3 + i, 3) for i, d in enumerate(data_specs["domains"])
        },
    }
    if queries:
        result["domain_query_positions"] = {
            d: torch.rand(batch, 5 + i, 3) for i, d in enumerate(data_specs["domains"])
        }
    for kind in ("anchor", "query"):
        values = {
            d: torch.rand(
                batch,
                result[f"domain_{kind}_positions"][d].shape[1],
                sum(v for v in s.get("feature_dim", {}).values()),
            )
            for d, s in data_specs["domains"].items()
            if s.get("feature_dim") and f"domain_{kind}_positions" in result
        }
        if values:
            result[f"domain_{kind}_features"] = values
    if data_specs.get("conditioning_dims"):
        result["conditioning_inputs"] = {
            k: torch.rand(batch, v) for k, v in data_specs["conditioning_dims"].items()
        }
    return result


def sample(batch, i):
    mask = batch["geometry_batch_idx"] == i
    offset = int(torch.where(mask)[0][0])
    index = batch["geometry_supernode_idx"]
    selected = batch["geometry_batch_idx"][index] == i
    return {
        "geometry_position": batch["geometry_position"][mask],
        "geometry_batch_idx": torch.zeros(int(mask.sum()), dtype=torch.long),
        "geometry_supernode_idx": index[selected] - offset,
        **{
            k: {d: t[i : i + 1] for d, t in v.items()}
            for k, v in batch.items()
            if isinstance(v, dict)
        },
    }


@pytest.mark.parametrize("domains", [("solid",), ("surface", "volume"), ("wall", "fluid", "wake")])
def test_real_domains_forward_backward(domains):
    data = specs(domains, features=True, conditions=True)
    model = make_model(data)
    batch = inputs(data)
    output = predict(model, batch)
    loss = sum(t.square().mean() for t in output.values())
    loss.backward()
    assert torch.isfinite(loss)
    assert len(output) == len(domains) * 2
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters())


@pytest.mark.parametrize("size", [2, 3])
def test_real_batch_matches_individual_outputs_and_gradients(size):
    torch.manual_seed(12)
    model = make_model()
    batch = inputs(batch=size)
    output = predict(model, batch)
    loss = sum(t.square().mean() for t in output.values())
    loss.backward()
    grad = {n: p.grad.clone() for n, p in model.named_parameters() if p.grad is not None}
    model.zero_grad()
    for i in range(size):
        single = predict(model, sample(batch, i))
        for name, t in single.items():
            torch.testing.assert_close(t, output[name][i : i + 1], rtol=1e-5, atol=1e-6)
        (sum(t.square().mean() for t in single.values()) / size).backward()
    for n, p in model.named_parameters():
        if n in grad:
            torch.testing.assert_close(p.grad, grad[n], rtol=1e-5, atol=1e-6)
    changed = copy.deepcopy(batch)
    changed["domain_anchor_positions"]["surface"][0].add_(2)
    for name, t in predict(model, changed).items():
        torch.testing.assert_close(t[1:], output[name][1:], rtol=1e-5, atol=1e-6)


def test_condition_starts_identity_then_learns_response():
    data = specs(features=True, conditions=True)
    model = make_model(data)
    batch = inputs(data)
    batch["conditioning_inputs"]["design"].requires_grad_()
    original = predict(model, batch)
    changed = copy.deepcopy(batch)
    changed["conditioning_inputs"]["design"] = torch.ones(1, 2) * 3
    for k, v in predict(model, changed).items():
        torch.testing.assert_close(v, original[k])
    for module in model.modules():
        from ai4e_contrib.ability.model.abupt.modules.blocks.domain import Modulation

        if isinstance(module, Modulation) and module.linear is not None:
            torch.nn.init.normal_(module.linear.weight, std=0.1)
    loss = sum(t.square().mean() for t in predict(model, batch).values())
    loss.backward()
    assert batch["conditioning_inputs"]["design"].grad.abs().sum() > 0


@pytest.mark.parametrize("geometry_dims", [None, {}, {"shape": 1}])
def test_features_and_geometry_conditions(geometry_dims):
    data = specs(features=True, conditions=True)
    model = make_model(data, geometry_conditioning_dims=geometry_dims)
    batch = inputs(data)
    feature = batch["domain_anchor_features"]["surface"].requires_grad_()
    if geometry_dims:
        batch["geometry_conditioning_inputs"] = {"shape": torch.ones(1, 1, requires_grad=True)}
    from ai4e_contrib.ability.model.abupt.modules.blocks.domain import Modulation

    for module in model.modules():
        if isinstance(module, Modulation) and module.linear is not None:
            torch.nn.init.normal_(module.linear.weight, std=0.1)
    sum(v.square().sum() for v in predict(model, batch).values()).backward()
    assert feature.grad.abs().sum() > 0
    if geometry_dims:
        assert batch["geometry_conditioning_inputs"]["shape"].grad.abs().sum() > 0
    elif geometry_dims is None:
        with pytest.raises(ValueError, match="继承"):
            predict(model, {**batch, "geometry_conditioning_inputs": {"design": torch.ones(1, 2)}})
