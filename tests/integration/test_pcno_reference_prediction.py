"""参考推理门禁与诊断口径；不把小数组测试当真实网络验收。"""

import pytest
import torch

from tools.verification.pcno.predict import errors, require_complete


def test_physical_metrics():
    actual = errors(torch.tensor([3.0, 5.0]), torch.tensor([1.0, 1.0]))
    assert actual["mae"] == 3.0
    assert actual["rmse"] == pytest.approx(10**0.5)
    assert actual["mare"] == pytest.approx(3 / (1 + 1e-8))


@pytest.mark.parametrize(
    "state", [{}, {"epoch": 250}, {"epoch": 250, "updates": 5249}, {"epoch": 1, "updates": 21}]
)
def test_incomplete_training_cannot_produce_final_baseline(state):
    with pytest.raises(ValueError, match="250 epochs"):
        require_complete(state)


def test_complete_state_and_metric_rejection():
    require_complete({"epoch": 250, "updates": 5250})
    with pytest.raises(ValueError, match="finite"):
        errors(torch.tensor([float("nan")]), torch.ones(1))
    with pytest.raises(ValueError, match="shape"):
        errors(torch.zeros(2), torch.zeros(3))


def test_continuation_does_not_accept_running_or_failed(tmp_path):
    import json

    from tools.verification.pcno.finish_reference import training_ready

    for branch in ["pres", "temp"]:
        root = tmp_path / f"{branch}-250"
        root.mkdir()
        (root / "status.json").write_text(
            json.dumps({"state": "running", "epoch": 1, "updates": 1})
        )
    assert not training_ready(tmp_path)
    (tmp_path / "pres-250/status.json").write_text(
        json.dumps({"state": "failed", "traceback": "test failure"})
    )
    with pytest.raises(RuntimeError, match="reference failed"):
        training_ready(tmp_path)
    for branch in ["pres", "temp"]:
        (tmp_path / f"{branch}-250/status.json").write_text(
            json.dumps({"state": "complete", "epoch": 250, "updates": 5250})
        )
    assert training_ready(tmp_path)


def test_saved_sample_does_not_retain_entire_chunk(tmp_path):
    from tools.verification.pcno.predict import owned_arrays

    full = torch.arange(100).reshape(10, 10)
    result = {"view": full[:1], "nested": [full[2:3]]}
    path = tmp_path / "sample.pt"
    torch.save(owned_arrays(result), path)
    restored = torch.load(path, weights_only=True)
    for value in [restored["view"], restored["nested"][0]]:
        assert value.untyped_storage().nbytes() == value.numel() * value.element_size()
    assert torch.equal(restored["view"], full[:1])
