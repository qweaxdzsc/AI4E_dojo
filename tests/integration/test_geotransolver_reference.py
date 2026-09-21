"""独立源码和完整网络结构的小空间对照。"""

import torch

from tools.verification.geotransolver.compare import compare


def test_full_structure_cpu_parity():
    torch.set_num_threads(4)
    torch.manual_seed(12)
    x = torch.randn(1, 25, 3)
    result = compare(
        {
            "functional_dim": 3,
            "out_dim": 1,
            "geometry_dim": 3,
            "n_layers": 4,
            "n_hidden": 128,
            "n_head": 4,
            "slice_num": 64,
            "structured_shape": (5, 5),
        },
        {"local_embedding": x, "geometry": x},
    )
    assert max(result.values()) <= 1e-6
