"""推理指标独立算术、不可定义值与等权样本统计验收。"""

import numpy as np
import pytest

from ai4e_core.abilities.eval.aggregation import summarize
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays
from ai4e_core.applications.aero_cfd.infer.evaluation import summarize_records


def test_physical_formulas_and_zero_denominators():
    truth = np.array([0.0, 1.0, 2.0, 4.0])[:, None]
    pred = np.array([1.0, 3.0, 1.0, 6.0])[:, None]
    metrics = [
        "relative_l2",
        "mae",
        "mse",
        "rmse",
        "max_abs_error",
        "r2",
        "relative_mae",
        "mean_relative_error",
        "mape",
    ]
    result = evaluate_arrays(pred, truth, metrics=metrics)
    expected = {
        "relative_l2": np.sqrt(10 / 21),
        "mae": 1.5,
        "mse": 2.5,
        "rmse": np.sqrt(2.5),
        "max_abs_error": 2.0,
        "r2": 1 - 10 / 8.75,
        "relative_mae": 6 / 7,
        "mean_relative_error": 1.0,
        "mape": 100.0,
    }
    assert result["values"] == pytest.approx(expected)
    assert result["relative_excluded"] == 1
    assert result["relative_threshold"] == 4e-12
    zero = evaluate_arrays(pred, np.zeros_like(pred), metrics=metrics)
    assert set(zero["undefined"]) == {
        "relative_l2",
        "r2",
        "relative_mae",
        "mean_relative_error",
        "mape",
    }
    assert all(zero["values"][k] is None for k in zero["undefined"])


def test_component_mask_and_linear_p90():
    truth = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
    pred = truth + np.array([1.0, 100.0])
    row = evaluate_arrays(
        pred, truth, component="0", mask=np.array([True, False, True]), metrics=["mae"]
    )
    assert row["values"] == {"mae": 1.0}
    assert row["count"] == 2 and row["excluded"] == 1
    result = summarize([1, 3, 9, None], expected=5, failed=1)
    assert result["mean"] == pytest.approx(13 / 3)
    assert result["median"] == 3 and result["p90"] == pytest.approx(7.8)
    assert result["valid"] == 3 and not result["complete"]


def test_performance_only_statistics_and_units():
    rows = [
        {
            "checkpoint_id": "cp",
            "checkpoint": "last",
            "split": "test",
            "field_id": "surface:p:scalar",
            "status": "succeeded",
            "values": {},
            "selected_metrics": ["prediction_seconds", "throughput"],
            "timings": {"prediction": s},
            "expected": 2,
        }
        for s in [2.0, 4.0]
    ]
    stats = {r["metric"]: r for r in summarize_records(rows)}
    assert stats["prediction_seconds"]["mean"] == 3
    assert stats["prediction_seconds"]["unit"] == "s"
    assert stats["throughput"]["throughput"] == pytest.approx(2 / 6)


def test_in_memory_evaluation_preserves_declared_validity():
    from types import SimpleNamespace
    from ai4e_core.applications.aero_cfd.infer.evaluation import evaluate_sample

    item = SimpleNamespace(name="car", domains={"surface": {
        "targets": {"pressure": "p"}, "validity": "valid"}}, payloads={
        "p.prediction": np.array([[2.], [np.nan], [6.]]),
        "p.truth": np.array([[1.], [9.], [3.]]), "valid": np.array([True, False, True])})
    rows = evaluate_sample(item, [{"id": "surface:pressure:scalar", "domain": "surface",
        "field": "pressure", "component": "scalar"}], ["mae"])
    assert rows[0]["values"]["mae"] == 2
    assert rows[0]["excluded"] == 1 and rows[0]["count"] == 2
