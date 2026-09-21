"""单组五轮调度、失败留痕与独立比较；不把 fake runner 证据当正式结果。"""

import shutil
import time
import uuid
from pathlib import Path

from .io import inside, inventory, read_json, write_json
from .ledger import summarize_time, summarize_usage
from .prepare import initial_prompt


def validate_protocol(experiment):
    """核对组级会话根与实验根，确认不可变 baseline 尚未被改写。"""
    experiment = Path(experiment).resolve()
    protocol = read_json(experiment / "protocol.json")
    group = protocol["group"]
    if group not in ("plain", "dojo"):
        raise ValueError("未知实验组")
    workspace = Path(protocol["session_workspace_root"])
    if workspace.is_symlink() or workspace.resolve() != experiment.parent:
        raise ValueError("会话必须绑定组级工作根")
    if workspace.name != f"neumann-{group}":
        raise ValueError("组级根名称不符")
    if (
        protocol["experiment_root"] != str(experiment)
        or experiment.name != protocol["experiment_id"]
    ):
        raise ValueError("实验目录身份不符")
    if not experiment.name.startswith("experiment-"):
        raise ValueError("实验目录必须使用 experiment-UUID")
    uuid.UUID(experiment.name.removeprefix("experiment-"))
    if protocol["rounds"] != 5:
        raise ValueError("实验必须为五轮")
    if inventory(experiment / "baseline") != protocol["baseline_files"]:
        raise ValueError("baseline 快照已改变")
    return protocol


def freeze_submission(experiment, submission, output):
    """复制候选科学产物和证据；任何缺失或软链接越界都拒绝。"""
    experiment, output = Path(experiment), Path(output)
    required = ("source", "config", "checkpoint", "predictions", "training", "summary", "diff")
    if any(key not in submission for key in required):
        raise ValueError("候选缺少源码/配置/权重/预测/训练诊断/总结/diff")
    output.mkdir(parents=True, exist_ok=False)
    frozen = {}
    for key in required:
        path = inside(experiment, submission[key])
        if path.is_dir():
            inventory(path)
            shutil.copytree(path, output / key)
        elif path.is_file():
            shutil.copyfile(path, output / key)
        else:
            raise FileNotFoundError(path)
        frozen[key] = key
    frozen["files"] = inventory(output)
    write_json(output / "submission.json", frozen)
    return frozen


def run(experiment, runner, evaluator):
    """同一会话连续五轮；runner 必须审计所有工具，evaluator 属主会话。"""
    experiment = Path(experiment).resolve()
    protocol = validate_protocol(experiment)
    simulation = runner.simulation
    state_path = experiment / "evidence/execution.json"
    state = (
        read_json(state_path)
        if state_path.exists()
        else {
            "status": "prepared",
            "session_id": None,
            "completed_rounds": [],
            "simulation": simulation,
            "started": None,
        }
    )
    if state["simulation"] != simulation:
        raise ValueError("模拟与真实会话不能互相续接")
    try:
        proof = runner.preflight(protocol)
        if (
            not proof.get("all_tools_isolated")
            or proof["workspace"] != protocol["session_workspace_root"]
        ):
            raise ValueError("执行器未验证整个会话的工作根和工具隔离")
        if not simulation and not protocol["environment_ready"]:
            raise ValueError("独立环境尚未通过验收")
        if not simulation:
            baseline = read_json(experiment / "round-00/result.json")
            if baseline["status"] != "complete" or baseline["epochs"] != 5000:
                raise ValueError("正式实验需要完整 round-00")
        write_json(experiment / "evidence/runner-preflight.json", proof)
        if state["started"] is None:
            state["started"] = time.monotonic()
        state["status"] = "running"
        state.pop("error", None)
        if state["session_id"] is None:
            state["session_id"] = runner.create_session(protocol)
            if not state["session_id"]:
                raise ValueError("必须在首轮执行前保存新会话 ID")
        write_json(state_path, state)
        for number in range(1, 6):
            if number in state["completed_rounds"]:
                continue
            round_root = experiment / f"round-{number:02d}"
            attempts = round_root / "attempts"
            attempts.mkdir(exist_ok=True)
            attempt = attempts / str(uuid.uuid4())
            attempt.mkdir()
            prompt = (
                initial_prompt(protocol)
                if number == 1
                else (
                    f"继续本实验第 {number}/5 轮，沿用自己的代码、记录与上下文。"
                    "精度第一，编码时间和 token 单列。完成后提交冻结候选与总结。"
                )
            )
            (attempt / "instruction.txt").write_text(prompt)
            attempt_start = time.monotonic()
            try:
                response = runner.turn(protocol, state["session_id"], number, prompt, attempt)
                if not response.get("session_id"):
                    raise ValueError("执行器未返回会话 ID")
                if state["session_id"] not in (None, response["session_id"]):
                    raise ValueError("五轮必须使用同一会话")
                write_json(state_path, state)
                write_json(attempt / "response.json", response)
                validate_protocol(experiment)
                timing = summarize_time(response["events"], response["started"], response["ended"])
                usage = summarize_usage(response["usage"])
                write_json(attempt / "timing.json", timing)
                write_json(attempt / "usage.json", usage)
                freeze_submission(experiment, response["submission"], attempt / "frozen")
                metrics = evaluator(attempt / "frozen")
                write_json(attempt / "metrics.json", metrics)
                if metrics["status"] != "complete" or metrics["sample_count"] != 10:
                    raise ValueError("十实例评价未完整成功")
                write_json(
                    round_root / "result.json",
                    {
                        "attempt": str(attempt.relative_to(experiment)),
                        "metrics": metrics,
                        "timing": timing,
                        "usage": usage,
                        "session_id": state["session_id"],
                        "simulation": simulation,
                    },
                )
                state["completed_rounds"].append(number)
                write_json(state_path, state)
            except BaseException as exc:
                write_json(
                    attempt / "failure.json",
                    {
                        "type": type(exc).__name__,
                        "error": str(exc),
                        "started": attempt_start,
                        "ended": time.monotonic(),
                    },
                )
                raise
        state["status"] = "five_rounds_completed_final_selection_pending"
    except BaseException as exc:
        state["status"] = "blocked" if not state["session_id"] else "interrupted"
        state["error"] = f"{type(exc).__name__}: {exc}"
        write_json(state_path, state)
        raise
    write_json(state_path, state)
    return state


