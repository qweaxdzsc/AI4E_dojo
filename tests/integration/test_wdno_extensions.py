"""公开研究目录扩展：完整配置、固定能量读回及拒绝错误输出。"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from ai4e_contrib.application.spatiotemporal_pde.wdno.configuration import load_configuration

ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "examples/recipe_extensions/wdno"


def audit_module():
    """载入用户目录中的普通函数，不依赖框架注册。"""
    spec = importlib.util.spec_from_file_location("wdno_extension_audit", EXTENSION / "audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_extension_configuration():
    cfg = load_configuration(EXTENSION / "config.yaml")
    assert cfg["model"]["dim"] == 8 and cfg["train"]["updates"] == 2
    assert cfg["components"]["derived"] == "variants.energy"
    assert cfg["inputs"]["infer"]["checkpoint"] is None


@pytest.mark.parametrize("failure", ["shape", "nonfinite", "values", "missing"])
def test_energy_consumer_rejects_invalid_output(failure):
    prediction = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
    arrays = {"prediction": prediction, "energy": np.mean(prediction**2, axis=-1)}
    audit = audit_module()
    assert audit.check_energy(arrays)["energy_readback_passed"]
    if failure == "shape":
        arrays["energy"] = arrays["energy"][:1]
    elif failure == "nonfinite":
        arrays["energy"][0, 0] = np.nan
    elif failure == "values":
        arrays["energy"][0, 0] += 1
    else:
        del arrays["energy"]
    with pytest.raises((ValueError, KeyError)):
        audit.check_energy(arrays)
