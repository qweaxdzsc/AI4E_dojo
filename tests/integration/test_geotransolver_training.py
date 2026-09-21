"""无关小网络的参数覆盖、组合优化、轮次日程及恢复。"""

from copy import deepcopy

import pytest
import torch

from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
from ai4e_core.abilities.training.parameter_partition import partition_parameters
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler


def test_partition_rejects_overlap_and_missing():
    m = torch.nn.Linear(2, 1)
    for choices in ({"a": lambda n, p: False}, {"a": lambda n, p: True, "b": lambda n, p: True}):
        with pytest.raises(ValueError):
            partition_parameters(m, choices)


def test_optimizer_and_epoch_scheduler_resume():
    torch.manual_seed(5)
    a = torch.nn.Linear(3, 2)
    b = deepcopy(a)

    def configure(m):
        groups = partition_parameters(
            m, {"m": lambda n, p: p.ndim == 2, "v": lambda n, p: p.ndim != 2}
        )
        opt = CombinedOptimizer(
            [
                torch.optim.AdamW(groups["m"], lr=0.01),
                torch.optim.SGD(groups["v"], lr=0.02, momentum=0.9),
            ]
        )
        sch = EpochBoundaryScheduler(torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=10), 3)
        return opt, sch

    oa, sa = configure(a)
    ob, sb = configure(b)
    x = torch.randn(4, 3)

    def step(m, o, s):
        o.zero_grad()
        m(x).square().mean().backward()
        o.step()
        s.step()

    for _ in range(4):
        step(a, oa, sa)
    b.load_state_dict(a.state_dict())
    ob.load_state_dict(deepcopy(oa.state_dict()))
    sb.load_state_dict(deepcopy(sa.state_dict()))
    for _ in range(4):
        step(a, oa, sa)
        step(b, ob, sb)
    for p, q in zip(a.parameters(), b.parameters()):
        torch.testing.assert_close(p, q, rtol=0, atol=0)
    assert sa.state_dict() == sb.state_dict()
    assert sa.scheduler.last_epoch == 2


def test_checkpoint_interval_uses_public_assembly(tmp_path):
    from ai4e_core.abilities.training.iteration_stream import IterationStream
    from ai4e_core.applications.base.iteration_training import train_model

    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    saved = []

    class Session:
        def checkpoint(self, label, payload, namespace):
            saved.append(payload["updates"])
            path = tmp_path / "latest.pt"
            torch.save(payload, path)
            return path

        def report(self, *a, **kw):
            pass

    result = train_model(
        model,
        optimizer,
        IterationStream(4, 1),
        lambda ids: torch.ones(1, 1),
        lambda m, x: m(x).square().mean(),
        updates=5,
        session=Session(),
        contract={},
        namespace="train",
        checkpoint_every=2,
    )
    assert saved == [2, 4, 5]
    assert result["status"] == "complete"
