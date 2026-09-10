"""第 61 项：规模、参数量、峰值内存及条件 ETA。"""

import torch

from ai4e_core.abilities.training import loop
from tests.integration.test_train_loop import Run


def test_progress_includes_scale_parameters_and_peak_memory(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append((args, kwargs)))
    monkeypatch.setattr(loop.sys.stderr, "isatty", lambda: False)
    model = torch.nn.Linear(3, 2)
    report = loop.fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: [None],
        lambda network, _: {"loss": network(torch.ones(1, 3)).square().mean()},
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 1, "split_counts": {"train": 2, "test": 1}},
        contract={},
    )
    assert report["updates"] == 1
    setup = [item for item in events if item[0][1] == "诊断"]
    assert setup and setup[0][1]["规模"] == {"train": 2, "test": 1}
    assert setup[0][1]["参数量"] == 8
    progress = [item for item in events if item[0][1] == "进度"]
    assert progress and "峰值内存" in progress[0][1]
    assert "预计剩余" not in progress[0][1]


def test_eta_only_on_interactive_terminal(tmp_path, monkeypatch):
    events = []
    monkeypatch.setattr(loop, "event", lambda *args, **kwargs: events.append(kwargs))
    monkeypatch.setattr(loop.sys.stderr, "isatty", lambda: True)
    model = torch.nn.Linear(1, 1)
    loop.fit(
        model,
        torch.optim.SGD(model.parameters(), lr=0.1),
        lambda _: [None],
        lambda network, _: {"loss": network(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 1.0},
        Run(tmp_path),
        config={"max_epochs": 2},
        contract={},
    )
    first = next(item for item in events if item.get("轮次") == 1)
    assert "预计剩余" in first