def summarize(comparison):
    """独立读取两组产物；缺少正式证据时不输出伪排名或零成本。"""
    comparison = Path(comparison)
    config = read_json(comparison / "comparison-protocol.json")
    groups = {}
    for group, location in config["experiments"].items():
        root = Path(location)
        protocol = validate_protocol(root)
        if protocol["baseline_files"] != config["baseline_files"]:
            raise ValueError("两组共同起点已漂移")
        rounds = []
        for n in range(1, 6):
            path = root / f"round-{n:02d}/result.json"
            if path.exists():
                rounds.append({"round": n, **read_json(path)})
        groups[group] = {
            "experiment_id": protocol["experiment_id"],
            "rounds": rounds,
            "completed_rounds": len(rounds),
            "final": None,
        }
        baseline_result = root / "round-00/result.json"
        groups[group]["baseline"] = read_json(baseline_result) if baseline_result.exists() else None
        execution = root / "evidence/execution.json"
        groups[group]["execution"] = read_json(execution) if execution.exists() else None
        final = root / "final/selection.json"
        if final.exists():
            selected = read_json(final)
            chosen = selected["round"]
            candidate = next((r for r in rounds if r["round"] == chosen), None)
            if candidate is not None and selected.get("metrics"):
                groups[group]["final"] = {**candidate, "metrics": selected["metrics"]}
        if rounds:
            groups[group]["best"] = min(
                rounds, key=lambda r: r["metrics"]["final_mean_relative_l2"]
            )
        groups[group]["fifth"] = next((r for r in rounds if r["round"] == 5), None)
    complete = set(groups) == {"plain", "dojo"} and all(
        g["completed_rounds"] == 5 and g["final"] for g in groups.values()
    )
    simulated = any(r.get("simulation") for g in groups.values() for r in g["rounds"])
    accuracy = []
    if complete:
        accuracy = sorted(
            (
                {"group": k, "value": g["final"]["metrics"]["final_mean_relative_l2"]}
                for k, g in groups.items()
            ),
            key=lambda x: x["value"],
        )
    result = {
        "status": "simulation" if simulated else ("complete" if complete else "incomplete"),
        "accuracy_ranking": accuracy,
        "groups": groups,
        "framework_efficiency_ranking": {"coding_seconds": [], "coding_tokens": []},
        "full_cost": {},
        "training_diagnostics": {},
        "dojo_usage": {},
        "evidence_completeness": {k: g["completed_rounds"] for k, g in groups.items()},
    }
    # 所有尝试（包括失败前已记录的账本）都参与成本，不只加已完成轮次。
    for group, location in config["experiments"].items():
        root = Path(location)
        events, usages, windows = [], [], []
        failures = list(root.glob("round-*/attempts/*/failure.json"))
        for path in root.glob("round-*/attempts/*/response.json"):
            response = read_json(path)
            events.extend(response["events"])
            usages.extend(response["usage"])
            windows.append((response["started"], response["ended"]))
        selection_path = root / "final/selection.json"
        if selection_path.exists():
            selected = read_json(selection_path)
            if selected.get("evaluation_event"):
                event = selected["evaluation_event"]
                events.append(event)
                windows.append((event["start"], event["end"]))
        cost = {
            "time": None,
            "tokens": summarize_usage(usages),
            "failed_attempts": len(failures),
            "measurement_complete": bool(windows) and not failures,
        }
        if windows:
            cost["time"] = summarize_time(
                events, min(a for a, _ in windows), max(b for _, b in windows)
            )
            if cost["time"]["unaccounted_seconds"] > 1e-6:
                cost["measurement_complete"] = False
        result["full_cost"][group] = cost
    for metric, ledger in (("coding_seconds", "time"), ("coding_tokens", "tokens")):
        costs = result["full_cost"]
        if complete and all(
            c["measurement_complete"] and c[ledger] and c[ledger].get(metric) is not None
            for c in costs.values()
        ):
            result["framework_efficiency_ranking"][metric] = sorted(
                ({"group": g, "value": c[ledger][metric]} for g, c in costs.items()),
                key=lambda x: x["value"],
            )
    verified_sessions = all(
        (Path(location) / "evidence/execution.json").exists()
        and read_json(Path(location) / "evidence/execution.json").get("status") == "complete"
        for location in config["experiments"].values()
    )
    if result["status"] == "complete" and (
        not verified_sessions
        or not all(c["measurement_complete"] for c in result["full_cost"].values())
    ):
        result["status"] = "incomplete"
    write_json(comparison / "results/comparison.json", result)
    write_json(
        comparison / "results/accuracy.json", {"ranking": accuracy, "status": result["status"]}
    )
    write_json(comparison / "results/cost.json", result["full_cost"])
    (comparison / "REPORT.md").write_text(
        f"# Neumann 双组实验\n\n状态：{result['status']}\n\n"
        + "\n".join(f"- {k}：{g['completed_rounds']}/5 轮。" for k, g in groups.items())
        + "\n\n精度第一；编码时间和 token 独立比较。训练成本不直接判断框架开发效率。\n"
        + "\n## 独立 baseline（不计优化轮）\n\n"
        + "\n".join(
            f"- {k}：{g['baseline']['training']['training_updates']} 次更新，"
            f"训练 {g['baseline']['training']['training_seconds']:.2f} 秒，"
            f"平均完整场相对 L2 {g['baseline']['metrics']['final_mean_relative_l2']:.17g}。"
            for k, g in groups.items()
            if g["baseline"]
        )
        + "\n\n原 709 秒是历史完整 recipe；本次普通 Python baseline 复用准备材料，计时范围不同。\n"
        + "\n## 正式会话状态\n\n"
        + "\n".join(
            f"- {k}：{g['execution']['status']}；"
            f"{g['execution'].get('error', '') if g['execution']['status'] in ('blocked', 'interrupted') else ''}"
            for k, g in groups.items()
            if g["execution"]
        )
        + "\n\n完整准备证据见 evidence/，正式运行完成前不报告 Dojo 效果结论。\n"
    )
    return result


