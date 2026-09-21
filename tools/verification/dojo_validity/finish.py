"""正式实验封账：两条五轮轨迹、独立精度与全部阶段成本分别交付。"""

import json
import re
import shutil
from pathlib import Path

from .formal import rollout_path
from .io import digest, inside, inventory, read_json, write_json
from .ledger import summarize_time, summarize_usage, union_seconds
from .runner import summarize, validate_protocol
from .telemetry import collect


def diagnostics(root):
    """保留每轮科学诊断原文，同时核对权重实际字节数和冻结内容。"""
    rounds = []
    for number in range(1, 6):
        result = read_json(root / f"round-{number:02d}/result.json")
        frozen = inside(root, result["attempt"]) / "frozen"
        manifest = read_json(frozen / "submission.json")
        actual = inventory(frozen)
        actual.pop("submission.json")
        if actual != manifest["files"]:
            raise ValueError(f"第{number}轮冻结内容被修改")
        source = "\n".join(p.read_text() for p in (frozen / "source").rglob("*.py"))
        imports = sorted(set(re.findall(r"\b(ai4e_[a-zA-Z0-9_.]+)", source)))
        rounds.append(
            {
                "round": number,
                "training": read_json(frozen / "training"),
                "checkpoint_size_bytes": (frozen / "checkpoint").stat().st_size,
                "checkpoint_sha256": digest(frozen / "checkpoint"),
                "ai4e_references_in_frozen_source": imports,
                "summary": (frozen / "summary").read_text(),
            }
        )
    return rounds


def measure_queue(costs):
    """在主控中核对串行执行排队，保留无法归因的其他等待。"""
    for group, cost in costs.items():
        gaps = [
            e
            for e in cost["time"]["intervals"]
            if e["source"] == "between recorded CLI/evaluator processes"
        ]
        other_windows = [
            w for other, c in costs.items() if other != group for w in c["execution_windows"]
        ]
        queue = [
            (max(e["start"], w["start"]), min(e["end"], w["end"]))
            for e in gaps
            for w in other_windows
            if max(e["start"], w["start"]) < min(e["end"], w["end"])
        ]
        cost["time"]["executor_queue_seconds"] = union_seconds(queue)
        cost["time"]["orchestration_wait_seconds"] = union_seconds(
            [(e["start"], e["end"]) for e in gaps]
        )
        cost["time"]["queue_measurement"] = (
            "本组调用间隙与另一组实际 CLI/评价窗口的交集；不推断其他未标记等待的原因。"
        )


