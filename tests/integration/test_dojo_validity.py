"""实验目录、独立指标、成本和五轮调度的圈定验收；fake 不冒充正式会话。"""

import uuid
from pathlib import Path

import numpy as np
import pytest

from tools.verification.dojo_validity.io import digest, inside, inventory, read_json, write_json
from tools.verification.dojo_validity.isolation import DesktopRunner, IsolationUnavailable
from tools.verification.dojo_validity.ledger import summarize_time, summarize_usage
from tools.verification.dojo_validity.metrics import evaluate, evaluate_arrays
from tools.verification.dojo_validity.prepare import initial_prompt
from tools.verification.dojo_validity.runner import finalize, run, summarize, validate_protocol


def arm(base, group):
    """为调度测试提供结构真实、科学计算刻意不启用的材料。"""
    root = base / f"neumann-{group}"
    experiment = root / f"experiment-{uuid.uuid4()}"
    (experiment / "baseline").mkdir(parents=True)
    (experiment / "baseline/initial-checkpoint.pt").write_bytes(b"test-only")
    for name in ["evidence", "final", *[f"round-{n:02d}" for n in range(6)]]:
        (experiment / name).mkdir()
    write_json(
        experiment / "protocol.json",
        {
            "group": group,
            "experiment_id": experiment.name,
            "experiment_root": str(experiment),
            "session_workspace_root": str(root),
            "baseline_files": inventory(experiment / "baseline"),
            "rounds": 5,
            "environment_ready": False,
        },
    )
    return experiment


def usage(request_id, phase="coding", input_tokens=10, output_tokens=4):
    """包含缓存子计数的规范化供应商记录。"""
    return {
        "request_id": request_id,
        "phase": phase,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": 8,
        "cache_write_tokens": 0,
        "input_includes_cache": True,
        "output_includes_reasoning": True,
    }


def test_roots_and_independent_baseline(tmp_path):
    plain, dojo = arm(tmp_path, "plain"), arm(tmp_path, "dojo")
    a, b = validate_protocol(plain), validate_protocol(dojo)
    assert a["experiment_id"] != b["experiment_id"]
    assert a["baseline_files"] == b["baseline_files"]
    assert a["session_workspace_root"] == str(tmp_path / "neumann-plain")
    assert str(dojo) not in (plain / "protocol.json").read_text()
    (plain / "baseline/initial-checkpoint.pt").write_bytes(b"changed")
    assert (dojo / "baseline/initial-checkpoint.pt").read_bytes() == b"test-only"
    with pytest.raises(ValueError, match="baseline"):
        validate_protocol(plain)


def test_wrong_session_root_rejected(tmp_path):
    experiment = arm(tmp_path, "plain")
    protocol = read_json(experiment / "protocol.json")
    protocol["session_workspace_root"] = str(experiment)
    write_json(experiment / "protocol.json", protocol)
    with pytest.raises(ValueError, match="组级"):
        validate_protocol(experiment)


def test_prompt_materials_only_local(tmp_path):
    plain, dojo = arm(tmp_path, "plain"), arm(tmp_path, "dojo")
    a, b = [initial_prompt(validate_protocol(p)) for p in (plain, dojo)]
    assert "Dojo" not in a and "neumann-dojo" not in a
    assert "DOJO_AGENT_GUIDE.md" in b and "docs/agent-help/index.md" in b
    assert "文档学习计入编码成本" in b


def test_relative_path_and_symlink_escape(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "link").symlink_to(tmp_path / "outside")
    for path in ("../other", str(tmp_path), "link"):
        with pytest.raises(ValueError):
            inside(root, path)
    with pytest.raises(ValueError):
        inventory(root)


def test_fp64_metrics_known_answer():
    truth = {"b": np.ones((2, 3)), "a": np.full((2, 3), 2)}
    prediction = {"a": truth["a"] * 1.5, "b": truth["b"] * 2}
    result = evaluate_arrays(prediction, truth)
    assert result["final_mean_relative_l2"] == pytest.approx(0.75)
    assert result["std_relative_l2"] == pytest.approx(0.25)
    assert result["median_relative_l2"] == pytest.approx(0.75)
    assert result["p90_relative_l2"] == pytest.approx(0.95)
    assert result["mean_predicted_to_true_norm"] == pytest.approx(1.75)
    assert result["mean_mae"] == pytest.approx(1)


