"""真实矩阵产物的证据门禁；显式指定已运行目录，不用合成数据冒充训练。"""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from tools.verification.classic_networks.protocol import COMBINATIONS


@pytest.fixture
def evidence_root():
    value = os.environ.get("DOJO_CLASSIC_EVIDENCE")
    if not value:
        pytest.skip("需要主控十三组合真实实验目录；此跳过不属于真实验收")
    return Path(value)


@pytest.mark.parametrize("case,family", COMBINATIONS)
def test_real_matrix_and_cumulative_budget(evidence_root, case, family):
    identity = family + "-" + case
    reports = json.loads((evidence_root / "evidence/matrix.json").read_text())
    budget = json.loads((evidence_root / "budget/budget.json").read_text())
    report = reports[identity]
    assert report["status"] == "passed"
    assert report["updates"] in (20, 50, 100)
    comparison = report["reference_prediction_comparison"]
    _, fixed = read_arrays(report["outputs"]["infer"], kind="classic-results-v1")
    predicted = np.load(comparison["prediction"])["prediction"]
    np.testing.assert_allclose(predicted, fixed["prediction"], rtol=1e-5, atol=1e-6)
    recovery = report["recovery_state_comparison"]
    assert recovery["contract_compared_exactly"]
    assert {"optimizer", "stream", "python_rng", "numpy_rng", "torch_rng"} <= set(
        recovery["components"]
    )
    assert 0 < budget["combinations"][identity]["spent_seconds"] < 10800
    assert Path(report["outputs"]["train"]["checkpoint"]).is_file()
    assert Path(report["resumed"]["train"]["checkpoint"]).is_file()
    assert len(report["outputs"]["post"]["rows"]) == (2 if case == "shapenet_volume" else 8)
    if case == "shapenet_volume":
        rows = report["outputs"]["post"]["original_mesh"]["rows"]
        assert len(rows) == 2
        assert all(0 < row["coverage"] <= 1 for row in rows)
