"""主会话人工核验后的利用率汇总；参考覆盖与实际职责复用分别计算。"""

import json
from collections import Counter
from pathlib import Path

from ..io import write_json
from .skill_study import OPPORTUNITIES


def index_events(root, number):
    """生成原始事件阅读索引；启发式标签不是阅读充分性或实际采用的判定。"""
    root = Path(root)
    rows = []
    for path in sorted(
        (root / f"evidence/sessions/dojo/round-{number:02d}").glob("*/events.jsonl")
    ):
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            event = json.loads(line)
            if event["event"].get("type") != "item.completed":
                continue
            item = event["event"].get("item", {})
            text = item.get("command", "")
            tags = []
            if item.get("type") == "web_search" or "https://" in text:
                tags.append("external_reference_candidate")
            if any(
                x in text
                for x in ("dojo-resources", "ai4e_core", "read_help_topic", "describe_help_symbol")
            ):
                tags.append("dojo_reference_or_call_candidate")
            if item.get("type") == "file_change" or any(
                x in text for x in ("write_text(", "cat >", "apply_patch")
            ):
                tags.append("implementation_change_candidate")
            if "activity.py training" in text:
                tags.append("training_command")
            rows.append(
                {
                    "time": event["received"],
                    "source": str(path.relative_to(root)),
                    "line": line_number,
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "tags": tags,
                    "command": text,
                    "exit_code": item.get("exit_code"),
                    "text": item.get("text"),
                }
            )
    rows.sort(key=lambda row: row["time"])
    write_json(root / f"reviews/round-{number:02d}-events.json", rows)
    return rows


def summarize_review(review):
    """按冻结职责清单计一次机会；未知不补零，直接与可适配能力均入分母。"""
    rows = review["opportunities"]
    if set(rows) != set(OPPORTUNITIES):
        raise ValueError("职责清单缺失或漂移")
    available = {"direct", "adaptable"}
    adopted = {"direct", "adapted"}
    applicability, choices = Counter(), Counter()
    numerator = denominator = 0
    for key, row in rows.items():
        a, c = row["availability"], row["choice"]
        if a not in available | {"not_applicable", "unknown"}:
            raise ValueError(f"非法能力适用性: {key}")
        if c not in adopted | {"justified_custom", "custom", "not_applicable", "unknown"}:
            raise ValueError(f"非法选择: {key}")
        if a == "not_applicable" and c in adopted:
            raise ValueError("不适用项不能同时计采用")
        if c in adopted and not row.get("evidence"):
            raise ValueError("实际复用必须有调用或运行证据")
        if c == "justified_custom" and not row.get("reason"):
            raise ValueError("有理由自写必须有具体原因")
        applicability[a] += 1
        choices[c] += 1
        denominator += a in available
        numerator += a in available and c in adopted
    decisions = review.get("decisions", [])
    both = sum(bool(d.get("dojo_evidence")) and bool(d.get("web_evidence")) for d in decisions)
    return {
        "responsibility_count": len(rows),
        "availability_counts": dict(applicability),
        "choice_counts": dict(choices),
        "reused_known_applicable": numerator,
        "known_applicable": denominator,
        "utilization_known": numerator / denominator if denominator else None,
        "unknown_availability": applicability["unknown"],
        "unknown_choice": choices["unknown"],
        "decision_count_reviewed": len(decisions),
        "dual_reference_decisions": both,
        "dual_reference_coverage": both / len(decisions) if decisions else None,
        "framework_responsibilities": {
            k: rows[k] for k in ("training_loop", "run_records", "checkpoint_and_resume")
        },
        "basis": "main-session code and original-event review; one count per responsibility, not imports",
    }
