"""RMHD 科学口径、最小材料、冻结顺序和真实操作系统边界验收。"""

import socket
import sys
from pathlib import Path

import numpy as np
import pytest

from tools.verification.dojo_validity.io import digest, read_json, write_json
from tools.verification.dojo_validity.rmhd.controller import (
    evaluate_hidden,
    freeze_round,
    lock_final,
    run_pair,
    verify_frozen,
)
from tools.verification.dojo_validity.rmhd.isolation import clean_environment, execute, policy
from tools.verification.dojo_validity.rmhd.metrics import aggregate, field_errors
from tools.verification.dojo_validity.rmhd.model import UNet
from tools.verification.dojo_validity.rmhd.network import PublicProxy, public_addresses
from tools.verification.dojo_validity.rmhd.protocol import gate
from tools.verification.dojo_validity.rmhd.sessions import CliDriver, prompt
from tools.verification.dojo_validity.rmhd.verification import schedule_digest


def candidate(root, number):
    """冻结测试不用可执行 checkpoint，不运行任何候选代码。"""
    root.mkdir(parents=True)
    for name in ("predict.py", "weights.pt", "statistics.json"):
        (root / name).write_text("test fixture")
    write_json(
        root / "submission.json",
        {
            "interface": "rmhd-predict-v1",
            "round": number,
            "entrypoint": "predict.py",
            "checkpoint": "weights.pt",
            "statistics": "statistics.json",
            "method": "fixture",
            "dojo_usage": [],
        },
    )
    return root


def test_group_protocol_cannot_expand_controller_authority(tmp_path):
    experiment = tmp_path / "jorek-rmhd-plain/experiment-one"
    comparison = tmp_path / "controller"
    path = experiment / "protocol.json"
    original = {
        "session_workspace_root": "/",
        "runtime_readonly_roots": ["/Users"],
        "model": "agent-modified",
    }
    write_json(path, original)
    write_json(
        comparison / "evidence/plain-initial-materials.json", {"protocol.json": digest(path)}
    )
    write_json(
        comparison / "comparison-protocol.json",
        {
            "experiments": {"plain": str(experiment)},
            "runtime_readonly_roots": ["/approved-runtime"],
            "model": "trusted-model",
            "reasoning": "high",
        },
    )
    driver = CliDriver(comparison)
    actual = driver.trusted_protocol("plain", experiment)
    assert actual["session_workspace_root"] == str(experiment.parent)
    assert actual["runtime_readonly_roots"] == ["/approved-runtime"]
    assert actual["model"] == "trusted-model"
    write_json(path, original | {"runtime_readonly_roots": ["/"]})
    with pytest.raises(ValueError, match="已修改"):
        driver.trusted_protocol("plain", experiment)
    with pytest.raises(ValueError, match="路径"):
        driver.trusted_protocol("plain", tmp_path)


def test_model_is_network_only_and_count():
    model = UNet()
    assert sum(p.numel() for p in model.parameters()) == 495998
    import torch

    assert model(torch.zeros(1, 60, 100, 100)).shape == (1, 30, 100, 100)


def test_loaded_model_count_handles_wrapped_ensemble_and_shared_weights():
    import torch

    from tools.verification.dojo_validity.rmhd.worker import loaded_models

    model = torch.nn.Linear(2, 3)

    @torch.inference_mode()
    def component(x):
        return model(x)

    predictors = {"one": component, "shared": component}

    def ensemble(x):
        return sum(fn(x) for fn in predictors.values())

    result = loaded_models(ensemble)
    assert result["total_parameter_count"] == 9
    assert len(result["module_classes"]) == 1
    assert loaded_models(lambda x: x)["total_parameter_count"] is None


