"""冻结准备绑定数据与模型声明，探测不推进随机流。"""

import json
import random
from types import SimpleNamespace

import pytest
import torch

from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
from tests.integration.test_physical_dataset_contract import physical_fixture


def test_freeze_change_rejected_and_rng_preserved(tmp_path):
    view = physical_fixture(tmp_path)
    config = {
        "model": {"parameters": {"width": 2}},
        "trainprep": {"domains": {"surface": {"position": "pos", "targets": {"p": "p"}}}},
        "sampling": {},
        "normalization": {"execute": True, "fields": {"pos": {"method": "identity"}}},
    }

    def probe(*args, **kwargs):
        random.random()
        torch.rand(1)

    model = SimpleNamespace(SOURCE="external-component", prepare_sample=probe)
    dataset = SimpleNamespace(open_physical=lambda _: view)
    before = (random.getstate(), torch.get_rng_state().clone())
    _, _, record = open_preparation(config, dataset, model)
    assert random.getstate() == before[0] and torch.equal(torch.get_rng_state(), before[1])
    path = tmp_path / "preparation.json"
    path.write_text(json.dumps(record))
    open_preparation(config, dataset, model, path)
    config["model"]["parameters"]["width"] = 3
    with pytest.raises(ValueError, match="变化"):
        open_preparation(config, dataset, model, path)
