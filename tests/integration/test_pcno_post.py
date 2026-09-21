"""固定结果、独立真值和扩展数组的实际消费。"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.model.pcno import build_model, import_weights
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.applications.geothermal.post import evaluate_results, read_results

ROOT = Path(__file__).resolve().parents[2]


def test_saved_extension_is_consumed_and_tamper_rejected(tmp_path):
    source = tmp_path / "base"
    source.mkdir()
    sample = {
        "Temp": torch.arange(21.0).reshape(1, 1, 1, 1, 21),
        "Twh": [torch.ones(2, 20)],
        "Pinj": [torch.ones(1, 20)],
    }
    torch.save(sample, source / "case.pt")
    record = {
        "version": 1,
        "kind": "results",
        "samples": [{"id": "case/0", "file": "case.pt", "sha256": digest(source / "case.pt")}],
        "truth_available": False,
        "scope": "no independent truth",
    }
    (source / "results.json").write_text(json.dumps(record))
    before = (source / "results.json").read_bytes()
    spec = importlib.util.spec_from_file_location(
        "local_pcno", ROOT / "examples/recipe_extensions/pcno/local_components.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = module.temperature_drop(source / "results.json", tmp_path / "extended")
    manifest, values = read_results(target)
    metrics = evaluate_results(manifest, values)
    assert metrics["mean"] is None
    assert metrics["derived"]["temperature_drop"] == {"mean": -19.0, "count": 1}
    assert (source / "results.json").read_bytes() == before
    np.save(tmp_path / "extended/temperature_drop.npy", np.array([0.0]))
    with pytest.raises(ValueError, match="派生数组变化"):
        read_results(target)


def test_original_weight_import_is_explicitly_not_resume(tmp_path):
    torch.manual_seed(7)
    model = build_model(branch="pres")
    source = tmp_path / "author.pt"
    torch.save({"model": model.state_dict(), "epoch": 9}, source)
    other = build_model(branch="pres")
    report = import_weights(other, source)
    assert report["mode"] == "weights_only" and not report["exact_resume"]
    assert all(torch.equal(x, other.state_dict()[k]) for k, x in model.state_dict().items())
    with pytest.raises(RuntimeError):
        import_weights(build_model(branch="temp"), source)


def test_local_constructor_replacement_changes_real_weights():
    spec = importlib.util.spec_from_file_location(
        "local_pcno", ROOT / "examples/recipe_extensions/pcno/local_components.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    torch.manual_seed(7)
    baseline = build_model(branch="pres")
    torch.manual_seed(7)
    changed = module.build_model(branch="pres")
    assert not torch.equal(list(baseline.parameters())[-1], list(changed.parameters())[-1])
