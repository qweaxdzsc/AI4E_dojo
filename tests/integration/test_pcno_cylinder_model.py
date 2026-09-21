"""正式二维时空网络的输入边界及反向验收。"""

import pytest
import torch

from ai4e_contrib.ability.model.pcno.cylinder import build_model


@pytest.mark.parametrize("branch,channels", [("fluid", 3), ("structure", 1)])
def test_real_network(branch, channels):
    torch.set_num_threads(2)
    model = build_model(branch=branch, width=8, modes=(2, 2, 2), blocks=4, horizon=4)
    history = torch.randn(1, 3, 12, 12, 4)
    result = model(history)
    assert result.shape == (1, 4, 12, 12, channels)
    result.square().mean().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    with pytest.raises(ValueError, match="历史"):
        model(history[:, :2])
