"""后处理独立随机流、参考张量包与原子能力分层的回归验收。"""

import random
from pathlib import Path

import numpy as np
import pytest
import torch

from ai4e_core.abilities.data.save.store import write_tensor_file
from ai4e_core.abilities.inference.randomness import seeded_randomness
from tests.integration.test_post_inference import _fit_then_post_config, _run_script
from tests.integration.test_train_recipe import prepared_case


def test_inference_randomness_repeats_and_restores_on_failure():
    random.seed(12)
    np.random.seed(12)
    torch.manual_seed(12)
    state = torch.get_rng_state().clone()
    with seeded_randomness(42):
        first = (random.random(), np.random.rand(), torch.rand(3))
    with pytest.raises(RuntimeError), seeded_randomness(42):
        second = (random.random(), np.random.rand(), torch.rand(3))
        raise RuntimeError("推理失败")
    assert first[:2] == second[:2]
    assert torch.equal(first[2], second[2])
    assert torch.equal(state, torch.get_rng_state())
    assert random.random() == random.Random(12).random()
    assert np.random.rand() == np.random.RandomState(12).rand()


def test_atomic_tensor_bundle_failure_preserves_previous_file(tmp_path, monkeypatch):
    path = tmp_path / "sample.pt"
    write_tensor_file(path, {"pressure": torch.ones(2, 1)})

    def fail(*args, **kwargs):
        raise OSError("磁盘写入失败")

    monkeypatch.setattr(torch, "save", fail)
    with pytest.raises(OSError):
        write_tensor_file(path, {"pressure": torch.zeros(2, 1)}, overwrite=True)
    assert torch.equal(torch.load(path, weights_only=True)["pressure"], torch.ones(2, 1))
    assert list(tmp_path.iterdir()) == [path]


def test_post_flags_do_not_change_saved_prediction(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    _fit_then_post_config(cfg)
    cfg.post.random_stream = "global"
    result, trained, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(trained / "checkpoints/last.pt")
    results = []
    for evaluate in (True, False):
        cfg.post.evaluate = evaluate
        cfg.paths.datasets.predictions = str(tmp_path / f"predictions-{evaluate}")
        result, _, summary = _run_script(folder, cfg, entry="post.py")
        assert result.returncode == 0, result.stderr
        item = summary["reports"]["post"]["predictions"][0]
        packed = torch.load(item["packed"], weights_only=True)
        assert Path(item["packed"]).name == "sample_0000.pt"
        for name, value in packed.items():
            assert torch.equal(
                value, torch.load(Path(item["output"]) / f"{name}.pt", weights_only=True)
            )
        results.append(packed)
    assert results[0].keys() == results[1].keys()
    for name in results[0]:
        assert torch.equal(results[0][name], results[1][name])


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="需要真实 Apple GPU")
def test_mps_randomness_restored_on_exception():
    from ai4e_core.abilities.inference.randomness import seeded_randomness

    before = torch.mps.get_rng_state()
    with pytest.raises(RuntimeError, match="abort"), seeded_randomness(17):
        torch.rand(16, device="mps")
        raise RuntimeError("abort")
    assert torch.equal(before, torch.mps.get_rng_state())


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="需要真实 Apple GPU")
def test_rope_mps_forward_backward_stays_on_device():
    from ai4e_contrib.ability.model.abupt.modules.rope import rope
    from ai4e_core.abilities.modeling.modules.position_encoding import RopeFrequency

    positions = torch.rand(1, 8, 3, device="mps")
    frequencies = RopeFrequency(dim=64, ndim=3).to("mps")(positions)
    x = torch.randn(1, 3, 8, 64, device="mps", requires_grad=True)
    output = rope(x, frequencies)
    output.square().mean().backward()
    assert frequencies.device.type == output.device.type == x.grad.device.type == "mps"
    assert torch.isfinite(x.grad).all()
