"""独立选优政策、恢复拒绝和真实 writer 下普通/EMA 权重来源配对。"""

import copy

import pytest
import torch

from ai4e_core import run
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.run import TrainingRun
from tests.integration.test_epoch_stream import capability


@pytest.fixture
def selection_type():
    return capability("selection").BestMetric


@pytest.mark.parametrize(
    "mode,values,wanted", [("min", [3, -1, -1, 2], -1), ("max", [-2, 1, 1, 0], 1)]
)
@pytest.mark.parametrize("tie,last_step", [("first", 1), ("last", 2)])
def test_policy_and_resume(selection_type, mode, values, wanted, tie, last_step):
    selector = selection_type(mode=mode, tie=tie)
    assert selector.state_dict()["best"] is None
    for step, value in enumerate(values):
        before = selector.state_dict()
        improved = selector.improves(value)
        assert selector.state_dict() == before
        if improved:
            selector.commit(value, step=step, source="candidate")
        else:
            with pytest.raises(ValueError):
                selector.commit(value, step=step, source="candidate")
        restored = selection_type(mode=mode, tie=tie)
        restored.load_state_dict(selector.state_dict())
        selector = restored
    assert selector.state_dict()["best"] == wanted
    assert selector.state_dict()["step"] == last_step


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), True, "2"])
def test_nonfinite_or_non_numeric_rejected(selection_type, value):
    selector = selection_type()
    before = selector.state_dict()
    with pytest.raises(ValueError):
        selector.improves(value)
    with pytest.raises(ValueError):
        selector.commit(value, step=0, source="raw")
    assert selector.state_dict() == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("mode", "max"),
        ("tie", "last"),
        ("best", float("nan")),
        ("step", -1),
        ("source", ""),
        ("version", True),
    ],
)
def test_invalid_restore_is_atomic(selection_type, field, value):
    selector = selection_type()
    selector.commit(2.0, step=1, source="raw")
    before = selector.state_dict()
    bad = {**before, field: value}
    with pytest.raises(ValueError):
        selector.load_state_dict(bad)
    assert selector.state_dict() == before


@pytest.mark.parametrize("step,source", [(-1, "raw"), (True, "raw"), (2, ""), (2, None)])
def test_invalid_commit_metadata_is_atomic(selection_type, step, source):
    selector = selection_type()
    before = selector.state_dict()
    with pytest.raises(ValueError):
        selector.commit(1, step=step, source=source)
    assert selector.state_dict() == before


def test_real_session_selection_weights_and_failed_save(selection_type, tmp_path, monkeypatch):
    result = {}

    def train(cfg):
        session = TrainingRun()
        selector = selection_type()
        selected = None
        model = torch.nn.Linear(1, 1, bias=False)
        x = torch.ones(2, 1)
        with torch.no_grad():
            model.weight.fill_(3)
        ema = MovingAverage(model, decay=0.5)
        # EMA 真正由公开组件更新，验证快照不冒用当前 raw 权重。
        candidates = [("raw", copy.deepcopy(model.state_dict()))]
        for raw in (1, -1):
            with torch.no_grad():
                model.weight.fill_(raw)
            ema.update(model)
            candidates.append(("ema", copy.deepcopy(ema.state)))
            if raw == 1:
                candidates.append(("raw", copy.deepcopy(model.state_dict())))
        with torch.no_grad():
            model.weight.fill_(4)
        candidates.append(("raw", copy.deepcopy(model.state_dict())))
        for step, (source, weights) in enumerate(candidates):
            model.load_state_dict(weights)
            with torch.no_grad():
                metric = model(x).square().mean().item()
            if selector.improves(metric):
                candidate = {
                    "model": copy.deepcopy(model.state_dict()),
                    "step": step,
                    "source": source,
                }
                session.checkpoint("best", candidate, namespace="train")
                selector.commit(metric, step=step, source=source)
                selected = candidate
        state = selector.state_dict()
        assert state["source"] == "ema" and state["step"] == 3 and state["best"] == 0.25
        latest = session.checkpoint(
            "latest",
            {"model": model.state_dict(), "selector": state, "selected": selected},
            namespace="train",
        )
        saved = torch.load(latest, weights_only=True)
        restored = selection_type()
        restored.load_state_dict(saved["selector"])
        assert (saved["selected"]["step"], saved["selected"]["source"]) == (
            state["step"],
            state["source"],
        )
        model.load_state_dict(saved["selected"]["model"])
        torch.testing.assert_close(model(x), torch.full_like(x, 0.5), rtol=0, atol=0)
        assert not restored.improves(0.3)
        before = restored.state_dict()

        def fail(*args, **kwargs):
            raise OSError("injected save failure")

        with monkeypatch.context() as patch:
            patch.setattr(torch, "save", fail)
            with pytest.raises(OSError, match="injected"):
                if restored.improves(0.01):
                    session.checkpoint("best", {"model": model.state_dict()}, namespace="train")
                    restored.commit(0.01, step=8, source="raw")
        assert restored.state_dict() == before
        best = torch.load(latest.with_name("best.pt"), weights_only=True)
        assert best["step"] == 3 and best["source"] == "ema"
        result.update(saved=saved, prediction=model(x).detach())
        session.report({"selection": state}, stage="train")

    def loader(path, overrides):
        return {
            "run_root": str(tmp_path / "records"),
            "data_root": str(tmp_path / "data"),
            "pipeline": {"stages": ["train"]},
            "train": {"snapshot": False},
        }

    assert run.launch({"train": train}, script=__file__, config_loader=loader, argv=[]) == 0
    assert result["saved"]["selector"]["best"] == 0.25
