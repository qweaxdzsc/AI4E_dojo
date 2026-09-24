"""四会话材料因素、可信权限、冻结屏障与随机延迟顺序回归。"""

import json
from pathlib import Path

import numpy as np
import pytest

from tools.verification.dojo_validity.io import inventory, read_json, write_json
from tools.verification.dojo_validity.rmhd import factorial as f
from tools.verification.dojo_validity.rmhd.evaluate import latency_orders
from tools.verification.dojo_validity.rmhd.factorial_audit import responsibilities, reuse_sets


def test_expanded_reuse_counts_imported_body_and_deduplicates_copy():
    local = {f"local:{i}" for i in range(12)}
    dojo = {f"dojo:{i}" for i in range(100)}
    result = reuse_sets(
        local,
        dojo,
        provided={"local:0"},
        imports={"local:1"},
        copied_origin={"local:2": "dojo:0", "local:3": "dojo:0"},
    )
    assert result["expanded_dojo_sloc"] == 100
    assert result["expanded_implementation_sloc"] == 108
    assert result["expanded_dojo_reuse_ratio"] == 100 / 108
    assert result["dojo_copied_retained_sloc"] == 1
    assert reuse_sets(set(), set())["expanded_dojo_reuse_ratio"] is None
    with pytest.raises(ValueError):
        reuse_sets(local, dojo, copied_origin={"not-executed:9": "dojo:1"})


def test_responsibility_import_only_not_use_and_unknown_not_zero():
    rows = [
        {"needed": True, "availability": "direct", "adopted": True, "executed": False},
        {
            "needed": True,
            "availability": "adaptable",
            "adopted": True,
            "executed": True,
            "evidence": ["training trace"],
        },
        {"needed": True, "availability": "unknown"},
    ]
    r = responsibilities(rows)
    assert r["adopted_executed"] == 1 and r["known_applicable"] == 2
    assert r["lower"] == 1 / 3 and r["upper"] == 2 / 3


def test_round_cost_uses_interval_union_and_preserves_missing_tokens():
    from tools.verification.dojo_validity.rmhd.factorial_report import round_cost

    c = {
        "time": {
            "intervals": [
                {"round": 0, "phase": "coding", "start": 1, "end": 4},
                {"round": 0, "phase": "coding", "start": 2, "end": 5},
                {"round": 1, "phase": "coding", "start": 8, "end": 9},
            ]
        },
        "tokens": {
            "raw_requests": [
                {"round": 0, "phase": "coding", "input_tokens": 10, "output_tokens": 5},
                {"round": 0, "phase": "mixed", "input_tokens": 20, "output_tokens": 5},
                {"round": 0, "phase": "coding", "input_tokens": None, "output_tokens": None},
            ]
        },
    }
    r = round_cost(c, 0)
    assert r["seconds"]["coding"] == 4
    assert r["coding_tokens_lower"] == 15 and r["coding_tokens_upper"] is None
    assert r["total_accounted_tokens"] == 40 and r["missing_fields_requests"] == 1
    assert round_cost({"time": None, "tokens": None}, 0)["seconds"]["coding"] is None


def test_replay_includes_local_script_glue_but_not_unused_definitions(tmp_path):
    import runpy

    from tools.verification.dojo_validity.rmhd.trace_replay import ReplayCoverage

    source = tmp_path / "run.py"
    source.write_text(
        "import math\ndef unused():\n    return 999\ndef used(x):\n    return x+1\nvalue=used(3)\n"
    )
    trace = ReplayCoverage({"local": tmp_path})
    trace.start()
    try:
        runpy.run_path(str(source), run_name="__main__")
    finally:
        trace.stop()
    result = trace.save(tmp_path / "trace.json")
    assert result["local_module_execution"][0]["executed_lines"] == [6]
    assert result["files"][0]["function_lines"] == [4, 5]


