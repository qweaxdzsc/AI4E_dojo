"""core 能力独立使用及迁移数学对照。"""

import numpy as np
import pytest
import torch

from ai4e_core.abilities.constraint.relative_norm import relative_norm
from ai4e_core.abilities.geometry.radius_query import (
    BallQuery,
    build_radius_cache_arrays,
    gather_neighbors,
    install_prepared_queries,
    radius_indices,
)
from ai4e_core.abilities.modeling.modules.context_projection import (
    ContextProjector,
)
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock
from ai4e_core.abilities.modeling.weights import load_mapped_weights


def test_attention_without_contrib():
    torch.manual_seed(2)
    x = torch.randn(2, 12, 16, requires_grad=True)
    context = ContextProjector(16, heads=2, dim_head=8, slice_num=4, use_te=False)(x)
    block = GALEBlock(2, 16, 0.0, slice_num=4, context_dim=8)
    y = block((x,), context)[0]
    assert y.shape == x.shape
    y.square().mean().backward()
    assert torch.isfinite(x.grad).all()


def test_radius_reference_order_and_padding():
    from tools.verification.geotransolver.reference import load_reference

    reference = load_reference()
    torch.manual_seed(1)
    p = torch.randn(2, 17, 3)
    q = torch.randn(2, 13, 3)
    for k in (5, 21):
        i, v = radius_indices(p, q, 1.2, k, chunk_size=3)
        ri, rp = reference.radius_search(p, q, 1.2, k, return_points=True)
        assert torch.equal(i, ri)
        torch.testing.assert_close(gather_neighbors(p, i, v), rp, rtol=0, atol=0)


def test_prepared_neighbor_identity():
    x = np.random.default_rng(4).normal(size=(2, 12, 3)).astype("float32")
    arrays = {"local_positions": x, **build_radius_cache_arrays(x, radii=[1.0], neighbors=[5])}
    model = torch.nn.Sequential(BallQuery(1.0, 5))
    install_prepared_queries(
        model, arrays, radii=[1.0], neighbors=[5], cache_spec={"radii": [1.0], "neighbors": [5]}
    )
    p = torch.from_numpy(x[[1, 0]])
    i, points = model[0](p, p)
    ri, valid = radius_indices(p, p, 1.0, 5)
    assert torch.equal(i, ri)
    torch.testing.assert_close(points, gather_neighbors(p, ri, valid))
    with pytest.raises(ValueError, match="参数身份"):
        install_prepared_queries(
            model, arrays, radii=[2.0], neighbors=[5], cache_spec={"radii": [1.0], "neighbors": [5]}
        )
    arrays["local_positions"] = x + 1
    with pytest.raises(ValueError, match="身份"):
        install_prepared_queries(
            model, arrays, radii=[1.0], neighbors=[5], cache_spec={"radii": [1.0], "neighbors": [5]}
        )


def test_per_sample_norm_and_mapped_weight_validation():
    a = torch.tensor([[2.0], [20.0]])
    b = torch.tensor([[1.0], [10.0]])
    assert relative_norm(a, b) == 1
    with pytest.raises(ValueError):
        relative_norm(a, b * 0)
    m = torch.nn.Linear(2, 1)
    original = {k: v.clone() for k, v in m.state_dict().items()}
    load_mapped_weights(
        m, {"w": original["weight"], "b": original["bias"]}, mapping={"w": "weight", "b": "bias"}
    )
    with pytest.raises(ValueError):
        load_mapped_weights(m, {"x": torch.zeros(1)})
    for k, v in m.state_dict().items():
        assert torch.equal(v, original[k])


def test_public_unstructured_attention_defaults_to_plain_torch():
    from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionIrregularMesh

    layer = PhysicsAttentionIrregularMesh(16, heads=2, dim_head=8, slice_num=4)
    x = torch.randn(1, 7, 16)
    assert layer(x).shape == x.shape
    with pytest.raises(NotImplementedError):
        PhysicsAttentionIrregularMesh(16, use_te=True)
