"""运行只快照调用方配置，业务参数和数据发现不得覆盖用户输入。"""

import json
from pathlib import Path

import pytest
import torch
import yaml
from omegaconf import OmegaConf

from ai4e_core import run
from ai4e_core.run.training import TrainingRun
from tests.integration.test_dataset_recipe import execute_case, public_config, setup_case


@pytest.mark.parametrize("payload", [{"research": {"x": 5}}, {"choices": [1, 4]}])
def test_generic_loader_and_snapshot_isolation(tmp_path, payload):
    root = tmp_path / "records"
    config = {"run_root": str(root), "pipeline": {"stages": ["work"]}, **payload}
    observed = []

    def loader(path, overrides):
        observed.append((path, overrides))
        return config

    def work(cfg):
        session = TrainingRun()
        session.record_config(OmegaConf.to_container(cfg))
        cfg["mutated"] = True
        with pytest.raises(ValueError, match="已冻结"):
            session.record_config(OmegaConf.to_container(cfg))
        session.checkpoint("last", {"weights": torch.tensor([1])})

    assert (
        run.launch(
            {"work": work},
            script=str(tmp_path / "code/job.py"),
            argv=["--set", "anything=2"],
            config_loader=loader,
        )
        == 0
    )
    directory = next(root.iterdir())
    saved = yaml.safe_load((directory / "inputs/config.yaml").read_text())
    state = torch.load(directory / "checkpoints/last.pt", weights_only=False)
    assert state["effective_config"] == saved
    assert "mutated" not in saved and "execution" not in config
    assert observed[0][1] == ["anything=2"]


def test_discovered_source_is_report_not_config(tmp_path):
    folder, cfg = setup_case(tmp_path)
    assert execute_case(folder, cfg) == 0
    directory = next(Path(cfg.run_root).iterdir())
    saved = yaml.safe_load((directory / "inputs/config.yaml").read_text())
    report = json.loads((directory / "summary.json").read_text())["reports"]["dataset"]
    assert saved["dataset"] == OmegaConf.to_container(public_config(cfg).dataset)
    assert "definition" not in saved["dataset"]
    assert report["partitions"] == {"train": ["a"], "test": ["b"]}
    assert report["definition"] and "rawprep" in saved and "sources" not in saved
