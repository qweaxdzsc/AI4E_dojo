"""第 59 项：信号与回调异常时尝试可恢复收尾。"""

import os
import signal

import pytest
import torch

from ai4e_core.abilities.training.loop import fit
from tests.integration.test_train_loop import Run


def test_callback_exception_writes_recoverable_latest(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    run = Run(tmp_path)

    def explode():
        raise RuntimeError("injected evaluation failure")

    with pytest.raises(RuntimeError, match="injected"):
        fit(
            model,
            optimizer,
            lambda _: [None],
            lambda network, _: {"loss": network(torch.ones(1, 1)).square().mean()},
            explode,
            run,
            config={"max_epochs": 1, "snapshot": False},
            contract={},
        )
    latest = run.writer.run_dir / "checkpoints" / "latest.pt"
    assert latest.is_file()
    assert not (run.writer.run_dir / "checkpoints" / "last.pt").exists()


def test_termination_signal_saves_after_current_update(tmp_path):
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    run = Run(tmp_path)

    def step(network, _batch):
        os.kill(os.getpid(), signal.SIGTERM)
        return {"loss": network(torch.ones(1, 1)).square().mean()}

    with pytest.raises(InterruptedError, match="终止信号"):
        fit(
            model,
            optimizer,
            lambda _: [None, None],
            step,
            lambda: {"loss": 1.0},
            run,
            config={"max_epochs": 1},
            contract={},
        )
    assert (run.writer.run_dir / "checkpoints" / "latest.pt").is_file()
