"""查询分块仅影响解码，缓存累加、点身份与输出覆盖保持一致。"""

import torch

from ai4e_contrib.ability.model.transolver3.component import construct
from ai4e_contrib.ability.model.transolver3.inference import SurfaceInference


def test_cached_decode_chunk_size_preserves_full_result():
    torch.manual_seed(7)
    model = construct(
        space_dim=3, fun_dim=0, out_dim=1, n_hidden=16, n_layers=2, n_head=4, slice_num=4
    )
    features = torch.rand(1, 17, 3)

    def chunks():
        for start in [0, 9]:
            end = min(start + 9, 17)
            yield torch.arange(start, end), {"features": features[:, start:end]}

    caches = []
    original = list(
        SurfaceInference(model).predict(
            chunks, observer=lambda *event: caches.append(event[2].clone())
        )
    )
    observed = []
    split = list(
        SurfaceInference(model).predict(
            chunks, query_chunk_size=3, observer=lambda *event: observed.append(event[2].clone())
        )
    )
    assert max(len(ids) for ids, _ in split) <= 3
    assert torch.equal(torch.cat([i for i, _ in split]), torch.arange(17))
    for a, b in zip(caches, observed, strict=True):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    torch.testing.assert_close(
        torch.cat([v["fields"] for _, v in original], dim=1),
        torch.cat([v["fields"] for _, v in split], dim=1),
        rtol=1e-5,
        atol=1e-6,
    )