def test_import_side_effect_is_not_scientific_reuse(tmp_path, monkeypatch):
    import runpy
    import sys

    from tools.verification.dojo_validity.rmhd.trace_replay import ReplayCoverage

    module = "audit_import_side_effect_fixture"
    (tmp_path / f"{module}.py").write_text(
        "def register():\n    return 3\n"
        "def compute(x):\n    return x+1\n"
        "registration=register()\ninitial=compute(0)\n"
    )
    script = tmp_path / "run.py"
    script.write_text(f"import {module}\nresult={module}.compute(4)\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    trace = ReplayCoverage({"local": tmp_path})
    trace.start()
    try:
        runpy.run_path(str(script), run_name="__main__")
    finally:
        trace.stop()
        sys.modules.pop(module, None)
    result = trace.save(tmp_path / "trace.json")
    functions = {fn["name"] for row in result["files"] for fn in row["functions"]}
    assert functions == {"compute"}
    assert {row["function"] for row in result["import_context_calls_excluded"]} >= {
        "register",
        "compute",
    }


from tools.verification.dojo_validity.rmhd.factorial_materials import CELLS, instructions


def test_latency_windows_reproducible_balanced_and_varied():
    first = list(latency_orders(45, 42))
    again = list(latency_orders(45, 42))
    assert len(first) == 3
    for a, b in zip(first, again, strict=True):
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(np.bincount(a), np.full(45, 5))
    assert not np.array_equal(first[0], first[1])
    with pytest.raises(ValueError):
        list(latency_orders(0, 42))


def setup_study(tmp_path):
    root = tmp_path / "comparison"
    config = {"experiments": {}, "model": "fixed", "reasoning": "low", "runtime_readonly_roots": []}
    for group, cell in CELLS.items():
        exp = tmp_path / (cell["slug"] + "-study") / ("experiment-" + group)
        exp.mkdir(parents=True)
        write_json(exp / "protocol.json", {"session_workspace_root": "/", "model": "spoofed"})
        (exp / "SUBMISSION.md").write_text(instructions(cell["baseline_provided"]))
        (exp / "activity.py").write_text("# fixture")
        (exp / "environment").mkdir()
        (exp / "environment/runtime").write_text("runtime")
        write_json(root / f"evidence/{group}-initial-materials.json", inventory(exp))
        config["experiments"][group] = str(exp)
    config["round_orders"] = {str(n): list(CELLS)[n % 4 :] + list(CELLS)[: n % 4] for n in range(6)}
    write_json(root / "comparison-protocol.json", config)
    write_json(root / "state.json", {"phase": "ready"})
    for name in (
        "material-audit",
        "isolation-all",
        "cli-capability",
        "worker-check",
        "runtime-capability",
    ):
        write_json(root / f"evidence/{name}.json", {"passed": True})
    write_json(root / "private-split.json", {"splits": {"test": []}})
    return root, config


def test_independent_material_copy_is_not_hardlink(tmp_path):
    from tools.verification.dojo_validity.rmhd.runtime import independent_copy

    source = tmp_path / "source"
    source.write_text("original")
    copy = independent_copy(source, tmp_path / "copy")
    assert source.stat().st_ino != copy.stat().st_ino
    source.write_text("modified")
    assert copy.read_text() == "original" and copy.stat().st_nlink == 1


def test_runtime_gate_is_required_before_formal_dispatch(tmp_path):
    root, _ = setup_study(tmp_path)
    write_json(root / "evidence/runtime-capability.json", {"passed": False})
    with pytest.raises(ValueError, match="runtime-capability"):
        f.run(root)
    assert read_json(root / "state.json")["phase"] == "ready"


def test_runtime_file_alias_chain_does_not_open_sibling_files(tmp_path):
    import sys

    from tools.verification.dojo_validity.rmhd.isolation import execute, policy

    if sys.platform != "darwin":
        pytest.skip("Seatbelt requires macOS")
    own = tmp_path / "own"
    own.mkdir()
    libs = tmp_path / "libs"
    libs.mkdir()
    (libs / "versioned").write_text("public runtime")
    (libs / "private").write_text("forbidden")
    (libs / "library").symlink_to("versioned")
    alias = tmp_path / "alias"
    alias.symlink_to(libs, target_is_directory=True)
    body = policy([own], [alias / "library"])
    allowed = execute(body, ["/bin/cat", alias / "library"], own)
    denied = execute(body, ["/bin/cat", alias / "private"], own)
    assert allowed.returncode == 0 and allowed.stdout == "public runtime"
    assert denied.returncode != 0


def submission(exp, n):
    path = Path(exp) / f"round-{n:02d}/submission"
    path.mkdir(parents=True)
    for name in ("predict.py", "checkpoint.pt", "stats.json"):
        (path / name).write_text("fixture")
    write_json(
        path / "submission.json",
        {
            "interface": "rmhd-predict-v1",
            "round": n,
            "entrypoint": "predict.py",
            "checkpoint": "checkpoint.pt",
            "statistics": "stats.json",
            "method": "fake runner",
            "dojo_usage": [],
        },
    )
    return path


def test_open_model_materials_do_not_inherit_unet_recipe():
    text = instructions(False).lower()
    for token in ("unet", "u-net", "500", "2500", "495998", "adam", "baseline-evidence"):
        assert token not in text
    assert "sampling_schedule_sha256" in instructions(True)
    assert "audit-replay" in text


def test_authority_comes_from_controller_and_tamper_is_rejected(tmp_path):
    root, cfg = setup_study(tmp_path)
    exp = Path(cfg["experiments"]["NP"])
    p = f.Driver(root).trusted_protocol("NP", str(exp))
    assert p["session_workspace_root"] == str(exp.parent)
    assert p["model"] == "fixed" and p["runtime_readonly_roots"] == []
    assert not p["baseline_provided"] and not p["dojo_available"]
    (exp / "protocol.json").write_text("{}")
    with pytest.raises(ValueError, match="修改"):
        f.Driver(root).trusted_protocol("NP", str(exp))
    cfg["experiments"]["NP"] = cfg["experiments"]["BP"]
    with pytest.raises(ValueError):
        f.validate_cell_config(cfg)


def test_fake_24_candidates_before_hidden_and_selection_is_immutable(tmp_path):
    root, cfg = setup_study(tmp_path)
    events = []

    class Fake:
        def round(self, group, number, location):
            with pytest.raises(ValueError, match="禁止隐藏"):
                f.hidden(root)
            events.append((number, group))
            return submission(location, number)

        def select_final(self, group, location):
            assert len(events) == 24
            with pytest.raises(ValueError, match="禁止隐藏"):
                f.hidden(root)
            return {"round": 2, "validation_reason": "fixture"}

    f.run(root, Fake())
    assert events == [(n, g) for n in range(6) for g in cfg["round_orders"][str(n)]]
    assert read_json(root / "state.json")["phase"] == "all_finals_locked"
    calls = []

    def evaluator(group, n, candidate, out):
        calls.append((group, n))
        assert candidate.is_dir()
        return {"status": "invalid", "eligible": False}

    f.hidden(root, evaluator)
    assert len(calls) == 24
    assert not list(tmp_path.glob("rmhd-*/experiment-*/hidden-results"))
    with pytest.raises(ValueError):
        f.lock(root, "BP", {"round": 1})
    with pytest.raises(ValueError):
        f.run(root, Fake())
    assert read_json(root / "final-selections/BP.json")["round"] == 2


def test_candidate_links_and_modified_frozen_bytes_rejected(tmp_path):
    root, cfg = setup_study(tmp_path)
    write_json(root / "state.json", {"phase": "running"})
    source = submission(cfg["experiments"]["BP"], 0)
    f.freeze(root, "BP", 0, source)
    target = f.verify_frozen(root, "BP", 0) / "predict.py"
    target.chmod(0o644)
    target.write_text("tampered")
    with pytest.raises(ValueError, match="变更"):
        f.verify_frozen(root, "BP", 0)
    source2 = submission(cfg["experiments"]["BD"], 0)
    (source2 / "leak").symlink_to(root / "private-split.json")
    with pytest.raises(ValueError):
        f.freeze(root, "BD", 0, source2)


def test_four_group_report_keeps_validation_selection_and_unknown_audit(tmp_path, monkeypatch):
    from tools.verification.dojo_validity.rmhd import factorial_report as report

    root, _cfg = setup_study(tmp_path)

    class Fake:
        def round(self, group, number, location):
            source = submission(location, number)
            write_json(source / "stats.json", {})
            write_json(
                root / f"validation/{group}/round-{number:02d}/one/result.json",
                {
                    "status": "evaluated",
                    "eligible": True,
                    "accuracy": {"mean_field_relative_l2": 1 / (number + 1)},
                },
            )
            return source

        def select_final(self, group, location):
            return {"round": 2, "validation_reason": "fixture"}

    f.run(root, Fake())

    def evaluator(group, n, candidate, out):
        return {
            "status": "evaluated",
            "eligible": True,
            "accuracy": {"mean_field_relative_l2": 1 / (n + 1)},
            "latency_p95_seconds": 0.02,
        }

    f.hidden(root, evaluator)
    monkeypatch.setattr(
        report, "collect", lambda *a: {"status": "missing", "time": None, "tokens": None}
    )
    monkeypatch.setattr(report, "plot", lambda *a: None)
    monkeypatch.setattr(report, "plot_details", lambda *a: None)
    result = report.summarize(root)
    assert set(result["groups"]) == set(CELLS)
    assert result["groups"]["BD"]["final"]["accuracy"]["mean_field_relative_l2"] == 1 / 3
    assert result["groups"]["BD"]["posthoc_best_eligible_round"] == 5
    assert (
        result["science_complete"]
        and not result["cost_complete"]
        and not result["reuse_audit_complete"]
    )
    assert not list(tmp_path.glob("rmhd-*/experiment-*/REPORT.md"))


def test_detail_series_preserves_unknown_and_expanded_numerator_denominator():
    from tools.verification.dojo_validity.rmhd.factorial_report import detail_series

    row = {
        "round": 0,
        "final_selected": True,
        "cost": {"seconds": {"coding": 12}, "coding_tokens_lower": 20, "coding_tokens_upper": None},
        "validation": {"accuracy": {"per_field_relative_l2": {"rho": 0.3}}},
        "hidden": {"status": "failed"},
        "reuse": {
            "status": "partial",
            "whole_pipeline": reuse_sets({"local:1"}, {"dojo:1", "dojo:2"}),
        },
    }
    values = detail_series({"BD": {"rounds": [row]}})[0]
    assert values["whole_pipeline_expanded_dojo_sloc"] == 2
    assert values["whole_pipeline_expanded_implementation_sloc"] == 3
    assert values["prediction_expanded_dojo_sloc"] is None
    assert values["responsibility_numerator"] is None
    assert values["validation_rho"] == 0.3 and values["hidden_rho"] is None
    assert values["coding_tokens_upper"] is None


def test_trace_positions_deduplicates_paths_excludes_imports_and_rejects_drift(tmp_path):
    import hashlib

    from tools.verification.dojo_validity.rmhd.factorial_audit import trace_positions

    source = "def run():\n    import math\n    return math.sqrt(4)\n"
    sha = hashlib.sha256(source.encode()).hexdigest()
    rows = []
    for name in ("a.py", "b.py"):
        file = tmp_path / name
        file.write_text(source)
        rows.append(
            {
                "file": str(file),
                "package": "local",
                "relative": name,
                "sha256": sha,
                "function_lines": [1, 2, 3],
                "executed_lines": [2, 3],
            }
        )
    positions = trace_positions([{"files": rows}])
    summary = reuse_sets(**{k: positions[k] for k in ("local", "dojo", "provided", "imports")})
    assert summary["local_implementation_sloc"] == 2
    assert len(positions["executed_positions"]) == 1
    supplied = trace_positions([{"files": rows}], provided_sha256=[sha])
    assert supplied["provided"] == supplied["local"]
    file.write_text(source + "# drift\n")
    with pytest.raises(ValueError, match="摘要变化"):
        trace_positions([{"files": rows}])


def test_descriptive_interaction_requires_four_eligible_positive_scores():
    import math

    from tools.verification.dojo_validity.rmhd.factorial_report import descriptive_effects

    groups = {
        g: {"final": {"eligible": True, "accuracy": {"mean_field_relative_l2": e}}}
        for g, e in {"BP": 0.4, "BD": 0.2, "NP": 0.8, "ND": 0.2}.items()
    }
    result = descriptive_effects(groups)
    assert result["interaction_open_minus_given"]["log_error_ratio_difference"] == pytest.approx(
        math.log(0.5)
    )
    groups["ND"]["final"]["eligible"] = False
    assert (
        descriptive_effects(groups)["interaction_open_minus_given"]["log_error_ratio_difference"]
        is None
    )
    assert descriptive_effects(groups)["ND/NP"]["accuracy_difference"] == pytest.approx(-0.6)


def test_verified_storage_clone_preserves_bytes_mode_and_independence(tmp_path):
    import hashlib
    import stat

    from tools.verification.dojo_validity.rmhd.runtime import clone_verified_file

    source, target = tmp_path / "source", tmp_path / "target"
    source.write_bytes(b"frozen library")
    target.write_bytes(source.read_bytes())
    target.chmod(0o444)
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    result = clone_verified_file(source, target, sha)
    assert result["independent"] and result["sha256"] == sha
    assert stat.S_IMODE(target.stat().st_mode) == 0o444
    source.write_text("changed source")
    assert target.read_bytes() == b"frozen library"
    with pytest.raises(ValueError, match="摘要"):
        clone_verified_file(source, target, sha)
    assert target.read_bytes() == b"frozen library"


def test_interrupted_phase_stays_unknown_after_cli_resume(tmp_path):
    from tools.verification.dojo_validity.rmhd.accounting import incomplete_activities

    for name, start, completed in (
        ("interrupted", 12, False),
        ("resumed", 32, True),
        ("still_running", 52, False),
    ):
        folder = tmp_path / "evidence/activities" / name
        folder.mkdir(parents=True)
        write_json(
            folder / "started.json",
            {"event_id": name, "phase": "training", "start": start, "command": ["train.py"]},
        )
        if completed:
            write_json(folder / "completed.json", {"end": 39, "exit_code": 0})
    rows = incomplete_activities(tmp_path, [(10, 20), (30, 40)])
    assert [row["event_id"] for row in rows] == ["interrupted"]
    assert rows[0]["end"] is None and rows[0]["exit_code"] is None


def test_cli_cumulative_and_reset_usage_reconcile_without_double_count():
    from tools.verification.dojo_validity.rmhd.accounting import reconcile_cli_totals

    requests = {
        key: {
            "request_id": key,
            "phase": "coding",
            "input_tokens": value,
            "output_tokens": 1,
            "cache_read_tokens": value // 2,
            "cache_write_tokens": 0,
        }
        for key, value in zip("abcd", (10, 20, 30, 40), strict=True)
    }

    def report(ids, input_tokens, output_tokens):
        return {
            "source": ids,
            "request_ids": list(ids),
            "summaries": [
                {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cached_input_tokens": input_tokens // 2,
                }
            ],
        }

    result = reconcile_cli_totals(
        [report("a", 10, 1), report("ab", 30, 2), report("abcd", 70, 2)], requests
    )
    assert result["matches"]
    assert result["request_total"] == result["cli_covered_request_total"] == 104
    assert [r["request_ids"] for r in result["reports"]] == [["a"], ["a", "b"], ["c", "d"]]
    assert result["uncovered_request_ids"] == []


def test_missing_cli_process_receipt_is_not_reconstructed_from_last_event(tmp_path):
    from tools.verification.dojo_validity.rmhd.accounting import unclosed_cli_attempts

    for name in ("interrupted", "resumed", "still_running"):
        folder = tmp_path / "round-03" / name
        folder.mkdir(parents=True)
        (folder / "events.jsonl").write_text(
            '{"received": 10, "event": {"type": "turn.started"}}\n'
            '{"received": 20, "event": {"type": "item.completed"}}\n'
        )
        if name == "resumed":
            write_json(folder / "process.json", {"started": 10, "ended": 22, "returncode": 0})
    rows = unclosed_cli_attempts(tmp_path)
    assert [Path(r["source"]).name for r in rows] == ["interrupted", "still_running"]
    assert all(r["last_observed"] == 20 and r["end"] is None for r in rows)
    assert all(r["start"] is None and r["exit_code"] is None for r in rows)
    assert all(r["status"] == "open_or_interrupted" for r in rows)


def test_unclosed_cli_with_truncated_event_remains_visible(tmp_path):
    from tools.verification.dojo_validity.rmhd.accounting import collect

    folder = tmp_path / "evidence/sessions/ND/round-03/attempt"
    folder.mkdir(parents=True)
    (folder / "events.jsonl").write_text('{"received":')
    result = collect(tmp_path, "ND")
    assert result["status"] == "missing" and result["time"] is None
    assert result["unclosed_cli_attempts"][0]["last_observed"] is None
    assert result["unclosed_cli_attempts"][0]["malformed_event_lines"] == 1


def test_cli_usage_missing_mismatch_and_uncovered_requests_remain_unresolved():
    from tools.verification.dojo_validity.rmhd.accounting import reconcile_cli_totals

    requests = {"a": {"request_id": "a", "phase": "coding", "input_tokens": 10, "output_tokens": 2}}
    for summaries in (
        [],
        [{"input_tokens": 10}],
        [{"input_tokens": 11, "output_tokens": 2}],
        [{"input_tokens": 10, "output_tokens": 2, "cached_input_tokens": None}],
        [{"input_tokens": 10, "output_tokens": 2, "cached_input_tokens": 5}],
    ):
        result = reconcile_cli_totals(
            [{"source": "attempt", "request_ids": ["a"], "summaries": summaries}], requests
        )
        assert not result["matches"]
        assert result["uncovered_request_ids"] == ["a"]
        assert result["cli_covered_request_total"] is None
    assert reconcile_cli_totals([], requests)["request_total"] == 12


def test_unknown_command_usage_is_not_assumed_coding():
    from tools.verification.dojo_validity.rmhd.accounting import response_phase

    def call(command):
        return {"name": "exec_command", "arguments": json.dumps({"cmd": command})}

    assert response_phase(call("python long_job.py")) == "unclassified"
    assert response_phase(call("cat recipe/train.py")) == "coding"
    assert (
        response_phase(call("python activity.py training -- python train.py"))
        == "training_observation"
    )
    assert (
        response_phase(call("python activity.py data_preparation -- python prepare.py"))
        == "data_preparation"
    )


def test_unknown_time_is_separate_from_waiting_and_coding():
    from tools.verification.dojo_validity.ledger import summarize_time

    result = summarize_time(
        [
            {"event_id": "outer", "phase": "idle_or_wait", "start": 0, "end": 10},
            {"event_id": "unknown", "phase": "unclassified", "start": 1, "end": 8},
            {"event_id": "observed", "phase": "training", "start": 3, "end": 6},
        ],
        0,
        10,
    )
    assert result["coding_seconds"] == 0
    assert result["training_seconds"] == 3
    assert result["unclassified_seconds"] == 4
    assert result["idle_or_wait_seconds"] == 3
    assert result["overlapping_activity_seconds"] == 0
    assert result["unaccounted_seconds"] == 0

    from tools.verification.dojo_validity.rmhd.factorial_report import round_cost

    events = [e | {"round": 2} for e in result["intervals"]]
    per_round = round_cost({"time": {"intervals": events}}, 2)
    assert per_round["seconds"]["coding"] == 0
    assert per_round["seconds"]["unclassified"] == 4


def test_coding_heredoc_does_not_label_following_training_as_coding():
    from tools.verification.dojo_validity.rmhd.accounting import activity, response_phase

    command = "python activity.py coding -- python - <<'PY'\nprint('a;b')\nPY\npython replay_train.py independent 5000"
    assert activity(command) == "mixed"
    assert activity("/bin/zsh -lc " + __import__("shlex").quote(command)) == "mixed"
    assert (
        response_phase({"name": "exec_command", "arguments": json.dumps({"cmd": command})})
        == "mixed"
    )
    assert activity("python activity.py coding -- python -c 'print(1); print(2)'") == "coding"
    assert activity("cat config.yaml && python long_job.py") == "mixed"
    assert (
        activity(
            "python activity.py coding -- python edit.py; python activity.py training -- python train.py"
        )
        == "mixed"
    )
    assert activity("python activity.py training -- python train.py") == "training"
    assert activity("python activity.py coding -- python - <<'PY'\nprint(1)") == "unclassified"


def test_native_unknown_command_does_not_become_coding(tmp_path, monkeypatch):
    from tools.verification.dojo_validity.rmhd import audit
    from tools.verification.dojo_validity.rmhd.accounting import collect

    directory = tmp_path / "evidence/sessions/BP/round-00/attempt"
    directory.mkdir(parents=True)
    (directory / "prompt.txt").write_text("test")
    write_json(directory / "process.json", {"started": 1, "ended": 6, "returncode": 0})
    item = {"id": "job", "type": "command_execution", "command": "python long_job.py"}
    rows = [
        {"received": 2, "event": {"type": "item.started", "item": item}},
        {"received": 5, "event": {"type": "item.completed", "item": item | {"exit_code": 0}}},
    ]
    (directory / "events.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    monkeypatch.setattr(audit, "archive_group", lambda *a: {"activity_helper_matches": False})
    result = collect(tmp_path, "BP")
    assert result["time"]["coding_seconds"] == 0
    assert result["time"]["unclassified_seconds"] == 3
    assert result["status"] == "partial"


def test_unclosed_event_envelope_is_unknown_not_recovered_process_time():
    from tools.verification.dojo_validity.rmhd.accounting import observed_unclosed_intervals

    row = {
        "source": "/sessions/ND/round-03/interrupted",
        "first_observed": 12,
        "last_observed": 18,
        "start": None,
        "end": None,
        "exit_code": None,
    }
    observed = observed_unclosed_intervals([row], 10, 20)
    assert observed[0]["phase"] == "unclassified"
    assert observed[0]["round"] == 3
    assert (observed[0]["start"], observed[0]["end"]) == (12, 18)
    assert "not process endpoints" in observed[0]["source"]
    assert row["start"] is None and row["end"] is None and row["exit_code"] is None
    assert observed_unclosed_intervals([row], 20, 25) == []

    from tools.verification.dojo_validity.rmhd.factorial_report import classified_queue_gaps

    gap = {"phase": "idle_or_wait", "source": "controller scheduling gap", "start": 10, "end": 20}
    assert classified_queue_gaps({"intervals": [gap, *observed]}) == [(10, 12), (18, 20)]
