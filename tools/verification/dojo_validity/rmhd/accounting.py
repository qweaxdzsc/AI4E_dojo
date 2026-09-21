"""主控原始流成本账本：按请求去重，未知活动留空，不用总时长倒推编码。"""

import json
import re
from datetime import datetime
from pathlib import Path

from ..io import read_json
from ..ledger import summarize_time
from ..telemetry import call_phase

PHASES = (
    "coding",
    "training_observation",
    "evaluation",
    "environment_setup",
    "data_preparation",
    "mixed",
    "unclassified",
)


def activity(command):
    """显式阶段命令归类；混合脚本/长进程未经可信观察不可默认为编码。"""
    found = set(
        re.findall(
            r"activity\.py\s+(coding|training|evaluation|environment_setup|data_preparation)",
            command,
        )
    )
    if len(found) == 1:
        return found.pop()
    if len(found) > 1:
        return "mixed"
    if any(token in command for token in ("apply_patch", "cat ", "sed -n", "rg ", "read_text")):
        return "coding"
    return "unclassified"


def response_phase(payload):
    """按当前请求实际工具分类；数据准备不混入环境，纯分析/文档阅读属于编码。"""
    body = str(payload.get("input", payload.get("arguments", "")))
    if "activity.py data_preparation" in body:
        others = re.findall(r"activity\.py\s+(training|evaluation|environment_setup|coding)", body)
        return "mixed" if others else "data_preparation"
    return call_phase(payload)


def raw_intervals(directory, process, native):
    """用原始 turn/tool 时刻划出生成、工具和等待区间，不用训练时间作减法。"""
    raw = [
        json.loads(line)
        for p in (directory / "raw-rollouts").glob("*.jsonl")
        for line in p.read_text().splitlines()
        if line.strip()
    ]
    prompt_text = (directory / "prompt.txt").read_text()
    positions = [
        i
        for i, e in enumerate(raw)
        if e.get("type") == "response_item"
        and e.get("payload", {}).get("role") == "user"
        and any(c.get("text") == prompt_text for c in e["payload"].get("content", []))
    ]
    if not positions:
        return []
    index = positions[-1]
    begin = next(
        (
            i
            for i in range(index, -1, -1)
            if raw[i].get("payload", {}).get("type") == "task_started"
        ),
        index,
    )
    end = next(
        (
            i + 1
            for i in range(index, len(raw))
            if raw[i].get("payload", {}).get("type") == "task_complete"
        ),
        len(raw),
    )
    streamed = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
    turn = next(
        (r["received"] for r in streamed if r["event"].get("type") == "turn.started"),
        process["started"],
    )
    offset = turn - datetime.fromisoformat(raw[begin]["timestamp"]).timestamp()
    result, opened = [], {}
    cursor = turn

    def add(start, stop, phase, source):
        start, stop = max(process["started"], start), min(process["ended"], stop)
        if stop > start:
            result.append(
                {
                    "event_id": f"{directory.name}:raw:{len(result)}",
                    "phase": phase,
                    "start": start,
                    "end": stop,
                    "source": source,
                }
            )

    add(process["started"], turn, "environment_setup", "CLI start/resume")
    for record in raw[begin:end]:
        payload = record.get("payload", {})
        when = datetime.fromisoformat(record["timestamp"]).timestamp() + offset
        kind = payload.get("type")
        if record.get("type") == "response_item" and kind in {"function_call", "custom_tool_call"}:
            phase = response_phase(payload)
            add(
                cursor,
                when,
                "idle_or_wait" if phase == "training_observation" else "coding",
                "model generation before tool",
            )
            opened[payload["call_id"]] = (when, phase, str(payload))
            cursor = max(cursor, when)
        elif (
            kind in {"function_call_output", "custom_tool_call_output"}
            and payload.get("call_id") in opened
        ):
            start, phase, body = opened.pop(payload["call_id"])
            phase = {"training_observation": "training", "mixed": "idle_or_wait"}.get(phase, phase)
            if "write_stdin" in body or any(
                n["start"] < when + 0.05 and n["end"] > start - 0.05 for n in native
            ):
                phase = "idle_or_wait"
            add(start, when, phase, "raw tool call/output")
            cursor = max(cursor, when)
        elif record.get("type") == "event_msg" and kind == "task_complete":
            add(cursor, when, "coding", "model analysis and final response")
            cursor = max(cursor, when)
    add(cursor, process["ended"], "idle_or_wait", "CLI finalization")
    return result


