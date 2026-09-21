"""正式 CLI 的权限包装、干净启动、续接与逐请求证据验证。"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from tools.verification.dojo_validity.cli import command, seatbelt, toml
from tools.verification.dojo_validity.formal import delivery_prompt, usage_records


def protocol(tmp_path):
    """使用独立测试根，不读取真实认证。"""
    root = tmp_path / "neumann-plain"
    experiment = root / "experiment-test"
    experiment.mkdir(parents=True)
    return {
        "session_workspace_root": str(root),
        "experiment_root": str(experiment),
        "experiment_id": experiment.name,
        "model": "same-model",
        "reasoning": "high",
    }


def test_cli_is_wrapped_and_resume_keeps_root(tmp_path, monkeypatch):
    p = protocol(tmp_path)
    home = tmp_path / "host"
    (home / ".codex").mkdir(parents=True)
    (home / ".codex/config.toml").write_text('model="host-model"\n')
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    args = command(p, tmp_path / "answer", "session-123")
    assert args[:2] == ["/usr/bin/sandbox-exec", "-p"]
    assert args[args.index("-C") + 1] == p["session_workspace_root"]
    assert args[args.index("resume") + 1] == "session-123"
    assert "--ignore-rules" in args and "--ignore-user-config" in args
    assert "--dangerously-bypass-approvals-and-sandbox" in args
    assert "(deny default)" in args[2]
    assert '(remote ip "localhost:*")' in args[2]
    assert 'model="same-model"' in args
    for i, arg in enumerate(args):
        if arg == "-c":
            tomllib.loads(args[i + 1])


def test_toml_nested_and_paths_are_literal():
    value = [{"path": '/path with spaces/a"b', "enabled": False}]
    assert tomllib.loads("x=" + toml(value))["x"] == value


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS seatbelt 专项")
def test_whole_process_filesystem_boundary(tmp_path):
    p = protocol(tmp_path)
    own = Path(p["session_workspace_root"])
    forbidden = tmp_path / "outside"
    forbidden.write_text("test sentinel")
    link = own / "link"
    link.symlink_to(forbidden)

    def execute(*args):
        return subprocess.run(
            ["/usr/bin/sandbox-exec", "-p", seatbelt(p), *args],
            cwd=own,
            capture_output=True,
            text=True,
            check=False,
        )

    assert execute("/usr/bin/touch", str(own / "file")).returncode == 0
    for target in (str(forbidden), str(link)):
        result = execute("/bin/cat", target)
        assert result.returncode != 0 and "Operation not permitted" in result.stderr
    assert execute("/bin/ls", str(tmp_path)).returncode != 0
    assert execute("/usr/bin/touch", str(forbidden)).returncode != 0


def test_delivery_does_not_name_other_group(tmp_path):
    prompt = delivery_prompt(protocol(tmp_path), 1)
    assert "neumann-dojo" not in prompt and "Dojo" not in prompt
    assert "infer.py" in prompt and "activity.py" in prompt


def test_provider_usage_preserves_ids_and_cache(tmp_path):
    p = protocol(tmp_path)
    folder = Path(p["experiment_root"]) / "agent-state/sessions"
    folder.mkdir(parents=True)
    payload = {
        "response_id": "real-response",
        "usage": {"input_tokens": 100, "output_tokens": 12, "cached_input_tokens": 80},
    }
    row = {"type": "token_usage_record", "timestamp": "2026-09-20T00:00:00Z", "payload": payload}
    (folder / "rollout-session.jsonl").write_text(json.dumps(row) + "\n")
    target = tmp_path / "evidence"
    target.mkdir()
    records = usage_records(p, "session", target)
    assert records[0]["request_id"] == "real-response"
    assert records[0]["input_tokens"] == 100
    assert records[0]["cache_read_tokens"] == 80
    assert records[0]["cache_write_tokens"] is None
    assert records[0]["raw"] == payload
    assert (target / "rollout.jsonl").exists()


def test_request_activity_classification():
    from tools.verification.dojo_validity.telemetry import call_phase

    assert (
        call_phase(
            {"input": 'await tools.exec_command({cmd:"python activity.py training -- train.py"})'}
        )
        == "training_observation"
    )
    assert (
        call_phase(
            {"input": 'await tools.exec_command({cmd:"python activity.py evaluation -- infer.py"})'}
        )
        == "evaluation"
    )
    assert (
        call_phase({"input": "await tools.write_stdin({session_id:123})"}) == "training_observation"
    )
    assert call_phase({"input": 'await tools.apply_patch("research code")'}) == "coding"
    assert (
        call_phase({"input": "activity.py training -- a; activity.py evaluation -- b"}) == "mixed"
    )


@pytest.mark.parametrize("native_activity", [False, True])
def test_complete_request_and_time_ledger(tmp_path, native_activity):
    from tools.verification.dojo_validity.io import read_json, write_json
    from tools.verification.dojo_validity.telemetry import collect

    p = protocol(tmp_path)
    root = Path(p["experiment_root"])
    folder = root / "evidence/formal-initialization"
    folder.mkdir(parents=True)
    write_json(folder / "session.json", {"session_id": "real-session"})
    write_json(folder / "process.json", {"started": 0.0, "ended": 10.0})
    (folder / "prompt.txt").write_text("initialize")
    (folder / "events.jsonl").write_text(
        json.dumps({"received": 0.1, "event": {"type": "turn.started"}})
        + "\n"
        + json.dumps(
            {
                "received": 9.1,
                "event": {
                    "type": "turn.completed",
                    "usage": {"input_tokens": 220, "output_tokens": 30},
                },
            }
        )
        + "\n"
    )
    if native_activity:
        with (folder / "events.jsonl").open("a") as stream:
            for received, kind, item in [
                (1.2, "item.started", {"id": "edit", "type": "file_change"}),
                (1.4, "item.completed", {"id": "edit", "type": "file_change"}),
                (1.4, "item.started", {"id": "train", "type": "command_execution"}),
                (
                    3.0,
                    "item.completed",
                    {
                        "id": "train",
                        "type": "command_execution",
                        "command": "python activity.py training -- train.py",
                    },
                ),
            ]:
                stream.write(
                    json.dumps({"received": received, "event": {"type": kind, "item": item}}) + "\n"
                )
    raw = []

    def event(second, kind, payload):
        raw.append(
            {"timestamp": f"2026-09-20T00:00:{second:02d}Z", "type": kind, "payload": payload}
        )

    event(0, "event_msg", {"type": "task_started", "turn_id": "init"})
    event(
        0, "response_item", {"type": "message", "role": "user", "content": [{"text": "initialize"}]}
    )
    event(
        1,
        "response_item",
        {
            "type": "custom_tool_call",
            "call_id": "call1",
            "name": "exec",
            "input": "read local code",
        },
    )
    event(
        2,
        "token_usage_record",
        {
            "response_id": "request1",
            "turn_id": "init",
            "usage": {"input_tokens": 100, "output_tokens": 10},
        },
    )
    event(3, "response_item", {"type": "custom_tool_call_output", "call_id": "call1"})
    event(
        8,
        "token_usage_record",
        {
            "response_id": "request2",
            "turn_id": "init",
            "usage": {"input_tokens": 120, "output_tokens": 20},
        },
    )
    event(9, "event_msg", {"type": "task_complete"})
    transcripts = root / "agent-state/sessions"
    transcripts.mkdir(parents=True)
    (transcripts / "rollout-real-session.jsonl").write_text(
        "\n".join(json.dumps(e) for e in raw) + "\n"
    )
    result = collect(p)
    assert result["measurement_complete"]
    assert result["time"]["environment_setup_seconds"] == pytest.approx(
        7.3 if native_activity else 9.1
    )
    assert result["time"]["training_seconds"] == pytest.approx(1.6 if native_activity else 0.0)
    assert result["time"]["unaccounted_seconds"] == pytest.approx(0.0)
    assert result["tokens"]["environment_setup_tokens"] == 250
    assert result["tokens"]["request_count"] == 2
    assert read_json(root / "results/cost-audit.json")["tokens"]["total_accounted_tokens"] == 250


def test_writing_training_command_is_coding():
    from tools.verification.dojo_validity.telemetry import call_phase

    assert (
        call_phase(
            {"input": 'await tools.apply_patch("code mentioning activity.py training -- train")'}
        )
        == "coding"
    )
    assert (
        call_phase(
            {
                "name": "exec_command",
                "arguments": json.dumps({"cmd": "python activity.py training -- train.py"}),
            }
        )
        == "training_observation"
    )
    assert (
        call_phase(
            {
                "input": 'await tools.apply_patch("code"); await tools.exec_command({"cmd":"python activity.py training -- train.py"})'
            }
        )
        == "mixed"
    )


def test_cli_template_commands_keep_activity_phase():
    from tools.verification.dojo_validity.telemetry import call_phase

    assert (
        call_phase(
            {
                "name": "exec",
                "input": 'const e=load("e"); text(await tools.exec_command({cmd:`${py} ${e}/activity.py evaluation -- ${py} infer.py`}));',
            }
        )
        == "evaluation"
    )
    assert (
        call_phase(
            {
                "name": "exec",
                "input": 'await tools.apply_patch("new source"); await tools.exec_command({cmd:`${py} ${e}/activity.py evaluation -- ${py} infer.py`});',
            }
        )
        == "mixed"
    )


def test_serial_queue_counts_only_observed_overlap():
    from tools.verification.dojo_validity.finish import measure_queue

    costs = {
        "plain": {
            "time": {"intervals": []},
            "execution_windows": [{"start": 2, "end": 8}, {"start": 7, "end": 9}],
        },
        "dojo": {
            "time": {
                "intervals": [
                    {
                        "start": 1,
                        "end": 10,
                        "source": "between recorded CLI/evaluator processes",
                    }
                ]
            },
            "execution_windows": [{"start": 10, "end": 12}],
        },
    }
    measure_queue(costs)
    assert costs["plain"]["time"]["executor_queue_seconds"] == 0
    assert costs["dojo"]["time"]["executor_queue_seconds"] == 7
    assert costs["dojo"]["time"]["orchestration_wait_seconds"] == 9
