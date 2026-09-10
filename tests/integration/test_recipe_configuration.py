"""五段用户配置和稳定库输入：覆盖顺序、默认值、路径及拒绝边界。"""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

from ai4e_contrib.application.aero_cfd import resolve_config
from tests.integration.test_dataset_recipe import (
    RECIPE,
    application_parameters,
    load_configuration,
    setup_case,
)


def test_default_business_semantics_and_isolated_arguments():
    public = load_configuration(RECIPE / "config.yaml")
    internal = application_parameters(public)
    assert resolve_config(internal) == internal
    assert internal["sampling"]["seed"] == 42
    assert "sampling" not in public
    assert list(internal["trainprep"]["domains"]) == list(public.trainprep.domains)
    before = OmegaConf.to_container(public, resolve=True)
    internal["sampling"]["seed"] = 321
    assert OmegaConf.to_container(public, resolve=True) == before


@pytest.mark.parametrize(
    "key", ["sampling.seed", "normalization.execute", "sources", "pre", "datapre"]
)
def test_old_user_keys_rejected(key):
    with pytest.raises(ValueError, match="旧案例配置键"):
        load_configuration(RECIPE / "config.yaml", {key: 1})


@pytest.mark.parametrize("stage", ["pre", "datapre"])
def test_old_stage_rejected(stage):
    with pytest.raises(ValueError, match="请改用 rawprep"):
        load_configuration(RECIPE / "config.yaml", {"pipeline.stages": [stage]})


def test_relative_statistics_and_defaults(tmp_path, monkeypatch):
    folder, _ = setup_case(tmp_path)
    monkeypatch.chdir(tmp_path.parent)
    cfg = load_configuration(
        folder / "config.yaml",
        {
            "trainprep.normalization.statistics": "../statistics.yaml",
            "trainprep.sampling.seed": 137,
            "train.learning_rate": 0.003,
        },
    )
    assert cfg.trainprep.normalization.statistics == str(tmp_path / "statistics.yaml")
    assert cfg.trainprep.sampling.seed == 137
    assert cfg.train.learning_rate == 0.003
    assert "sampling" not in cfg and "normalization" not in cfg


def test_transolver_defaults_and_custom_parameters(tmp_path):
    config = yaml.safe_load((RECIPE / "config.yaml").read_text())
    config["components"] = {"model": "ai4e_contrib.ability.model.transolver3.component"}
    config["pipeline"]["stages"] = ["rawprep"]
    config["model"] = {"parameters": {"n_hidden": 128}}
    config["train"] = {"learning_rate": 0.004}
    config["trainprep"]["sampling"] = {"seed": 93, "stride": 4}
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    public = load_configuration(path)
    internal = application_parameters(public)
    assert internal["sampling"] == {"seed": 93, "stride": 4}
    assert internal["model"]["parameters"]["n_hidden"] == 128
    assert internal["train"]["learning_rate"] == 0.004
    assert "sampling" not in public
    assert internal == resolve_config(deepcopy(internal), validate=False)


def test_reference_statistics_preflight_without_training_partition(tmp_path):
    from tests.integration.test_dataset_recipe import execute_case

    folder, cfg = setup_case(tmp_path)
    cfg.dataset.partition = {"test": ["b"]}
    cfg.statistics.mode = "reference"
    assert execute_case(folder, cfg) == 0
    assert not (Path(cfg.data_root) / "train/statistics.yaml").exists()