def usage_summary(rows):
    """只相加规范化 input+output；缓存已包含于输入，缺项不能填零。"""
    requests = {}
    for row in rows:
        key = row["request_id"]
        if key in requests and requests[key] != row:
            raise ValueError("重复请求 usage 或活动冲突")
        if row["phase"] not in PHASES:
            raise ValueError("未知请求活动")
        for name in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
            value = row.get(name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("非法 token 值")
        requests[key] = row
    rows = list(requests.values())

    def total(items):
        if any(r.get("input_tokens") is None or r.get("output_tokens") is None for r in items):
            return None
        return sum(r["input_tokens"] + r["output_tokens"] for r in items)

    result = {
        f"{phase}_tokens": total([r for r in rows if r["phase"] == phase]) for phase in PHASES
    }
    for field in (
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "tool_calls",
    ):
        result[field] = (
            sum(r[field] for r in rows)
            if rows and all(r.get(field) is not None for r in rows)
            else None
        )
    lower = result["coding_tokens"]
    uncertain = total([r for r in rows if r["phase"] in {"mixed", "unclassified"}])
    result.update(
        total_accounted_tokens=total(rows) if rows else None,
        request_count=len(rows),
        coding_tokens_lower=lower if rows else None,
        coding_tokens_upper=lower + uncertain
        if rows and lower is not None and uncertain is not None
        else None,
        raw_requests=rows,
        retry_count=None,
        missing_usage_requests=[
            r["request_id"]
            for r in rows
            if r.get("input_tokens") is None or r.get("output_tokens") is None
        ],
    )
    return result


def evaluation_interval(path, processes):
    """旧主控漏记区间时仅从主控文件时刻重建估计，并保留估计来源。"""
    execution = path.parent / "execution.json"
    if execution.exists():
        return read_json(execution), False
    # 以该次评价前最近一次CLI结束的墙钟/单调时钟对应关系转换。
    preceding = [p for p in processes if p.stat().st_mtime <= path.parent.stat().st_birthtime]
    if not preceding:
        raise ValueError("主控评价缺少可定位的时钟锚点")
    anchor = max(preceding, key=lambda p: p.stat().st_mtime)
    offset = read_json(anchor)["ended"] - anchor.stat().st_mtime
    return {
        "start": path.parent.stat().st_birthtime + offset,
        "end": path.stat().st_mtime + offset,
        "source": "estimated from controller directory birth/result write times, anchored to preceding CLI end",
        "clock_anchor": str(anchor),
        "exact_monotonic_interval_missing": True,
    }, True


def collect(comparison, group):
    """只读主控原始事件；区间来自 CLI 工具事件，agent 自报活动不作唯一依据。"""
    root = Path(comparison) / "evidence/sessions" / group
    intervals, windows, usages, errors, round_windows = [], [], [], [], []
    turn_usages = []
    retry_events, failed_tools = [], []
    processes = sorted(root.rglob("process.json"), key=lambda p: read_json(p)["started"])
    for process_path in processes:
        directory = process_path.parent
        round_match = re.fullmatch(r"round-(\d+)", directory.parent.name)
        round_number = int(round_match[1]) if round_match else None
        proc = read_json(process_path)
        windows.append((proc["started"], proc["ended"]))
        round_windows.append((proc["started"], proc["ended"], round_number))
        if proc["returncode"]:
            errors.append(str(directory))
        active, native = {}, []
        for line in (directory / "events.jsonl").read_text().splitlines():
            record = json.loads(line)
            event, when = record["event"], record["received"]
            if event.get("type") == "error" and "Reconnecting" in event.get("message", ""):
                retry_events.append(
                    {
                        "time": when,
                        "round": round_number,
                        "message": event["message"],
                        "source": str(directory),
                    }
                )
            if event.get("type") == "turn.completed":
                turn_usages.append(event.get("usage", {}))
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("exit_code") not in (None, 0):
                failed_tools.append(
                    {
                        "time": when,
                        "round": round_number,
                        "item_id": item.get("id"),
                        "exit_code": item["exit_code"],
                        "source": str(directory),
                    }
                )
            if event.get("type") == "item.started":
                active[item.get("id")] = when
            elif event.get("type") == "item.completed" and item.get("id") in active:
                start = active.pop(item["id"])
                phase = (
                    "coding"
                    if item.get("type") in {"file_change", "web_search", "reasoning"}
                    else activity(item.get("command", ""))
                )
                if phase in {"mixed", "unclassified"}:
                    phase = "coding" if phase == "unclassified" else "idle_or_wait"
                native.append(
                    {
                        "event_id": f"{directory.name}:{item['id']}",
                        "phase": phase,
                        "start": start,
                        "end": when,
                        "source": "controller CLI event stream",
                        "round": round_number,
                    }
                )
        intervals.extend(native)
        intervals.extend(
            e | {"round": round_number} for e in raw_intervals(directory, proc, native)
        )
        # 已复制的供应商请求 usage 是首选，CLI turn 总量仅作交叉核验，不能再相加。
        pending = []
        for path in sorted((directory / "raw-rollouts").glob("*.jsonl")):
            for line in path.read_text().splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = event.get("payload", {})
                if event.get("type") == "response_item" and payload.get("type") in {
                    "function_call",
                    "custom_tool_call",
                }:
                    pending.append(response_phase(payload))
                if event.get("type") == "token_usage_record":
                    usage = payload.get("usage", {})
                    kinds = set(pending)
                    # 无工具的请求可能是规划，也可能只是训练进度播报；不默认为编码。
                    phase = next(iter(kinds)) if len(kinds) == 1 else "mixed"
                    usages.append(
                        {
                            "request_id": payload["response_id"],
                            "phase": phase,
                            "input_tokens": usage.get("input_tokens"),
                            "output_tokens": usage.get("output_tokens"),
                            "cache_read_tokens": usage.get("cached_input_tokens"),
                            "cache_write_tokens": usage.get("cache_write_input_tokens"),
                            "raw": payload,
                            "round": round_number,
                            "tool_calls": len(pending),
                            "classification_basis": "observed tool actions"
                            if kinds
                            else "no observable tool actions; analysis versus progress observation unresolved",
                        }
                    )
                    pending.clear()
    if not windows:
        return {"status": "missing", "time": None, "tokens": None}
    # 组内阶段文件仅在冻结helper未改、且主控原始工具流证实相同阶段执行时采用。
    # 原始区间仍保留在主控副本，并标注证据来源；不只信agent给出的总秒数。
    from .audit import archive_group

    audit = archive_group(comparison, group)
    artifacts = Path(comparison) / "evidence/group-artifacts" / group
    controller_commands = "\n".join(p.read_text() for p in root.rglob("events.jsonl"))
    corroborated = []
    if audit["activity_helper_matches"]:
        for path in artifacts.glob("evidence/activities/*/completed.json"):
            row = read_json(path)
            if f"activity.py {row['phase']}" not in controller_commands:
                continue
            if not any(a <= row["start"] <= row["end"] <= b for a, b in windows):
                continue
            corroborated.append(
                {
                    "event_id": "activity:" + row["event_id"],
                    "phase": row["phase"],
                    "start": row["start"],
                    "end": row["end"],
                    "source": "unchanged phase helper corroborated by controller tool stream",
                    "pid": row.get("pid"),
                    "exit_code": row.get("exit_code"),
                    "round": next(
                        (n for a, b, n in round_windows if a <= row["start"] <= row["end"] <= b),
                        None,
                    ),
                }
            )
    intervals.extend(corroborated)
    # 顺序训练子过程中的评价不重复算训练；并行编码区间继续保留。
    evaluation_spans = [(r["start"], r["end"]) for r in corroborated if r["phase"] == "evaluation"]
    separated = []
    for row in intervals:
        pieces = [(row["start"], row["end"])]
        if row["phase"] == "training":
            for a, b in evaluation_spans:
                if not row["start"] <= a <= b <= row["end"]:
                    continue
                pieces = [
                    (x, y)
                    for start, stop in pieces
                    for x, y in ((start, min(stop, a)), (max(start, b), stop))
                    if y > x
                ]
        separated.extend(
            row | {"event_id": row["event_id"] + f":part-{i}", "start": a, "end": b}
            for i, (a, b) in enumerate(pieces)
        )
    intervals = separated
    # 每次续接原始 rollout 从头保存，完全相同请求只保留一份。
    dedup = {}
    for row in usages:
        if row["request_id"] in dedup and dedup[row["request_id"]]["raw"] != row["raw"]:
            raise ValueError("供应商原始usage冲突")
        dedup.setdefault(row["request_id"], row)
    estimates = []
    for split in ("validation", "hidden-results"):
        for evaluation in (Path(comparison) / split / group).rglob("result.json"):
            row, estimated = evaluation_interval(evaluation, processes)
            windows.append((row["start"], row["end"]))
            number = (
                int(evaluation.parent.parent.name.removeprefix("round-"))
                if split == "validation"
                else int(evaluation.parent.name.removeprefix("round-"))
            )
            intervals.append(
                row | {"event_id": str(evaluation), "phase": "evaluation", "round": number}
            )
            if estimated:
                estimates.append({"file": str(evaluation)} | row)
    ordered = sorted(windows)
    last = ordered[0][1]
    queue = 0.0
    for start, stop in ordered[1:]:
        if start > last:
            intervals.append(
                {
                    "event_id": f"scheduler:{len(intervals)}",
                    "phase": "idle_or_wait",
                    "start": last,
                    "end": start,
                    "source": "controller scheduling gap",
                }
            )
            queue += start - last
        last = max(last, stop)
    timing = summarize_time(intervals, ordered[0][0], last)
    timing["training_process_seconds"] = sum(
        e["end"] - e["start"]
        for e in intervals
        if e["phase"] == "training" and e["event_id"].startswith("activity:")
    )
    timing["orchestration_wait_seconds"] = queue
    tokens = usage_summary(dedup.values())
    tokens["retry_count_observed"] = len(retry_events)
    tokens["failed_request_usage_limit"] = (
        "Reconnect events have no provider request usage; total is accounted tokens, not a claim about unreported billing"
        if retry_events
        else None
    )
    cli_total = (
        sum(u["input_tokens"] + u["output_tokens"] for u in turn_usages)
        if turn_usages and all("input_tokens" in u and "output_tokens" in u for u in turn_usages)
        else None
    )
    reconciled = cli_total is not None and cli_total == tokens["total_accounted_tokens"]
    return {
        "status": "partial"
        if timing["unaccounted_seconds"] > 1e-6 or not dedup or not reconciled
        else "accounted_with_limits"
        if estimates or retry_events
        else "accounted",
        "time": timing,
        "tokens": tokens,
        "usage_reconciliation": {
            "cli_turn_total": cli_total,
            "request_total": tokens["total_accounted_tokens"],
            "matches": reconciled,
        },
        "failed_cli_attempts": errors,
        "connection_retry_events": retry_events,
        "failed_tool_commands": failed_tools,
        "execution_windows": windows,
        "estimated_evaluation_intervals": estimates,
        "group_activity_corroboration": {
            "helper_matches": audit["activity_helper_matches"],
            "events": len(corroborated),
        },
        "limits": "未归类时段不算编码；原始进程观察用于复核，缺失活动不判开发效率胜负",
    }