def test_report_uses_controller_validation_and_keeps_final_selection(tmp_path, monkeypatch):
    from tools.verification.dojo_validity.rmhd import report

    write_json(tmp_path / "state.json", {"phase": "hidden_evaluated_accounting_pending"})
    for group in ("plain", "dojo"):
        write_json(tmp_path / "final-selections" / f"{group}.json", {"round": 1})
        for number in range(6):
            path = candidate(tmp_path / "frozen" / group / f"round-{number:02d}", number)
            write_json(
                tmp_path / "receipts" / group / f"round-{number:02d}.json",
                {
                    "source_manifest": read_json(path / "submission.json"),
                },
            )
            row = {
                "status": "evaluated",
                "eligible": True,
                "accuracy": {"mean_field_relative_l2": 1 / (number + 1)},
            }
            write_json(tmp_path / "hidden-results" / group / f"round-{number:02d}/result.json", row)
            write_json(
                tmp_path / "validation" / group / f"round-{number:02d}/attempt/result.json", row
            )

    def costs(root, group):
        lower = 1 if group == "plain" else 4
        return {
            "status": "accounted",
            "time": {"coding_seconds": 1, "intervals": []},
            "tokens": {"coding_tokens_lower": lower, "coding_tokens_upper": lower + 1},
            "execution_windows": [],
            "connection_retry_events": [{}] if group == "plain" else [],
        }

    monkeypatch.setattr(report, "collect", costs)
    monkeypatch.setattr(report, "training_diagnostics", lambda *args: {})
    monkeypatch.setattr(report, "plot", lambda *args: None)
    result = report.summarize(tmp_path)
    assert result["status"] == "evaluated_review_pending"
    assert result["accuracy"]["plain"]["final"]["accuracy"]["mean_field_relative_l2"] == 0.5
    assert result["accuracy"]["plain"]["posthoc_best_round"] == 5
    assert result["framework_efficiency_ranking"]["coding_tokens"] is None


def test_equal_field_weight_fp64_and_identity():
    target = np.ones((40, 6, 2, 2)) * np.array([1, 2, 3, 4, 1e20, 6])[None, :, None, None]
    predicted = target * np.array([1.1, 1.2, 1.3, 1.4, 1.5, 1.6])[None, :, None, None]
    rows = [{"id": "one", "start": s} | field_errors(predicted, target) for s in (0, 80, 161)]
    result = aggregate(rows, ["one"])
    assert result["mean_field_relative_l2"] == pytest.approx(0.35)
    assert result["per_field_relative_l2"]["rho"] == pytest.approx(0.5)
    with pytest.raises(ValueError, match="缺失"):
        aggregate(rows[:-1], ["one"])
    with pytest.raises(ValueError, match="重复"):
        aggregate(rows + rows[:1], ["one"])


def test_evaluation_clock_not_overwritten_by_window_start(tmp_path, monkeypatch):
    import h5py

    from tools.verification.dojo_validity.rmhd import evaluate
    from tools.verification.dojo_validity.rmhd.protocol import FIELDS

    source = tmp_path / "source.h5"
    with h5py.File(source, "w") as stream:
        for field in FIELDS:
            stream[field] = np.broadcast_to(np.arange(1, 212)[:, None, None], (211, 2, 2))

    class FakeResident:
        def __init__(self, *args):
            pass

        def predict(self, history):
            return np.repeat(history[:, -1:], 40, axis=1), 0.049

        def close(self):
            pass

    monkeypatch.setattr(evaluate, "Resident", FakeResident)
    times = iter([1000.0, 1002.0])
    monkeypatch.setattr(evaluate.time, "monotonic", lambda: next(times))
    output = tmp_path / "evaluation"
    result = evaluate.evaluate_candidate(
        None, None, None, [{"path": str(source), "id": "one"}], output
    )
    assert result["eligible"]
    assert (
        result["accuracy"]["mean_field_relative_l2"]
        == result["persistence"]["mean_field_relative_l2"]
    )
    assert set(result["per_field_improvement_over_persistence"].values()) == {0.0}
    assert read_json(output / "execution.json") == {
        "start": 1000.0,
        "end": 1002.0,
        "source": "controller clock including inference and FP64 scoring",
    }


