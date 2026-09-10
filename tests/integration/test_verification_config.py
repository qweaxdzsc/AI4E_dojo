"""显式参考实验必须保留种子与预算，缺声明不能回到默认实验。"""

import pytest
import yaml

from tests.integration.test_dataset_recipe import RECIPE
from tools.verification.recipe_config import load_application_config, read_experiment


def test_nondefault_reference_sampling(tmp_path):
    cfg = yaml.safe_load((RECIPE / "config.yaml").read_text())
    sampling = cfg["trainprep"]["sampling"]
    sampling["seed"] = 197
    sampling["supernodes"]["num_points"] = 123
    sampling["domains"]["surface"]["anchor"]["num_points"] = 83
    path = tmp_path / "experiment.yaml"
    path.write_text(yaml.safe_dump(cfg))
    user, actual = read_experiment(path)
    assert actual == sampling
    assert user["trainprep"]["sampling"]["seed"] == 197
    assert read_experiment(None) == ({}, {})
    del sampling["seed"]
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError, match="缺少"):
        read_experiment(path)


def test_verification_uses_real_recipe_mapping():
    internal = load_application_config(RECIPE / "config.yaml")
    assert internal["sampling"]["seed"] == 42
    assert "rawprep" not in internal and "sampling" not in internal["trainprep"]
