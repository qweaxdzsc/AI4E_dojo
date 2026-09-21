"""普通网络的优化工厂、完整状态及恢复合同。"""

from copy import deepcopy
from types import SimpleNamespace

import pytest
import torch

from ai4e_contrib.application.aero_cfd.geotransolver import optimizer_factory, scheduler_factory
from ai4e_core.applications.aero_cfd.train.physical import configure_optimization


def test_optimizer_factories_restore_plain_network():
    torch.set_num_threads(2)
    torch.manual_seed(7)
    a = torch.nn.Linear(3, 2)
    settings = {
        "learning_rate": 0.001,
        "weight_decay": 0.0001,
        "step_size": 1,
        "gamma": 0.5,
        "accumulate": 1,
    }
    job = SimpleNamespace(model=a, config={"train": settings}, samples=[1, 2], extensions={})
    configure_optimization(
        job, optimizer_factory=optimizer_factory, scheduler_factory=scheduler_factory
    )
    x = torch.arange(12.0).reshape(4, 3) / 10
    for _ in range(2):
        job.optimizer.zero_grad()
        a(x).square().mean().backward()
        job.optimizer.step()
        job.scheduler.step()
    assert job.optimizer.param_groups[0]["lr"] == 0.0005
    b = torch.nn.Linear(3, 2)
    b.load_state_dict(a.state_dict())
    other = SimpleNamespace(model=b, config={"train": settings}, samples=[1, 2], extensions={})
    configure_optimization(
        other, optimizer_factory=optimizer_factory, scheduler_factory=scheduler_factory
    )
    other.optimizer.load_state_dict(deepcopy(job.optimizer.state_dict()))
    other.scheduler.load_state_dict(job.scheduler.state_dict())
    for j in (job, other):
        j.optimizer.zero_grad()
        j.model(x).square().mean().backward()
        j.optimizer.step()
        j.scheduler.step()
    for first, second in zip(a.parameters(), b.parameters(), strict=True):
        torch.testing.assert_close(first, second, atol=0, rtol=0)
    assert job.extensions == other.extensions
    with pytest.raises(ValueError, match="同时"):
        configure_optimization(job, optimizer_factory=optimizer_factory)
