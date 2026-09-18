"""通过真实Task比较固定结果，覆盖清单之外的数组依赖和科学口径。"""

import json
import shutil
from pathlib import Path

import ai4e_task as task
import numpy as np
import pytest
import yaml

from ai4e_core.abilities.data.save.array_manifest import save_arrays
from tools.verification.wdno.task_replay import managed

ROOT = Path(__file__).resolve().parents[2]


def result_set(root, *, prediction=1, target=0, ids=(1, 2)):
    """小数组只用于指标管理测试，不冒充WDNO模型预测。"""
    return {
        split: save_arrays(
            root / split,
            {
                "ids": np.array(ids),
                "prediction": np.full((2, 3, 4), prediction, dtype=np.float32),
                "target": np.full((2, 3, 4), target, dtype=np.float32),
                "energy": np.full((2, 3), prediction**2, dtype=np.float32),
            },
            kind="spatiotemporal-result-v1",
            metadata={},
        )
        for split in ("validation", "test")
    }


@pytest.fixture(scope="module")
def evaluated(tmp_path_factory):
    root = tmp_path_factory.mktemp("wdno-metrics")
    code = root / "recipe"
    shutil.copytree(ROOT / "recipes/wdno", code, ignore=shutil.ignore_patterns("__pycache__"))
    cfg = yaml.safe_load((code / "config.yaml").read_text())
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["rawprep"] = {"source": None, "indices": None}
    cfg["inputs"]["post"] = result_set(root / "original")
    cfg["components"]["network"] = "not_installed.network"
    project = root / "project"
    task.create_project(project)
    current = task.new_task(project, "fixed-results", source=code, configuration=cfg)
    first, a = managed(project, current, cfg)
    _, b = managed(project, current, cfg)
    assert first["reports"]["post"]["test"]["mse"] == 1
    return root, project, current, cfg, a, b


@pytest.mark.parametrize(
    "filename", ["manifest.json", "prediction.npy", "target.npy", "ids.npy", "energy.npy"]
)
@pytest.mark.parametrize("operation", ["change", "remove"])
def test_changed_array_invalidates_only_affected_split(evaluated, filename, operation):
    _, project, _, cfg, a, b = evaluated
    path = Path(cfg["inputs"]["post"]["test"]).parent / filename
    original = path.read_bytes()
    try:
        if operation == "remove":
            path.unlink()
        else:
            path.write_bytes(original + b"changed")
        values = task.compare_runs(project, a["id"], b["id"])["metrics"]
        assert values["post/test_mse"]["status"] == "missing"
        assert values["post/validation_mse"]["status"] == "available"
    finally:
        path.write_bytes(original)


@pytest.mark.parametrize(
    ("change", "expected"),
    [("prediction", "available"), ("target", "incompatible"), ("ids", "incompatible")],
)
def test_prediction_is_integrity_not_comparison_identity(evaluated, change, expected):
    root, project, current, cfg, a, _ = evaluated
    other = {
        **cfg,
        "inputs": {
            **cfg["inputs"],
            "post": result_set(root / change, **{change: (3, 4) if change == "ids" else 2}),
        },
    }
    _, b = managed(project, current, other)
    comparison = task.compare_runs(project, a["id"], b["id"])
    assert {v["status"] for v in comparison["metrics"].values()} == {expected}


@pytest.mark.parametrize("field", ["definition", "unit", "statistic", "data_identity"])
def test_different_or_missing_scientific_semantics(evaluated, field):
    _, project, _, _, a, b = evaluated
    path = project / b["run_path"] / "artifacts/metrics.json"
    original = path.read_bytes()
    try:
        value = json.loads(original)
        semantics = value["items"]["post/test_mse"]["semantics"]
        semantics[field] = "deliberately-different"
        path.write_text(json.dumps(value))
        assert (
            task.compare_runs(project, a["id"], b["id"])["metrics"]["post/test_mse"]["status"]
            == "incompatible"
        )
        if field != "definition":
            del semantics[field]
            path.write_text(json.dumps(value))
            assert (
                task.compare_runs(project, a["id"], b["id"])["metrics"]["post/test_mse"]["status"]
                == "missing"
            )
    finally:
        path.write_bytes(original)


@pytest.mark.parametrize("failure", ["escape", "missing"])
@pytest.mark.parametrize("entry", ["assets", "metrics"])
def test_publishing_rejects_invalid_array_dependencies(tmp_path, failure, entry):
    from ai4e_contrib.ability.eval.wdno.physical import metrics
    from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import (
        record_arrays,
        record_metrics,
    )
    from ai4e_core.run.writer import RunWriter

    results = result_set(tmp_path / "results")
    path = Path(results["test"])
    record = json.loads(path.read_text())
    record["fields"]["prediction"]["path"] = (
        "../../outside.npy" if failure == "escape" else "absent.npy"
    )
    path.write_text(json.dumps(record))
    writer = RunWriter.create(tmp_path / "runs")
    with pytest.raises(ValueError if failure == "escape" else FileNotFoundError):
        if entry == "assets":
            record_arrays(writer, {"test": str(path)}, kind="other", stage="post")
        else:
            record_metrics(writer, {"test": str(path)}, {"test": {"mse": 1.0}}, metrics)
