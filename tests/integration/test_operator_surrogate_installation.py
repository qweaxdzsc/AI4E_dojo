"""只读取统一串行真实证据；缺证据时跳过，绝不在测试中训练或安装。"""

import json
import os
from pathlib import Path

import pytest

from tools.verification.operator_surrogates.installed_replay import OPERATOR_CASES, SURROGATE_CASES
from tools.verification.operator_surrogates.serial_matrix import COMBINATIONS


def _root():
    value = os.environ.get("DOJO_OPERATOR_SURROGATE_EVIDENCE")
    if not value:
        pytest.skip("需要真实串行与独立wheel证据；跳过不表示真实验收通过")
    return Path(value).resolve()


@pytest.mark.parametrize("combo,family,case", COMBINATIONS)
def test_real_eleven_serial_combinations_passed(combo, family, case):
    root = _root()
    candidates = sorted((root / "evidence").glob(f"{combo}-formal-*.json"))
    assert candidates, f"缺少{combo}正式证据"
    record = json.loads(candidates[-1].read_text())
    assert record["phase"] == "formal" and record["status"] == "passed"
    detail = record["result"]
    assert detail["status"] == "passed"
    assert 0 <= record["seconds"] <= 10800
    assert detail["metrics"]
    if family in {"deeponet", "fno"}:
        assert Path(detail["reference_checkpoint"]).is_file()
        assert detail["prediction_comparison"]
    else:
        assert detail["case"] == case and detail["family"] == family
        assert detail["prediction_resume_verified"] is True
        assert detail["reference_comparison"] and detail["physical_reference_comparison"]
        assert detail["reload"]["max_absolute_error"] == 0
        if family == "kriging":
            assert all(item["success"] for item in detail["diagnostics"]["targets"])
            assert all(item["success"] for item in detail["reference_fit_diagnostics"])
            assert detail["variance"]["minimum"] >= 0
            assert detail["variance"]["fixed_parameter_reference"]
        if family == "lightgbm":
            assert detail["continuation"]["exact_for_this_fixed_run"] is True
            assert all(
                value == 2 for value in detail["continuation"]["additional_actual_iterations"]
            )


@pytest.mark.parametrize("identity", OPERATOR_CASES + SURROGATE_CASES)
def test_real_eight_installed_cases_task_and_relocation(identity):
    root = _root()
    summary = json.loads((root / "evidence/installed.json").read_text())[identity]
    assert summary["status"] == "passed"
    assert summary["attempts"][-1]["status"] == "passed"
    report = json.loads(Path(summary["report"]).read_text())
    assert report["status"] == "passed" and report["case_id"] == identity
    assert report["budget_identity"] == summary["budget_identity"]
    assert report["task"]["finished"]["status"] == "succeeded"
    assert report["task"]["runtime"]["phase"] == "final"
    assert report["runtime_final"]["pid"] != report["task"]["runtime"]["pid"]
    for runtime in (report["runtime_final"], report["task"]["runtime"]):
        assert runtime["modules"]
        assert all(
            Path(path).resolve().is_relative_to(root / "installed")
            for paths in runtime["modules"].values()
            for path in paths
        )
    phases = report["phases"]
    assert phases["independent_post"]["post_identical"] is True
    assert report["relocations"]
    names = ("direct", "task") if identity in SURROGATE_CASES else ("direct", "resumed", "task")
    for name in names:
        assert phases[name]["complete_results"]["all_prepared_test_identities"] is True
        assert phases[name]["complete_results"]["all_array_hashes_checked"] is True
    if identity in SURROGATE_CASES:
        assert phases["state_readback"]["all_arrays_identical"] is True
        assert phases["state_readback"]["context_identical"] is True
        if identity.endswith("pod_surrogate_replacement"):
            assert phases["state_readback"]["state_kind"] == "local-pod-mlp-v1"
    else:
        assert (
            phases["direct"]["updates"],
            phases["resumed"]["updates"],
            phases["task"]["updates"],
        ) == (1, 2, 1)
        assert all(
            report["recovery"][name] is True
            for name in (
                "history_prefix_identical",
                "contract_identical",
                "optimizer_advanced_once",
                "stream_advanced_once",
                "weights_updated",
                "continuous_state_exact",
            )
        )