@pytest.mark.parametrize("bad", ["missing", "nan", "shape", "zero"])
def test_bad_sample_rejects_whole_evaluation(bad):
    targets = {"a": np.ones((2, 2))}
    predictions = {"a": targets["a"].copy()}
    if bad == "missing":
        predictions = {}
    elif bad == "nan":
        predictions["a"][0, 0] = np.nan
    elif bad == "shape":
        predictions["a"] = np.ones((1, 2))
    else:
        targets["a"][:] = 0
    with pytest.raises(ValueError):
        evaluate_arrays(predictions, targets)


def test_manifests_use_frozen_truth_and_exact_ten(tmp_path):
    for group, scale in (("pred", 2), ("truth", 1)):
        root = tmp_path / group
        root.mkdir()
        records = []
        for i in range(10):
            path = root / f"test-{i:05d}.npy"
            np.save(path, np.full((128, 128), scale, dtype=np.float32))
            records.append({"id": path.stem, "path": path.name, "sha256": digest(path)})
        write_json(root / "manifest.json", {"samples": records})
    args = (
        tmp_path / "pred/manifest.json",
        tmp_path / "truth/manifest.json",
        tmp_path / "metrics.json",
    )
    assert evaluate(*args)["final_mean_relative_l2"] == 1
    np.save(tmp_path / "pred/test-00000.npy", np.zeros((128, 128)))
    with pytest.raises(ValueError, match="摘要"):
        evaluate(*args)


def test_time_overlap_is_not_added_to_wall():
    events = [
        {"event_id": "c", "phase": "coding", "start": 0, "end": 10},
        {"event_id": "t", "phase": "training", "start": 5, "end": 20},
        {"event_id": "w", "phase": "idle_or_wait", "start": 12, "end": 25},
    ]
    result = summarize_time(events, 0, 25)
    assert result["coding_seconds"] == 10
    assert result["training_seconds"] == 15
    assert result["idle_or_wait_seconds"] == 5
    assert result["overlapping_activity_seconds"] == 5
    assert result["end_to_end_seconds"] == 25
    assert result["unaccounted_seconds"] == 0
    with pytest.raises(ValueError):
        summarize_time(events * 2, 0, 25)


def test_tokens_dedupe_cache_and_missing():
    row = usage("a")
    result = summarize_usage([row, row, usage("b", "training_observation")])
    assert result["total_accounted_tokens"] == 28
    assert result["input_tokens"] == 20
    assert result["output_tokens"] == 8
    assert result["cache_read_tokens"] == 16
    assert result["coding_tokens"] == 14
    assert result["evaluation_tokens"] is None
    assert summarize_usage([usage("missing", input_tokens=None)])["total_accounted_tokens"] is None
    assert summarize_usage([{**row, "retry_count": None}])["retry_count"] is None
    with pytest.raises(ValueError):
        summarize_usage([row, usage("a", output_tokens=99)])


class FakeRunner:
    """只用于测试控制流；永远标记 simulation，不作为隔离或训练证明。"""

    simulation = True

    def __init__(self, fail_round=None):
        self.fail_round = fail_round
        self.calls = []
        self.session = str(uuid.uuid4())

    def preflight(self, protocol):
        return {
            "workspace": protocol["session_workspace_root"],
            "all_tools_isolated": True,
            "simulation": True,
        }

    def create_session(self, protocol):
        return self.session

    def turn(self, protocol, session, number, prompt, attempt):
        self.calls.append((session, number))
        if number == self.fail_round:
            raise RuntimeError("simulated interruption")
        root = Path(protocol["experiment_root"])
        candidate = attempt / "candidate"
        candidate.mkdir()
        submission = {}
        for key in ("source", "config", "checkpoint", "predictions", "training", "summary", "diff"):
            path = candidate / key
            path.write_text(str(number))
            submission[key] = str(path.relative_to(root))
        return {
            "session_id": self.session,
            "started": number * 10,
            "ended": number * 10 + 10,
            "events": [
                {
                    "event_id": f"{number}-c",
                    "phase": "coding",
                    "start": number * 10,
                    "end": number * 10 + 10,
                }
            ],
            "usage": [usage(str(number))],
            "submission": submission,
            "text": "fake response",
        }


def fake_evaluator(frozen):
    """不做科学计算的测试指标。"""
    number = int((frozen / "checkpoint").read_text())
    return {"status": "complete", "sample_count": 10, "final_mean_relative_l2": 1 / number}


