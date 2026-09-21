"""圆柱准入用的独立解析场及可微性验收。"""

import pytest
import torch

from ai4e_core.abilities.constraint.continuity import (
    staggered_divergence,
    triangle_divergence,
    triangle_geometry,
    triangle_gradient,
    weighted_mean_square,
)


def test_affine_triangle_and_gradcheck():
    p = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=torch.double)
    cells = torch.tensor([[0, 1, 2], [1, 3, 2]])
    inverse, area = triangle_geometry(p, cells)
    velocity = torch.stack((2 * p[:, 0] + p[:, 1], p[:, 0] - 2 * p[:, 1]), -1)
    torch.testing.assert_close(
        triangle_divergence(velocity, cells, inverse), torch.zeros(2, dtype=torch.double)
    )
    torch.testing.assert_close(
        triangle_divergence(p, cells, inverse), torch.full((2,), 2.0, dtype=torch.double)
    )
    assert area.sum() == 1
    assert torch.autograd.gradcheck(
        lambda x: triangle_gradient(x, cells, inverse), (velocity.requires_grad_(),)
    )


def test_staggered_and_empty_domain():
    x, y = torch.meshgrid(torch.arange(5.0), torch.arange(6.0), indexing="ij")
    velocity = torch.stack((2 * x + y, x - 2 * y), -1)
    torch.testing.assert_close(staggered_divergence(velocity), torch.zeros(4, 5))
    torch.testing.assert_close(
        staggered_divergence(torch.stack((x, y), -1)), torch.full((4, 5), 2.0)
    )
    with pytest.raises(ValueError, match="有效域"):
        weighted_mean_square(x, torch.zeros_like(x))


def test_invalid_triangle():
    with pytest.raises(ValueError, match="退化"):
        triangle_geometry(
            torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]), torch.tensor([[0, 1, 2]])
        )
