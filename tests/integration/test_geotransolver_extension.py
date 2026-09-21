"""误差数组实际保存读回和独立消费者校验。"""

import importlib.util
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays


def test_extension_changes_objective_and_consumes_saved_array(tmp_path):
    path = (
        Path(__file__).resolve().parents[2] / "examples/recipe_extensions/geotransolver/variants.py"
    )
    spec = importlib.util.spec_from_file_location("variants", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    p = torch.tensor([[1.5], [1.5]])
    t = torch.ones_like(p)
    assert module.squared_relative_loss(p, t) == 0.25
    arrays = {
        "prediction": np.ones((2, 1, 4, 1), dtype="float32") * 1.5,
        "target": np.ones((2, 1, 4, 1), dtype="float32"),
    }
    extra, description = module.error_field(arrays)
    manifest = save_arrays(
        tmp_path / "fixed", {**arrays, **extra}, kind="extension", metadata=description
    )
    _, restored = read_arrays(manifest, kind="extension")
    assert module.consume_error(restored, description) == {"max_abs_error": 0.5}
