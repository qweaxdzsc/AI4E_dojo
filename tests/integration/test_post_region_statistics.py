"""有效实体等权统计及全部九项误差的独立对照。"""

import numpy as np
import pytest

from ai4e_core.abilities.eval.catalog import METRICS
from ai4e_core.abilities.eval.region_statistics import region_statistics
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays
from ai4e_core.applications.aero_cfd.post import evaluate_fields, read_fields
from tests.integration.test_post_visualization_fields import field_sample


def test_region_statistics_and_mask():
    row = region_statistics([1., 2., 3., np.nan], mask=np.array([True, True, True, False]), region="slice")
    assert row["mean"] == 2 and row["count"] == 3 and row["excluded"] == 1
    assert row["std"] == pytest.approx(np.sqrt(2/3))
    assert row["p90"] == pytest.approx(2.8)


def test_all_nine_metrics_share_numeric_implementation():
    sample = read_fields(field_sample())
    actual = evaluate_fields(sample, selections=["volume:velocity:magnitude"], metrics=list(METRICS))[0]
    arrays = sample["fields"]
    expected = evaluate_arrays(arrays["volume.velocity.prediction"], arrays["volume.velocity.truth"], component="magnitude", metrics=list(METRICS))
    assert actual["values"] == expected["values"]
    assert len(actual["values"]) == 9
    assert actual["values"]["r2"] is None
