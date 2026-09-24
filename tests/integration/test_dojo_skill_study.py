"""单组 Skill 研究的权限来源、逐轮审查与隐藏评价门禁。"""

import pytest

from tools.verification.dojo_validity.io import digest, write_json
from tools.verification.dojo_validity.rmhd.skill_study import (
    StudyDriver,
    deliver,
    hidden,
    run_round,
)


def test_private_authority_and_protocol_tamper(tmp_path):
    root = tmp_path / "controller"
    workspace = tmp_path / "group"
    experiment = workspace / "experiment-a"
    write_json(experiment / "protocol.json", {"model": "untrusted", "experiment_root": "/tmp"})
    write_json(
        root / "comparison-protocol.json",
        {
            "experiments": {"dojo": str(experiment)},
            "workspace_root": str(workspace),
            "model": "trusted-model",
            "reasoning": "high",
            "runtime_readonly_roots": ["/usr"],
        },
    )
    write_json(
        root / "evidence/dojo-initial-materials.json",
        {
            "protocol.json": digest(experiment / "protocol.json"),
        },
    )
    result = StudyDriver(root).trusted_protocol("dojo", experiment)
    assert result["model"] == "trusted-model"
    assert result["experiment_root"] == str(experiment)
    assert result["session_workspace_root"] == str(workspace)
    with pytest.raises(ValueError):
        StudyDriver(root).trusted_protocol("plain", experiment)
    write_json(experiment / "protocol.json", {"model": "changed"})
    with pytest.raises(ValueError, match="协议"):
        StudyDriver(root).trusted_protocol("dojo", experiment)


@pytest.mark.parametrize("phase", ["ready", "running", "materials_prepared_isolation_pending"])
def test_hidden_cannot_run_before_single_final_lock(tmp_path, phase):
    write_json(tmp_path / "state.json", {"phase": phase})
    with pytest.raises(ValueError, match="冻结"):
        hidden(tmp_path)
    assert not (tmp_path / "hidden-results").exists()


def test_final_locked_cannot_resume_research(tmp_path):
    write_json(tmp_path / "state.json", {"phase": "single_final_locked"})
    with pytest.raises(ValueError):
        run_round(tmp_path, 5)


def test_skill_revision_requires_previous_frozen_and_review(tmp_path):
    write_json(tmp_path / "state.json", {"phase": "running"})
    write_json(
        tmp_path / "comparison-protocol.json", {"experiments": {"dojo": str(tmp_path / "group")}}
    )
    with pytest.raises(FileNotFoundError):
        deliver(tmp_path, 1, "不能跳过上一轮审查")
    assert not (tmp_path / "skill-revisions").exists()


def test_no_midround_skill_replacement(tmp_path):
    write_json(tmp_path / "active-round.json", {"round": 1})
    with pytest.raises(ValueError, match="正在执行"):
        deliver(tmp_path, 1, "不允许轮中指导")


def test_utilization_has_stable_denominator_and_requires_real_evidence():
    from tools.verification.dojo_validity.rmhd.skill_review import summarize_review
    from tools.verification.dojo_validity.rmhd.skill_study import OPPORTUNITIES

    rows = {k: {"availability": "direct", "choice": "custom"} for k in OPPORTUNITIES}
    rows["training_loop"].update(choice="adapted", evidence=["executed train_model call"])
    rows["objective"].update(choice="justified_custom", reason="scientific custom objective")
    review = {
        "opportunities": rows,
        "decisions": [
            {"dojo_evidence": ["read training help"], "web_evidence": ["read official docs"]},
            {"dojo_evidence": ["read evaluation help"], "web_evidence": []},
        ],
    }
    result = summarize_review(review)
    assert result["known_applicable"] == 13  # 有理由自写也不从可用能力分母删除
    assert result["utilization_known"] == 1 / 13
    assert result["dual_reference_coverage"] == 0.5
    rows["training_loop"]["evidence"] = []
    with pytest.raises(ValueError, match="证据"):
        summarize_review(review)


def test_public_proxy_does_not_close_quiet_model_stream(tmp_path, monkeypatch):
    """模拟暂时静默后有数据的隧道，不等待一分钟也能验证误切断回归。"""
    import socket
    import threading

    from tools.verification.dojo_validity.rmhd import network

    upstream = socket.socket()
    upstream.bind(("127.0.0.1", 0))
    upstream.listen(1)
    monkeypatch.setattr(
        network,
        "public_addresses",
        lambda *_: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", upstream.getsockname())],
    )
    original = network.select.select
    calls = []

    def quiet_once(*args):
        calls.append(1)
        return ([], [], []) if len(calls) == 1 else original(*args)

    monkeypatch.setattr(network.select, "select", quiet_once)

    def echo():
        conn, _ = upstream.accept()
        with conn:
            data = conn.recv(4)
            conn.sendall(data)

    thread = threading.Thread(target=echo)
    thread.start()
    try:
        with (
            network.PublicProxy(tmp_path / "network.jsonl") as proxy,
            socket.create_connection(("127.0.0.1", proxy.port), timeout=3) as client,
        ):
            client.sendall(b"CONNECT public.example:443 HTTP/1.1\r\nHost: public.example\r\n\r\n")
            header = b""
            while not header.endswith(b"\r\n\r\n"):
                header += client.recv(1)
            assert b"200" in header
            client.sendall(b"ping")
            assert client.recv(4) == b"ping"
    finally:
        upstream.close()
        thread.join(timeout=3)


