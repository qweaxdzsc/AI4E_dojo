"""从真实会话事件重建请求分类和活动区间，保留分类依据与未知项。"""

import ast
import json
import re
from datetime import datetime
from pathlib import Path

from .formal import rollout_path
from .io import read_json, write_json
from .ledger import summarize_time, summarize_usage


def call_phase(payload):
    """按实际工具调用内容分类；混合活动不能归入单一阶段。"""
    body = str(payload.get("input", payload.get("arguments", "")))
    phases = set()
    if "apply_patch" in body or payload.get("name") == "apply_patch":
        phases.add("coding")
    commands = re.findall(
        r'(?:"cmd"|\'cmd\'|\bcmd)\s*:\s*("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`)',
        body,
    )
    for literal in commands:
        try:
            command = literal[1:-1] if literal.startswith("`") else ast.literal_eval(literal)
        except (ValueError, SyntaxError):
            phases.add("mixed")
            continue
        if re.search(r"\b(cat\s*>|tee\s|sed\s+-i)", command):
            phases.add("coding")
            continue
        found = re.findall(
            r"activity\.py\s+(training|evaluation|environment_setup|data_preparation|coding)",
            command,
        )
        phases.update(found or ["coding"])
    if not phases and "exec_command" not in body and "apply_patch" not in body:
        phases.update(
            re.findall(
                r"activity\.py\s+(training|evaluation|environment_setup|data_preparation|coding)",
                body,
            )
        )
    mapping = {"training": "training_observation", "data_preparation": "environment_setup"}
    phases = {mapping.get(p, p) for p in phases}
    if phases:
        return next(iter(phases)) if len(phases) == 1 else "mixed"
    if "write_stdin" in body or payload.get("name") in ("wait", "sleep"):
        return "training_observation"
    return "coding"


def timestamp(event):
    """读取带时区的原始供应商事件时刻。"""
    return datetime.fromisoformat(event["timestamp"]).timestamp()


