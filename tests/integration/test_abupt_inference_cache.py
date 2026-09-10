"""真实模型几何、逐层锚点缓存与分块查询等价验收。"""

import copy

import pytest
import torch

from ai4e_contrib.ability.model.abupt.inference import InferenceContext
from tests.integration.test_abupt_multidomain import inputs, make_model, specs


@pytest.mark.parametrize("batch_size", [1, 2, 3])
def test_full_geometry_cache_and_chunks(batch_size):
    data = specs(features=True, conditions=True)
    model = make_model(data).eval()
    batch = inputs(data, batch_size)
    queries = batch.pop("domain_query_positions")
    features = batch.pop("domain_query_features")
    calls = []
    hook = model.encoder.register_forward_hook(lambda *args: calls.append(1))
    with torch.no_grad():
        full = model(**batch, domain_query_positions=queries, domain_query_features=features)[0]
        with InferenceContext(model, batch, preparation_id="fixture") as context:
            assert len(calls) == 2
            for size in [1, 3, 100]:
                result = context.chunks(
                    queries, features=features, chunk_size=size, preparation_id="fixture"
                )
                for k, v in result.items():
                    torch.testing.assert_close(v, full[k], rtol=1e-5, atol=1e-6)
            assert len(calls) == 2
            geo = context.cache.geometry_only()
            reused = {k: v for k, v in batch.items() if not k.startswith("geometry_")}
            output, _ = model(
                **reused,
                domain_query_positions=queries,
                domain_query_features=features,
                kv_cache=geo,
            )
            for k, v in output.items():
                torch.testing.assert_close(v, full[k], rtol=1e-5, atol=1e-6)
            assert len(calls) == 2
    hook.remove()


@pytest.mark.parametrize(
    "change", ["weights", "load", "mode", "dtype", "record", "grad", "close", "layers"]
)
def test_invalid_cache_rejected(change):
    model = make_model().eval()
    batch = inputs(queries=False)
    with torch.no_grad():
        ctx = InferenceContext(model, batch, preparation_id="a")
        if change == "weights":
            next(model.parameters()).add_(1)
        if change == "load":
            model.load_state_dict(copy.deepcopy(model.state_dict()))
        if change == "mode":
            model.train()
        if change == "dtype":
            model.double()
        if change == "close":
            ctx.close()
        if change == "layers":
            ctx.cache.physics.pop()
        query = {"surface": torch.rand(1, 2, 3)}
        if change == "grad":
            with torch.enable_grad(), pytest.raises(ValueError):
                ctx.query(query, preparation_id="a")
        else:
            with pytest.raises(ValueError):
                ctx.query(query, preparation_id="b" if change == "record" else "a")


def test_train_then_eval_and_extra_features_rejected():
    model = make_model().eval()
    with torch.no_grad():
        ctx = InferenceContext(model, inputs(queries=False), preparation_id="a")
        with pytest.raises(ValueError, match="对应"):
            ctx.chunks(
                {"surface": torch.rand(1, 2, 3)},
                features={"volume": torch.rand(1, 2, 1)},
                preparation_id="a",
            )
        model.train().eval()
        with pytest.raises(ValueError, match="改变"):
            ctx.query({"surface": torch.rand(1, 2, 3)}, preparation_id="a")


def test_cache_skips_all_kv_projections_and_reports_cost(record_property):
    from time import perf_counter

    model = make_model().eval()
    batch = inputs()
    query = batch.pop("domain_query_positions")
    calls = []
    hooks = [
        m.kv.register_forward_hook(lambda *args: calls.append(1))
        for m in list(model.blocks) + [b for layers in model.decoders.values() for b in layers]
    ]
    with torch.no_grad():
        start = perf_counter()
        full = model(**batch, domain_query_positions=query)[0]
        record_property("uncached_seconds", perf_counter() - start)
        with InferenceContext(model, batch, preparation_id="a") as ctx:
            count = len(calls)
            start = perf_counter()
            result = ctx.chunks(query, chunk_size=2, preparation_id="a")
            record_property("cached_query_seconds", perf_counter() - start)

            def size(value):
                if isinstance(value, torch.Tensor):
                    return value.numel() * value.element_size()
                if isinstance(value, dict):
                    return sum(size(v) for v in value.values())
                if isinstance(value, (list, tuple)):
                    return sum(size(v) for v in value)
                return 0

            record_property("cache_tensor_bytes", size(vars(ctx.cache)))
            assert len(calls) == count
            for k, v in result.items():
                torch.testing.assert_close(v, full[k], rtol=1e-5, atol=1e-6)
    for h in hooks:
        h.remove()