def test_fake_single_study_six_freezes_before_hidden(tmp_path, monkeypatch):
    """完整单组状态机：六轮冻结之前零隐藏执行，之后不能再优化或替换选择。"""
    from tools.verification.dojo_validity.io import read_json
    from tools.verification.dojo_validity.rmhd import skill_study as study

    root, workspace = tmp_path / "controller", tmp_path / "group"
    experiment = workspace / "experiment-fake"
    config = {
        "experiments": {"dojo": str(experiment)},
        "workspace_root": str(workspace),
        "model": "fake",
        "reasoning": "high",
        "runtime_readonly_roots": [],
    }
    write_json(root / "comparison-protocol.json", config)
    write_json(experiment / "protocol.json", {"group": "dojo", "python_executable": "/unused"})
    write_json(
        root / "evidence/dojo-initial-materials.json",
        {"protocol.json": digest(experiment / "protocol.json")},
    )
    write_json(root / "evidence/dojo-isolation.json", {"passed": True})
    write_json(root / "state.json", {"phase": "ready"})
    skill = experiment / "dojo-resources" / study.SKILL
    skill.parent.mkdir(parents=True)
    skill.write_text("fake skill")
    called, evaluated = [], []

    def fake_call(self, group, location, name, message):
        number = int(name.removeprefix("round-"))
        called.append(number)
        target = experiment / name / "submission"
        target.mkdir(parents=True)
        for key in ("entrypoint", "checkpoint", "statistics"):
            (target / key).write_text("fake data")
        write_json(
            target / "submission.json",
            {
                "interface": "rmhd-predict-v1",
                "round": number,
                "entrypoint": "entrypoint",
                "checkpoint": "checkpoint",
                "statistics": "statistics",
                "method": "fake unit test",
                "dojo_usage": [],
            },
        )

    monkeypatch.setattr(study.StudyDriver, "call", fake_call)
    monkeypatch.setattr(
        study.StudyDriver,
        "check_round",
        lambda self, g, n, loc, p: experiment / f"round-{n:02d}/submission",
    )
    monkeypatch.setattr(
        study.StudyDriver, "select_final", lambda *_: {"round": 2, "validation_reason": "fake"}
    )
    monkeypatch.setattr(study, "freeze_environment", lambda s, d, r: d.mkdir(parents=True))
    monkeypatch.setattr(
        study,
        "evaluate_candidate",
        lambda *args: evaluated.append(args[0].name) or {"status": "evaluated"},
    )
    for number in range(6):
        write_json(root / f"skill-revisions/round-{number:02d}.json", {"sha256": digest(skill)})
        with pytest.raises(ValueError):
            study.hidden(root)
        study.run_round(root, number)
        write_json(root / f"reviews/round-{number:02d}.json", {"reviewed": True})
    assert called == list(range(6)) and evaluated == []
    study.select(root)
    assert read_json(root / "state.json")["phase"] == "single_final_locked"
    write_json(root / "private-split.json", {"splits": {"test": []}})
    study.hidden(root)
    assert evaluated == [f"round-{n:02d}" for n in range(6)]
    assert not (experiment / "hidden-results").exists()
    with pytest.raises(ValueError):
        study.run_round(root, 5)


def test_internal_validation_clock_is_supplementary_and_bounded(tmp_path):
    import json

    from tools.verification.dojo_validity.rmhd.skill_report import internal_evaluation

    target = tmp_path / "frozen/dojo/round-01/training-logs/a-validation-events.jsonl"
    target.parent.mkdir(parents=True)
    records = [
        {"event": "start", "updates": 5, "variant": "raw", "monotonic": 12},
        {"event": "end", "updates": 5, "variant": "raw", "monotonic": 15},
        {"event": "start", "updates": 10, "variant": "raw", "monotonic": 30},
        {"event": "end", "updates": 10, "variant": "raw", "monotonic": 35},
    ]
    target.write_text("\n".join(map(json.dumps, records)))
    result = internal_evaluation(
        tmp_path, [{"phase": "training", "round": 1, "start": 10, "end": 20}]
    )
    assert result["seconds"] == 3
    assert result["independently_instrumented"] is False
    assert any(g["reason"] == "not enclosed by observed training" for g in result["gaps"])
    assert any(g["round"] == 0 for g in result["gaps"])
    target.write_text(json.dumps(records[1]))
    with pytest.raises(ValueError, match="缺少开始"):
        internal_evaluation(tmp_path, [])


def test_skill_report_requires_completed_hidden_evaluation(tmp_path):
    from tools.verification.dojo_validity.rmhd.skill_report import report

    write_json(tmp_path / "state.json", {"phase": "running"})
    with pytest.raises(ValueError, match="隐藏评价"):
        report(tmp_path)
    assert not (tmp_path / "results").exists()
