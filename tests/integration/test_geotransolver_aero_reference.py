"""独立上游多流前向、梯度及更新的数值对照，不调用 Dojo 参考算子。"""

import pytest
import torch

from ai4e_contrib.ability.model.geotransolver import GeoTransolver
from ai4e_contrib.application.geotransolver import build_optimizer
from tools.verification.geotransolver.reference import load_reference, reference_optimizer


@pytest.mark.parametrize("dims,outputs,global_dim", [((6, 7), (1, 3), None), ((6,), (4,), 6)])
def test_independent_forward_gradient_update(dims, outputs, global_dim):
    torch.set_num_threads(2)
    torch.manual_seed(42)
    options = {
        "functional_dim": dims,
        "out_dim": outputs,
        "geometry_dim": 3,
        "global_dim": global_dim,
        "n_layers": 2,
        "n_hidden": 16,
        "n_head": 2,
        "slice_num": 4,
        "mlp_ratio": 2,
        "use_te": False,
    }
    dojo = GeoTransolver(**options)
    reference = load_reference().GeoTransolver(**options)
    reference.load_state_dict(dojo.state_dict(), strict=True)
    inputs = {
        "local_embedding": tuple(torch.randn(1, 11 + i * 4, d) for i, d in enumerate(dims)),
        "geometry": torch.randn(1, 9, 3),
    }
    if global_dim:
        inputs["global_embedding"] = torch.randn(1, 1, global_dim)
    a, b = dojo(**inputs), reference(**inputs)
    for i, (x, y) in enumerate(zip(a, b, strict=True)):
        torch.testing.assert_close(x, y, atol=1e-6, rtol=1e-5)
        single = dojo.forward_stream(
            inputs["local_embedding"][i],
            stream_index=i,
            **{k: v for k, v in inputs.items() if k != "local_embedding"},
        )
        torch.testing.assert_close(x, single, atol=1e-6, rtol=1e-5)
    sum(x.square().mean() for x in a).backward()
    sum(x.square().mean() for x in b).backward()
    for x, y in zip(dojo.parameters(), reference.parameters(), strict=True):
        torch.testing.assert_close(x.grad, y.grad, atol=1e-6, rtol=1e-5)
    build_optimizer(dojo, lr=0.001, weight_decay=0.0001).step()
    reference_optimizer(reference, lr=0.001, weight_decay=0.0001).step()
    for name, value in dojo.state_dict().items():
        torch.testing.assert_close(value, reference.state_dict()[name], atol=1e-6, rtol=1e-5)


def test_selected_stream_rejects_coupled_local_context():
    model = GeoTransolver(
        functional_dim=(3, 3),
        out_dim=(1, 1),
        geometry_dim=3,
        n_layers=1,
        n_hidden=8,
        n_head=2,
        include_local_features=True,
    )
    with pytest.raises(ValueError, match="局部编码"):
        model.forward_stream(torch.zeros(1, 2, 3), stream_index=0)