def seal(comparison):
    """全部正式候选、活动与原始 usage 可核对后生成最终报告，不填补未知项。"""
    comparison = Path(comparison)
    config = read_json(comparison / "comparison-protocol.json")
    costs, science, states = {}, {}, {}
    for group, location in config["experiments"].items():
        root = Path(location)
        protocol = validate_protocol(root)
        state = read_json(root / "evidence/execution.json")
        if state["completed_rounds"] != [1, 2, 3, 4, 5] or state["simulation"]:
            raise ValueError(f"{group} 尚未完成五轮正式实验")
        selection = read_json(root / "final/selection.json")
        if (
            selection["metrics"]["status"] != "complete"
            or selection["metrics"]["sample_count"] != 10
        ):
            raise ValueError("最终候选十实例评价不完整")
        costs[group] = collect(protocol)
        pure = costs[group]["tokens"]["coding_tokens"]
        mixed = sum(
            r["input_tokens"] + r["output_tokens"]
            for r in costs[group]["tokens"]["raw_requests"]
            if r["phase"] == "mixed"
        )
        costs[group]["coding_token_bounds"] = {
            "lower": pure,
            "upper": pure + mixed if pure is not None else None,
            "mixed_unallocated": mixed,
        }
        baseline = read_json(root / "round-00/result.json")
        costs[group]["round00_preparation"] = baseline
        costs[group]["training_seconds_including_round00"] = (
            baseline["training"]["training_seconds"] + costs[group]["time"]["training_seconds"]
        )
        costs[group]["per_round"] = []
        for number in range(1, 6):
            windows = [w for w in costs[group]["execution_windows"] if w["round"] == number]
            start, end = min(w["start"] for w in windows), max(w["end"] for w in windows)
            intervals = [
                dict(e, start=max(start, e["start"]), end=min(end, e["end"]))
                for e in costs[group]["time"]["intervals"]
                if e["end"] > start and e["start"] < end
            ]
            turns = {w.get("turn_id") for w in windows if w.get("turn_id")}
            requests = [
                r
                for r in costs[group]["tokens"]["raw_requests"]
                if r["raw"].get("turn_id") in turns
            ]
            costs[group]["per_round"].append(
                {
                    "round": number,
                    "time": summarize_time(intervals, start, end),
                    "tokens": summarize_usage(requests),
                }
            )
        write_json(root / "results/accounting-rounds.json", costs[group]["per_round"])
        science[group] = diagnostics(root)
        if not costs[group]["measurement_complete"]:
            raise ValueError(f"{group} 成本尚未完整记账")
        states[group] = state
    measure_queue(costs)
    result = summarize(comparison)
    result.update(status="complete", full_cost=costs, training_diagnostics=science)
    result["framework_efficiency_ranking"] = {}
    for metric, ledger in [("coding_seconds", "time"), ("coding_tokens", "tokens")]:
        rows = [
            {"group": group, "value": cost[ledger].get(metric)} for group, cost in costs.items()
        ]
        result["framework_efficiency_ranking"][metric] = (
            sorted(rows, key=lambda r: r["value"])
            if all(r["value"] is not None for r in rows)
            else []
        )
    bounds = sorted(
        ({"group": g, **c["coding_token_bounds"]} for g, c in costs.items()),
        key=lambda b: b["lower"] if b["lower"] is not None else float("inf"),
    )
    result["coding_token_intervals"] = bounds
    if (
        any(b["lower"] is None or b["upper"] is None for b in bounds)
        or bounds[0]["upper"] > bounds[1]["lower"]
    ):
        result["framework_efficiency_ranking"]["coding_tokens"] = []
        result["coding_token_ordering"] = "indeterminate_mixed_request_ranges_overlap"
    else:
        result["coding_token_ordering"] = "ordered_without_allocating_mixed_requests"
    result["dojo_usage"] = {}
    for group, location in config["experiments"].items():
        root = Path(location)
        read_events = []
        for path in root.glob("round-*/attempts/*/cli/events.jsonl"):
            for line in path.read_text().splitlines():
                entry = json.loads(line)
                item = entry["event"].get("item", {})
                command = item.get("command", "")
                if (
                    item.get("type") == "command_execution"
                    and item.get("status") == "completed"
                    and any(
                        s in command for s in ["DOJO_AGENT_GUIDE", "agent-help", "dojo-research"]
                    )
                ):
                    read_events.append(
                        {
                            "source": str(path.relative_to(root)),
                            "command": command,
                            "exit_code": item.get("exit_code"),
                        }
                    )
        result["dojo_usage"][group] = {
            "documentation_events": read_events,
            "round_source_references": [
                {k: r[k] for k in ["round", "ai4e_references_in_frozen_source"]}
                for r in science[group]
            ],
            "interpretation": "源码引用和文档读取单列；是否实际调用应结合本组训练命令和运行产物核对。",
        }
        protected = comparison / "evidence/groups" / group
        protected.mkdir(parents=True, exist_ok=True)
        for name in ("whole-process-isolation.json", "formal-initialization/session.json"):
            source = root / "evidence" / name
            target = protected / Path(name).name
            shutil.copyfile(source, target)
        shutil.copyfile(
            rollout_path(read_json(root / "protocol.json"), states[group]["session_id"]),
            protected / "formal-rollout.jsonl",
        )
        for path in root.glob("round-*/attempts/*/cli/events.jsonl"):
            target = protected / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        selected = read_json(root / "final/selection.json")
        final_path = inside(root, selected["submission"])
        shutil.copytree(final_path, protected / "final-submission", dirs_exist_ok=True)
        for path in root.glob("evidence/evaluations/*/execution.json"):
            if str(final_path / "source/infer.py") in read_json(path)["command"]:
                shutil.copytree(
                    path.parent, protected / "independent-final-evaluation", dirs_exist_ok=True
                )
        write_json(
            protected / "evidence-manifest.json",
            {
                "files": {
                    k: v for k, v in inventory(protected).items() if k != "evidence-manifest.json"
                },
                "credential_files_copied": False,
            },
        )
    # 实际复制受保护证据后才封账；失败尝试已由完整账本覆盖。
    for group, location in config["experiments"].items():
        state = states[group]
        state.update(status="complete", accounting="results/cost-audit.json")
        state.pop("error", None)
        write_json(Path(location) / "evidence/execution.json", state)
        result["groups"][group]["execution"] = state
    result["evidence_completeness"] = {
        group: {
            "rounds": 5,
            "session_id": states[group]["session_id"],
            "independent_final_samples": 10,
            "cost_complete": True,
            "provider_retry_count": None,
        }
        for group in states
    }
    review_path = comparison / "evidence/scientific-review.json"
    if review_path.exists():
        result["scientific_review"] = read_json(review_path)
        for group, review in result["scientific_review"].get("groups", {}).items():
            if group in result["dojo_usage"]:
                result["dojo_usage"][group]["verified_review"] = review
    write_json(comparison / "results/comparison.json", result)
    write_json(
        comparison / "results/accuracy.json",
        {
            "status": "complete",
            "ranking": result["accuracy_ranking"],
            "rounds": {
                g: [
                    {
                        "round": r["round"],
                        "mean_relative_l2": r["metrics"]["final_mean_relative_l2"],
                    }
                    for r in v["rounds"]
                ]
                for g, v in result["groups"].items()
            },
        },
    )
    write_json(comparison / "results/cost.json", costs)
    lines = [
        "# PI-BSNet Neumann 双组五轮实验结果",
        "",
        "两组各在一个全新 Codex CLI 会话中完成五轮，最终候选均从冻结源码和权重重新推理，十实例 FP64 复算。精度、编码时间与编码 token 分别比较。",
        "固定 round-00 已在正式会话初始化前由主控在两组独立环境分别实跑，平均相对 L2 均为 0.018813866272418954。它的成本作为准备测量单列；以下端到端和 token 是各正式会话初始化至最终评价的口径。",
        "",
    ]
    for group in ["plain", "dojo"]:
        data = result["groups"][group]
        cost = costs[group]
        group_lines = [
            f"## {'白板组' if group == 'plain' else 'Dojo 可用组'}",
            "",
            f"- 会话：`{states[group]['session_id']}`。",
            f"- 最终提交第 {data['final']['round']} 轮，平均相对 L2：`{data['final']['metrics']['final_mean_relative_l2']:.15g}`。",
            f"- 第五轮：`{data['fifth']['metrics']['final_mean_relative_l2']:.15g}`；五轮最佳：`{data['best']['metrics']['final_mean_relative_l2']:.15g}`（第 {data['best']['round']} 轮）。",
            f"- 编码时间：{cost['time']['coding_seconds']:.3f} 秒；纯编码请求 token：{cost['tokens']['coding_tokens']}；混合活动 token：{cost['tokens']['mixed_tokens']}。",
            f"- 编码 token 可归属区间：{cost['coding_token_bounds']['lower']}–{cost['coding_token_bounds']['upper']}；混合请求不强行拆分。",
            f"- 训练：{cost['time']['training_seconds']:.3f} 秒；评价：{cost['time']['evaluation_seconds']:.3f} 秒；环境准备：{cost['time']['environment_setup_seconds']:.3f} 秒。",
            f"- 加计固定 round-00 后训练总时间：{cost['training_seconds_including_round00']:.3f} 秒。",
            f"- 端到端：{cost['time']['end_to_end_seconds']:.3f} 秒；其中等待 {cost['time']['idle_or_wait_seconds']:.3f} 秒；全部去重 token：{cost['tokens']['total_accounted_tokens']}。",
            f"- Token 构成：输入 {cost['tokens']['input_tokens']}、输出 {cost['tokens']['output_tokens']}；缓存读取 {cost['tokens']['cache_read_tokens']} 已包含在输入中，不重复加总。",
            f"- 执行器排队：{cost['time']['executor_queue_seconds']:.3f} 秒（包含在等待中）；全部调用间主控等待：{cost['time']['orchestration_wait_seconds']:.3f} 秒。串行排队不是框架耗时。",
            f"- 留档失败尝试：{cost['failed_attempts']}。",
            "",
        ]
        lines += group_lines
        own_rounds = [
            f"- 第 {r['round']} 轮：平均相对 L2 `{r['metrics']['final_mean_relative_l2']:.15g}`。"
            for r in data["rounds"]
        ]
        (Path(config["experiments"][group]) / "REPORT.md").write_text(
            "\n".join(
                [
                    "# 本组五轮实验结果",
                    "",
                    *group_lines,
                    "## 五轮轨迹",
                    "",
                    *own_rounds,
                    "",
                    "本报告仅含本组结果。完整区间、请求用量与逐轮统计见 results/cost-audit.json 和 results/accounting-rounds.json；最终独立评价见 final/selection.json。",
                    "共同 round-00 是正式会话初始化前的准备测量，训练成本单列；固定十个测试实例参与多轮反馈，不能作为独立泛化测试。",
                    "",
                ]
            )
        )
    lines += [
        "## 解释范围与证据",
        "",
        "计时直接来自模型/工具事件和实际进程，重叠取并集。请求 token 按实际工具活动分类，混合请求单列；未提供的供应商重试计数仍为空。初始工具路径缺失造成的白板首轮中断保留在总成本中，并在组织修复记录中单列，不能解释为框架差异。",
        "训练时间随科学模型变化而改变，不直接代表框架开发效率。五轮是两条连续轨迹；结论仅限本案例和这两条轨迹。",
        "混合请求同时包含编码和其他活动；若两组编码 token 区间重叠，不给出确定的编码 token 胜负。完整 token 总量仍可直接比较。",
        "逐轮精度、阶段时间区间、原始 request ID/usage、训练诊断、Dojo 文档读取与源码组件引用见 results/ 下三个 JSON；原始证据分别保存在两组 evidence/，比较材料只写入本主会话目录。",
        "",
    ]
    if "scientific_review" in result:
        lines += ["## 科学与框架使用核查", "", *result["scientific_review"]["findings"], ""]
    (comparison / "REPORT.md").write_text("\n".join(lines))
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()
    seal(args.comparison)
