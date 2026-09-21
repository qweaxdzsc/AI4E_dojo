"""可复制配置公开路径及失败边界。"""

from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf

from ai4e_contrib.application.geotransolver import load_configuration, validate

ROOT = Path(__file__).resolve().parents[2]


def test_config_file_dict_and_omegaconf_consistency(tmp_path):
    cfg = yaml.safe_load((ROOT / "recipes/geotransolver/darcy/config.yaml").read_text())
    cfg["inputs"]["rawprep"]["source"] = "raw"
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    actual = load_configuration(path, ["train.updates=2"])
    assert actual["inputs"]["rawprep"]["source"] == str(tmp_path / "raw")
    assert actual["train"]["updates"] == 2
    assert validate(OmegaConf.create(actual)) == validate(actual)
    cfg["train"]["resume"] = "old.pt"
    with pytest.raises(ValueError, match="旧配置"):
        validate(cfg)


def test_unknown_training_parameter_rejected():
    cfg = yaml.safe_load((ROOT / "recipes/geotransolver/darcy/config.yaml").read_text())
    cfg["train"]["batch_sze"] = 4
    with pytest.raises(ValueError, match="字段"):
        validate(cfg)