@pytest.mark.parametrize("bad", ["zero", "nan", "shape"])
def test_bad_prediction_never_drops_samples(bad):
    target = np.ones((40, 6, 2, 2))
    predicted = target.copy()
    if bad == "zero":
        target[:, 2] = 0
    elif bad == "nan":
        predicted[0, 0, 0, 0] = np.nan
    else:
        predicted = predicted[:-1]
    with pytest.raises(ValueError):
        field_errors(predicted, target)


def test_complete_baseline_gate_and_missing_fields():
    assert not gate({})["passed"]
    record = {
        "epochs": 500,
        "device": "mps",
        "training_seconds": 600,
        "latency_p95_seconds": 0.01,
        "validation": {
            "mean_field_relative_l2": 0.2,
            "per_field_relative_l2": {"rho": 0.2, "T": 0.2},
        },
        "persistence": {
            "mean_field_relative_l2": 0.4,
            "per_field_relative_l2": {"rho": 0.4, "T": 0.4},
        },
    }
    assert gate(record)["passed"]
    for key, value in (
        ("epochs", 5),
        ("training_seconds", 1800),
        ("latency_p95_seconds", 0.05001),
        ("device", "cpu"),
    ):
        assert not gate(record | {key: value})["passed"]


def test_five_round_pair_never_calls_hidden_until_both_final(tmp_path):
    write_json(tmp_path / "state.json", {"phase": "ready"})
    write_json(
        tmp_path / "comparison-protocol.json",
        {"experiments": {g: str(tmp_path / g) for g in ("plain", "dojo")}},
    )
    calls, hidden = [], []

    class Driver:
        def verify_startup(self, config):
            calls.append("startup")

        def round(self, group, number, location):
            calls.append((group, number))
            with pytest.raises(ValueError, match="禁止隐藏"):
                evaluate_hidden(tmp_path, lambda *a: hidden.append(a))
            return candidate(Path(location) / f"round-{number}/submission", number)

        def select_final(self, group, location):
            assert not hidden
            return {"round": 3, "validation_reason": "best validation"}

    run_pair(tmp_path, Driver())
    assert calls[:3] == ["startup", ("plain", 0), ("dojo", 0)]
    assert calls[3:5] == [("dojo", 1), ("plain", 1)]
    assert len(calls) == 13 and not hidden
    assert read_json(tmp_path / "state.json")["phase"] == "both_finals_locked"

    def evaluator(group, number, source, output):
        hidden.append((group, number))
        assert source.is_relative_to(tmp_path / "frozen")
        assert output.is_relative_to(tmp_path / "hidden-results")
        return {"status": "evaluated", "test_secret": "only controller"}

    evaluate_hidden(tmp_path, evaluator)
    assert len(hidden) == 12
    for group in ("plain", "dojo"):
        assert not list((tmp_path / group).rglob("result.json"))
        with pytest.raises(ValueError, match="关闭"):
            lock_final(tmp_path, group, {"round": 5})


def test_frozen_content_and_links_rejected(tmp_path):
    write_json(tmp_path / "state.json", {"phase": "running"})
    source = candidate(tmp_path / "source", 0)
    freeze_round(tmp_path, "plain", 0, source)
    frozen = verify_frozen(tmp_path, "plain", 0)
    path = frozen / "predict.py"
    path.chmod(0o644)
    path.write_text("mutated")
    with pytest.raises(ValueError, match="变化"):
        verify_frozen(tmp_path, "plain", 0)
    (source / "link").symlink_to(tmp_path / "secret")
    with pytest.raises(ValueError, match="软链接"):
        freeze_round(tmp_path, "dojo", 0, source)