def test_five_round_resume_and_failure_evidence(tmp_path):
    experiment = arm(tmp_path, "plain")
    runner = FakeRunner(fail_round=3)
    with pytest.raises(RuntimeError, match="interruption"):
        run(experiment, runner, fake_evaluator)
    assert list((experiment / "round-03/attempts").glob("*/failure.json"))
    runner.fail_round = None
    result = run(experiment, runner, fake_evaluator)
    assert result["completed_rounds"] == [1, 2, 3, 4, 5]
    assert [n for _, n in runner.calls] == [1, 2, 3, 3, 4, 5]
    assert all(session == runner.session for session, _ in runner.calls[1:])
    assert result["simulation"] is True


def test_pair_summary_retains_simulation_label(tmp_path):
    experiments = {g: arm(tmp_path, g) for g in ("plain", "dojo")}
    comparison = tmp_path / "neumann-comparison" / "comparison-test"
    for root in experiments.values():
        run(root, FakeRunner(), fake_evaluator)
        finalize(root, 5, fake_evaluator)
    write_json(
        comparison / "comparison-protocol.json",
        {
            "experiments": {k: str(p) for k, p in experiments.items()},
            "baseline_files": validate_protocol(experiments["plain"])["baseline_files"],
        },
    )
    result = summarize(comparison)
    assert result["status"] == "simulation"
    assert all(v["completed_rounds"] == 5 for v in result["groups"].values())
    assert result["full_cost"]["plain"]["tokens"]["coding_tokens"] == 70
    assert result["framework_efficiency_ranking"]["coding_tokens"] == []


def test_real_run_fails_closed_before_session(tmp_path):
    experiment = arm(tmp_path, "plain")
    with pytest.raises(IsolationUnavailable):
        run(experiment, DesktopRunner(), None)
    state = read_json(experiment / "evidence/execution.json")
    assert state["status"] == "blocked"
    assert state["session_id"] is None
    assert not list(experiment.glob("round-*/attempts"))


def test_failed_first_turn_keeps_created_session(tmp_path):
    experiment = arm(tmp_path, "plain")
    runner = FakeRunner(fail_round=1)
    with pytest.raises(RuntimeError):
        run(experiment, runner, fake_evaluator)
    assert read_json(experiment / "evidence/execution.json")["session_id"] == runner.session
    runner.fail_round = None
    run(experiment, runner, fake_evaluator)
    assert all(session == runner.session for session, _ in runner.calls)


def test_final_selection_preserves_chosen_round_and_rejects_mutation(tmp_path):
    experiment = arm(tmp_path, "plain")
    run(experiment, FakeRunner(), fake_evaluator)
    selection = finalize(experiment, 2, fake_evaluator)
    assert selection["round"] == 2
    assert selection["metrics"]["final_mean_relative_l2"] == 0.5
    result = read_json(experiment / "round-02/result.json")
    (experiment / result["attempt"] / "frozen/checkpoint").write_text("99")
    with pytest.raises(ValueError, match="冻结"):
        finalize(experiment, 2, fake_evaluator)


def test_different_session_response_is_rejected(tmp_path):
    class WrongSession(FakeRunner):
        def turn(self, *args):
            result = super().turn(*args)
            result["session_id"] = "another-session"
            return result

    experiment = arm(tmp_path, "plain")
    with pytest.raises(ValueError, match="同一会话"):
        run(experiment, WrongSession(), fake_evaluator)


def test_partial_time_and_mixed_tokens_are_visible():
    timing = summarize_time([{"event_id": "e", "phase": "coding", "start": 2, "end": 4}], 0, 10)
    assert timing["unaccounted_seconds"] == 8
    result = summarize_usage([usage("mixed", "mixed")])
    assert result["coding_tokens"] is None
    assert result["mixed_tokens"] == 14


def test_runtime_documentation_preserves_scope():
    repo = Path(__file__).resolve().parents[2]
    readme = (repo / "tools/verification/dojo_validity/README.md").read_text()
    assert "macOS Seatbelt 整进程隔离" in readme
    assert "不以请求总量冒充编码 token" in readme
    assert "session_workspace_root" in readme and "experiment" in readme
    assert "Dojo" in (repo / "docs/PRD/recipes/parametric_pde/PRD.md").read_text()
