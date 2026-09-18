"""逐步在线损失：每批记账、间隔冲刷与非有限拒绝。"""

from pathlib import Path

import pytest
import torch
from omegaconf import OmegaConf

from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.online import OnlineLoss
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from tests.integration.test_train_loop import Run

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd/config.yaml"


def _step(network, batch):
    extra = network(batch["x"]).sum() * 0
    return {
        "loss": extra + batch["loss"],
        "losses": {"p": extra + batch["part"]},
    }


def test_online_window_averages_and_rejects_nonfinite():
    window = OnlineLoss()
    window.record({"loss": torch.tensor(2.0), "losses": {"p": torch.tensor(1.0)}})
    window.record({"loss": torch.tensor(4.0), "losses": {"p": torch.tensor(3.0)}})
    assert window.flush() == {"loss": 3.0, "p": 2.0}
    assert window.empty()
    with pytest.raises(ValueError, match="窗口为空"):
        window.flush()
    with pytest.raises(ValueError, match="非有限"):
        window.record({"loss": torch.tensor(float("nan"))})


def test_accumulate_two_batches_then_epoch_flush(tmp_path, monkeypatch):
    from ai4e_core.abilities.training import loop

    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append((args[1], kwargs)))
    batches = [
        {"x": torch.ones(1, 1), "loss": torch.tensor(2.0), "part": torch.tensor(1.0)},
        {"x": torch.ones(1, 1), "loss": torch.tensor(4.0), "part": torch.tensor(3.0)},
    ]
    model = torch.nn.Linear(1, 1)
    report = fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: iter(batches),
        _step,
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 1, "accumulate": 2},
        contract={},
    )
    assert report["updates"] == 1
    progress = [item for item in events if item[0] == "进度"]
    assert len(progress) == 1
    assert progress[0][1]["损失"] == pytest.approx(3.0)
    assert progress[0][1]["在线"] == {"p": 2.0}


def test_flush_after_each_update_writes_items(tmp_path, monkeypatch):
    from ai4e_core.abilities.training import loop

    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append(kwargs))
    batches = [
        {"x": torch.ones(1, 1), "loss": torch.tensor(2.0), "part": torch.tensor(8.0)},
        {"x": torch.ones(1, 1), "loss": torch.tensor(4.0), "part": torch.tensor(2.0)},
    ]
    model = torch.nn.Linear(1, 1)
    fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: iter(batches),
        _step,
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 1, "log_every_updates": 1},
        contract={},
    )
    online = [item for item in events if "在线" in item and "耗时" not in item]
    assert [item["损失"] for item in online] == [pytest.approx(2.0), pytest.approx(4.0)]
    assert [item["在线"] for item in online] == [{"p": 8.0}, {"p": 2.0}]


def test_default_recipe_has_empty_update_interval_and_epoch_only_progress(tmp_path, monkeypatch):
    from ai4e_core.abilities.training import loop

    resolved = apply_resolved(OmegaConf.to_container(OmegaConf.load(RECIPE), resolve=True))
    assert resolved["train"]["log_every_updates"] is None
    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append(kwargs))
    model = torch.nn.Linear(1, 1)
    fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: [None],
        lambda network, _: {"loss": network(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 2},
        contract={},
    )
    assert [item["轮次"] for item in events] == [1, 2]


def test_named_nonfinite_is_rejected(tmp_path):
    model = torch.nn.Linear(1, 1)

    def step(network, batch):
        extra = network(torch.ones(1, 1)).sum() * 0
        return {"loss": extra + 1, "losses": {"p": extra + float("nan")}}

    with pytest.raises(ValueError, match="非有限"):
        fit(
            model,
            torch.optim.SGD(model.parameters(), lr=0.1),
            lambda _: [None],
            step,
            lambda: {"loss": 1.0},
            Run(tmp_path),
            config={"max_epochs": 1},
            contract={},
        )


@pytest.mark.parametrize("interval", [None, 1, 2, 3])
def test_epoch_report_keeps_all_online_batches_regardless_of_log_flush(tmp_path, interval):
    """页面消费整轮分项；更新日志冲刷不能清空或截短报告统计。"""
    import json

    model = torch.nn.Linear(1, 1)
    run = Run(tmp_path)
    batches = [
        {"x": torch.ones(1, 1), "loss": torch.tensor(loss), "part": torch.tensor(part)}
        for loss, part in [(2.0, 8.0), (4.0, 2.0), (6.0, 5.0)]
    ]
    fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: batches,
        _step,
        lambda: pytest.fail("关闭评估不得消费测试集"),
        run,
        config={"max_epochs": 1, "evaluation_enabled": False, "log_every_updates": interval},
        contract={},
    )
    record = json.loads((run.writer.run_dir / "artifacts/training.json").read_text())
    assert record["history"][0]["online"] == {"loss": 4.0, "p": 5.0}
    assert record["history"][0]["evaluation"] is None