def collect(protocol):
    """读取一个正式会话所有尝试，不删除失败，也不计准备期诊断会话。"""
    root = Path(protocol["experiment_root"])
    sid = read_json(root / "evidence/formal-initialization/session.json")["session_id"]
    raw = [json.loads(line) for line in rollout_path(protocol, sid).read_text().splitlines()]
    requests, calls, pending, classifications = [], {}, [], []
    # 一个响应的输出可能先含 commentary 再调用工具；usage 在该响应末记录。
    for event in raw:
        p = event["payload"]
        if event["type"] == "response_item" and p.get("type") in (
            "custom_tool_call",
            "function_call",
        ):
            phase = call_phase(p)
            calls[p["call_id"]] = (event, phase)
            pending.append(phase)
        if event["type"] == "token_usage_record":
            phases = set(pending) or {"coding"}
            phase = next(iter(phases)) if len(phases) == 1 else "mixed"
            u = p["usage"]
            requests.append(
                {
                    "request_id": p["response_id"],
                    "phase": phase,
                    "input_tokens": u["input_tokens"],
                    "output_tokens": u["output_tokens"],
                    "cache_read_tokens": u.get("cached_input_tokens"),
                    "cache_write_tokens": u.get("cache_write_input_tokens"),
                    "tool_calls": len(pending),
                    "retry_count": None,
                    "input_includes_cache": True,
                    "output_includes_reasoning": True,
                    "raw": p,
                    "timestamp": event["timestamp"],
                }
            )
            classifications.append(
                {
                    "request_id": p["response_id"],
                    "phase": phase,
                    "basis": "response tool actions; no tool => reasoning/analysis",
                    "tool_phases": pending.copy(),
                }
            )
            pending.clear()
    events, windows, turn_windows = [], [], []
    cli_token_total = 0
    cli_roots = [root / "evidence/formal-initialization", *root.glob("round-*/attempts/*/cli")]
    cli_roots = sorted(
        (p for p in cli_roots if (p / "process.json").exists()),
        key=lambda p: read_json(p / "process.json")["started"],
    )
    used_prompts = set()
    for folder in cli_roots:
        if not (folder / "process.json").exists():
            continue
        process = read_json(folder / "process.json")
        windows.append((process["started"], process["ended"]))
        entries = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]
        for entry in entries:
            if entry["event"].get("type") == "turn.completed":
                total_usage = entry["event"]["usage"]
                cli_token_total += total_usage["input_tokens"] + total_usage["output_tokens"]
        turn_event = next((e for e in entries if e["event"].get("type") == "turn.started"), None)
        if not turn_event:
            continue
        # 根据 CLI turn.started 与该请求的原始 task_started 配对，不用训练耗时反推编码。
        prompt = (folder / "prompt.txt").read_text()
        start_index = next(
            (
                i
                for i, e in enumerate(raw)
                if e["type"] == "response_item"
                and i not in used_prompts
                and e["payload"].get("role") == "user"
                and any(c.get("text", "") == prompt for c in e["payload"].get("content", []))
            ),
            None,
        )
        if start_index is None:
            continue
        used_prompts.add(start_index)
        begin = next(
            (
                i
                for i in range(start_index, -1, -1)
                if raw[i]["type"] == "event_msg" and raw[i]["payload"].get("type") == "task_started"
            ),
            start_index,
        )
        end = next(
            (
                i + 1
                for i in range(start_index, len(raw))
                if raw[i]["type"] == "event_msg"
                and raw[i]["payload"].get("type") == "task_complete"
            ),
            len(raw),
        )
        round_match = re.search(r"/round-(\d+)/attempts/", str(folder))
        turn_windows.append(
            {
                "turn_id": raw[begin]["payload"].get("turn_id"),
                "round": int(round_match[1]) if round_match else None,
                "start": process["started"],
                "end": process["ended"],
                "source": str(folder.relative_to(root)),
            }
        )
        offset = turn_event["received"] - timestamp(raw[begin])
        cursor = turn_event["received"]
        open_calls = {}
        native_open, native_spans = {}, []
        for entry in entries:
            item = entry["event"].get("item", {})
            if item.get("type") not in ("command_execution", "file_change"):
                continue
            if entry["event"]["type"] == "item.started":
                native_open[item["id"]] = entry["received"]
            elif entry["event"]["type"] == "item.completed" and item["id"] in native_open:
                phases = set(
                    re.findall(
                        r"activity\.py\s+(training|evaluation|environment_setup|data_preparation)",
                        item.get("command", ""),
                    )
                )
                phase = (
                    next(iter(phases))
                    if len(phases) == 1
                    else ("idle_or_wait" if phases else "coding")
                )
                native_spans.append(
                    (native_open.pop(item["id"]), entry["received"], phase, item["id"])
                )

        def add(a, b, phase, source, process=process, folder=folder):
            a, b = max(process["started"], a), min(process["ended"], b)
            if folder.name == "formal-initialization" and phase == "coding":
                phase = "environment_setup"
            if b > a:
                events.append(
                    {
                        "event_id": f"{folder.name}:{len(events)}",
                        "phase": phase,
                        "start": a,
                        "end": b,
                        "source": source,
                    }
                )

        add(process["started"], cursor, "environment_setup", "CLI launch and state resume")
        for e in raw[begin:end]:
            p = e["payload"]
            when = timestamp(e) + offset
            if e["type"] == "response_item" and p.get("type") in (
                "custom_tool_call",
                "function_call",
            ):
                phase = call_phase(p)
                add(
                    cursor,
                    when,
                    "idle_or_wait" if phase == "training_observation" else "coding",
                    "model response generation before " + p["call_id"],
                )
                open_calls[p["call_id"]] = (when, phase)
                cursor = max(cursor, when)
            elif e["type"] == "response_item" and p.get("type") in (
                "custom_tool_call_output",
                "function_call_output",
            ):
                if p.get("call_id") in open_calls:
                    start, phase = open_calls.pop(p["call_id"])
                    body = str(calls[p["call_id"]][0]["payload"])
                    time_phase = {
                        "training_observation": "training",
                        "evaluation": "evaluation",
                        "environment_setup": "environment_setup",
                    }.get(phase, "coding")
                    if (
                        "write_stdin" in body
                        or "activity.py" not in body
                        and phase == "training_observation"
                    ):
                        time_phase = "idle_or_wait"
                    if any(a < when + 0.05 and b > start - 0.05 for a, b, _, _ in native_spans):
                        # 原始 tool 调用可同时修改代码并等待训练。使用 CLI 子工具的
                        # 真实区间，不能将整个混合调用都计入编码。
                        time_phase = "idle_or_wait"
                    add(start, when, time_phase, "tool " + p["call_id"])
                    cursor = max(cursor, when)
            elif e["type"] == "event_msg" and p.get("type") == "task_complete":
                add(cursor, when, "coding", "model analysis and final response")
                cursor = max(cursor, when)
        add(cursor, process["ended"], "idle_or_wait", "CLI finalization")
        for a, b, phase, item_id in native_spans:
            add(a, b, phase, "CLI native item " + item_id)
    for path in root.glob("evidence/activities/*/completed.json"):
        activity = read_json(path)
        events.append(
            {
                **activity,
                "event_id": "process:" + activity["event_id"],
                "source": str(path.relative_to(root)),
            }
        )
    for path in root.glob("evidence/evaluations/*/execution.json"):
        event = read_json(path)
        end = event["end"]
        completion_source = "process monotonic clock including FP64 evaluation"
        metrics_path = path.with_name("metrics.json")
        if not event.get("includes_fp64_evaluation") and metrics_path.exists():
            # 早期 adapter 在推理后写 execution，随后写 metrics；用两个实际文件
            # 完成时刻补齐该段，来源显式保留，不把差额归入编码。
            end += max(0.0, metrics_path.stat().st_mtime - path.stat().st_mtime)
            completion_source = (
                "inference monotonic end plus observed metrics/execution file completion delta"
            )
        events.append(
            {
                "event_id": str(path.relative_to(root)),
                "phase": "evaluation",
                "start": event["start"],
                "end": end,
                "source": "independent frozen inference and FP64 evaluation",
                "completion_source": completion_source,
            }
        )
        windows.append((event["start"], end))
        round_match = re.search(r"/round-(\d+)/attempts/", " ".join(event.get("command", [])))
        turn_windows.append(
            {
                "round": int(round_match[1]) if round_match else None,
                "start": event["start"],
                "end": end,
                "source": str(path.relative_to(root)),
            }
        )
    if not windows:
        raise ValueError("无正式执行窗口")
    windows.sort()
    # CLI 调度以外主控实际等待的区间单列，不填入编码时间。
    last = windows[0][1]
    for start, stop in windows[1:]:
        if start > last:
            events.append(
                {
                    "event_id": f"scheduler:{len(events)}",
                    "phase": "idle_or_wait",
                    "start": last,
                    "end": start,
                    "source": "between recorded CLI/evaluator processes",
                }
            )
        last = max(last, stop)
    # 正在运行的 CLI 不能封账；这里只产出已完成窗口的临时统计。
    active_cli = any(not (p / "process.json").exists() for p in root.glob("round-*/attempts/*/cli"))
    unfinished_activities = [
        str(p.parent.relative_to(root))
        for p in root.glob("evidence/activities/*/started.json")
        if not p.with_name("completed.json").exists()
    ]
    events = [e for e in events if windows[0][0] <= e["start"] <= e["end"] <= last]
    time_result = summarize_time(events, windows[0][0], last)
    time_result["training_process_seconds"] = sum(
        e["end"] - e["start"]
        for e in events
        if e["phase"] == "training" and e["event_id"].startswith("process:")
    )
    initialization_turns = {
        w.get("turn_id")
        for w in turn_windows
        if w.get("source") == "evidence/formal-initialization" and w.get("turn_id")
    }
    initialization_requests = set()
    for request in requests:
        if request["raw"].get("turn_id") in initialization_turns:
            request["phase"] = "environment_setup"
            initialization_requests.add(request["request_id"])
    for item in classifications:
        if item["request_id"] in initialization_requests:
            item.update(phase="environment_setup", basis="formal initialization environment check")
    tokens = summarize_usage(requests)
    usage_reconciled = bool(requests) and tokens["total_accounted_tokens"] == cli_token_total
    result = {
        "time": time_result,
        "tokens": tokens,
        "usage_reconciled": usage_reconciled,
        "cli_completed_turn_tokens": cli_token_total,
        "execution_windows": turn_windows,
        "classification": classifications,
        "measurement_complete": not active_cli
        and not unfinished_activities
        and usage_reconciled
        and time_result["unaccounted_seconds"] < 1e-3,
        "provisional": active_cli,
        "unfinished_activities": unfinished_activities,
        "limitations": [
            "request classification is action based; mixed requests remain separate",
            "provider retry count is unavailable; raw CLI retry errors are retained",
        ],
        "failed_attempts": len(list(root.glob("round-*/attempts/*/failure.json"))),
    }
    write_json(root / "results/cost-audit.json", result)
    return result