def finalize(experiment, selected_round, evaluator):
    """冻结 agent 指定的已完成轮次并重新评价；计量未封账时仍不标 complete。"""
    experiment = Path(experiment).resolve()
    validate_protocol(experiment)
    state = read_json(experiment / "evidence/execution.json")
    if state["completed_rounds"] != [1, 2, 3, 4, 5] or selected_round not in range(1, 6):
        raise ValueError("必须完成五轮并明确选择其中一轮")
    result = read_json(experiment / f"round-{selected_round:02d}/result.json")
    frozen = inside(experiment, result["attempt"]) / "frozen"
    manifest = read_json(frozen / "submission.json")
    actual = inventory(frozen)
    actual.pop("submission.json")
    if actual != manifest["files"]:
        raise ValueError("已冻结候选发生变化，不能用新文件冒充历史结果")
    target = experiment / "final" / f"submission-{uuid.uuid4()}"
    shutil.copytree(frozen, target)
    start = time.monotonic()
    try:
        metrics = evaluator(target)
        if metrics["status"] != "complete" or metrics["sample_count"] != 10:
            raise ValueError("最终评价必须完整十实例")
    except BaseException as exc:
        write_json(
            target / "failure.json",
            {"error": str(exc), "started": start, "ended": time.monotonic()},
        )
        raise
    write_json(target / "metrics.json", metrics)
    selection = {
        "round": selected_round,
        "submission": str(target.relative_to(experiment)),
        "metrics": metrics,
        "simulation": state["simulation"],
        "evaluation_event": {
            "event_id": str(uuid.uuid4()),
            "phase": "evaluation",
            "start": start,
            "end": time.monotonic(),
        },
    }
    write_json(experiment / "final/selection.json", selection)
    state["status"] = "final_evaluated_accounting_pending"
    write_json(experiment / "evidence/execution.json", state)
    return selection