def test_clean_env_and_round_zero_instruction(tmp_path, monkeypatch):
    monkeypatch.setenv("UNRELATED_SECRET", "do-not-inherit")
    env = clean_environment(tmp_path)
    assert "UNRELATED_SECRET" not in env
    assert env["HOME"].startswith(str(tmp_path))
    p = {
        "group": "plain",
        "experiment_root": str(tmp_path),
        "session_workspace_root": str(tmp_path.parent),
        "python_executable": "/runtime/python",
    }
    text = prompt(p, 0)
    assert "自行编写" in text and "Dojo" not in text and "已经完成共同 baseline" not in text
    assert "DOJO_AGENT_GUIDE.md" in prompt(p | {"group": "dojo"}, 0)


def test_public_proxy_rejects_private_and_dns_rebinding(monkeypatch, tmp_path):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))],
    )
    with pytest.raises(ValueError, match="公网"):
        public_addresses("public-name.example", 80)
    monkeypatch.undo()
    with (
        PublicProxy(tmp_path / "network.jsonl") as proxy,
        socket.create_connection(("127.0.0.1", proxy.port)) as connection,
    ):
        connection.sendall(b"CONNECT 127.0.0.1:8000 HTTP/1.1\r\nHost: localhost\r\n\r\n")
        assert b"403" in connection.recv(1024)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS真实边界")
def test_whole_process_and_shared_readonly(tmp_path):
    own, shared = tmp_path / "own", tmp_path / "shared"
    own.mkdir()
    shared.mkdir()
    secret = tmp_path / "secret"
    secret.write_text("hidden")
    (shared / "public").write_text("public")
    (own / "link").symlink_to(secret)
    body = policy([own], [shared])
    assert "/opt/homebrew/lib" not in body
    assert "(allow network-outbound" not in body
    assert execute(body, ["/bin/cat", shared / "public"], own).returncode == 0
    for args in (
        ["/bin/cat", secret],
        ["/bin/cat", own / "link"],
        ["/bin/ls", tmp_path],
        ["/usr/bin/touch", shared / "new"],
        ["/bin/rm", shared / "public"],
        ["/bin/sh", "-c", 'cat "$1"', "probe", secret],
    ):
        assert execute(body, args, own).returncode != 0


def test_schedule_exact_order():
    assert len(schedule_digest()) == 64
    assert schedule_digest() == schedule_digest()


def test_environment_cannot_smuggle_private_files(tmp_path):
    from tools.verification.dojo_validity.rmhd.controller import freeze_environment

    env = tmp_path / "env"
    env.mkdir()
    truth = tmp_path / "truth.npy"
    truth.write_text("private")
    (env / "innocent-package.py").symlink_to(truth)
    with pytest.raises(ValueError, match="链接越界"):
        freeze_environment(env, tmp_path / "frozen", [])
    assert not (tmp_path / "frozen").exists()


def test_rmhd_usage_bounds_missing_and_no_cache_double_count():
    from tools.verification.dojo_validity.rmhd.accounting import response_phase, usage_summary

    coding = {
        "request_id": "a",
        "phase": "coding",
        "input_tokens": 100,
        "output_tokens": 10,
        "cache_read_tokens": 80,
        "cache_write_tokens": None,
    }
    mixed = coding | {"request_id": "b", "phase": "mixed", "input_tokens": 20}
    summary = usage_summary([coding, mixed, coding])
    assert summary["total_accounted_tokens"] == 140
    assert (summary["coding_tokens_lower"], summary["coding_tokens_upper"]) == (110, 140)
    assert usage_summary([coding | {"output_tokens": None}])["total_accounted_tokens"] is None
    assert (
        response_phase({"input": "activity.py data_preparation -- read.py"}) == "data_preparation"
    )


def test_hidden_gate_requires_both_final_files(tmp_path):
    write_json(tmp_path / "state.json", {"phase": "both_finals_locked"})
    with pytest.raises(FileNotFoundError):
        evaluate_hidden(tmp_path, lambda *args: pytest.fail("must not call hidden evaluator"))
