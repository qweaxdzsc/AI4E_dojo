"""主会话专属汇总：最终选择、第五轮与测试事后最优分开，成本不加权。"""

from pathlib import Path

from ..io import inside, read_json, write_json
from ..ledger import union_seconds
from .accounting import collect


def training_diagnostics(root, group, number, receipt):
    """参数与训练信息注明声明来源，checkpoint字节数由主控直接核文件。"""
    candidate = root / "frozen" / group / f"round-{number:02d}"
    manifest = receipt["source_manifest"]
    checkpoint = inside(candidate, manifest["checkpoint"])
    names = {
        "parameter_count",
        "trainable_parameter_count",
        "total_parameter_count",
        "model_depth",
        "training_updates",
        "updates",
        "epochs",
        "device",
        "resolved_device",
        "thread_count",
        "rss_peak_bytes",
        "peak_memory_bytes",
        "mps_driver_peak_observed_bytes",
    }
    declarations = []

    def visit(value, source):
        if isinstance(value, dict):
            found = {key: item for key, item in value.items() if key in names}
            if found:
                declarations.append({"source": source, "values": found})
            for item in value.values():
                if isinstance(item, dict):
                    visit(item, source)

    for path in candidate.rglob("*.json"):
        if path.stat().st_size < 10_000_000:
            visit(read_json(path), path.relative_to(candidate).as_posix())
    hidden = root / "hidden-results" / group / f"round-{number:02d}/result.json"
    model_info = read_json(hidden).get("loaded_models") if hidden.exists() else None
    weights = {
        str(p.relative_to(candidate)): p.stat().st_size
        for p in candidate.rglob("*")
        if p.is_file() and p.suffix in {".pt", ".pth", ".safetensors"}
    }
    return {
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "weight_assets_size_bytes": sum(weights.values()) if weights else None,
        "weight_asset_files": weights,
        "checkpoint_size_scope": "manifest checkpoint may be a JSON ensemble recipe; weight assets are reported separately",
        "declarations": declarations,
        "parameter_count_verified_from_loading": bool(
            model_info and model_info.get("total_parameter_count") is not None
        ),
        "loaded_models": model_info,
        "source": "frozen candidate metadata plus controller file size; inspect source/logs for actual calls",
    }


def summarize(comparison):
    """只有隐藏评价完成后绘制测试曲线；不向任何组根写回测试信息。"""
    root = Path(comparison)
    state = read_json(root / "state.json")
    if state["phase"] not in {
        "hidden_evaluated_accounting_pending",
        "complete",
        "evaluated_evidence_incomplete",
        "evaluated_review_pending",
    }:
        raise ValueError("隐藏评价尚未完成，禁止伪造对比结果")
    result_dir = root / "results"
    result_dir.mkdir(exist_ok=True)
    groups, costs = {}, {}
    for group in ("plain", "dojo"):
        rounds = []
        for number in range(6):
            row = read_json(root / "hidden-results" / group / f"round-{number:02d}/result.json")
            receipt = read_json(root / "receipts" / group / f"round-{number:02d}.json")
            method = receipt["source_manifest"]["method"]
            try:
                path = inside(root / "frozen" / group / f"round-{number:02d}", method)
                if path.is_file():
                    method = path.read_text()
            except (ValueError, OSError):
                pass
            validations = sorted(
                (root / "validation" / group / f"round-{number:02d}").glob("*/result.json"),
                key=lambda p: p.stat().st_mtime,
            )
            validation = next(
                read_json(p) for p in reversed(validations) if read_json(p)["status"] == "evaluated"
            )
            rounds.append(
                {
                    "round": number,
                    "method": method,
                    "dojo_usage": receipt["source_manifest"]["dojo_usage"],
                    "training_diagnostics": training_diagnostics(root, group, number, receipt),
                    "hidden": row,
                    "validation": validation,
                }
            )
        final = read_json(root / "final-selections" / f"{group}.json")
        valid = [r for r in rounds if r["hidden"].get("accuracy") is not None]
        groups[group] = {
            "rounds": rounds,
            "final_selection": final,
            "final": rounds[final["round"]]["hidden"],
            "round_05": rounds[5]["hidden"],
            "posthoc_best_round": min(
                valid, key=lambda r: r["hidden"]["accuracy"]["mean_field_relative_l2"]
            )["round"]
            if valid
            else None,
        }
        costs[group] = collect(root, group)
    for group, other in (("plain", "dojo"), ("dojo", "plain")):
        gaps = [
            e
            for e in costs[group]["time"]["intervals"]
            if e["source"] == "controller scheduling gap"
        ]
        costs[group]["time"]["executor_queue_seconds"] = union_seconds(
            [
                (max(gap["start"], a), min(gap["end"], b))
                for gap in gaps
                for a, b in costs[other]["execution_windows"]
                if max(gap["start"], a) < min(gap["end"], b)
            ]
        )
    eligible = [g for g in groups if groups[g]["final"].get("eligible")]
    accuracy_ranking = sorted(
        eligible, key=lambda g: groups[g]["final"]["accuracy"]["mean_field_relative_l2"]
    )
    accounted = all(c["status"] in {"accounted", "accounted_with_limits"} for c in costs.values())
    complete_cost_evidence = all(c["status"] == "accounted" for c in costs.values())
    coding_ranking = (
        sorted(costs, key=lambda g: costs[g]["time"]["coding_seconds"]) if accounted else None
    )
    token_ranking = None
    if all(
        costs[g].get("tokens") and costs[g]["tokens"].get("coding_tokens_upper") is not None
        for g in costs
    ) and not any(c.get("connection_retry_events") for c in costs.values()):
        a, b = (costs[g]["tokens"] for g in ("plain", "dojo"))
        if a["coding_tokens_upper"] < b["coding_tokens_lower"]:
            token_ranking = ["plain", "dojo"]
        elif b["coding_tokens_upper"] < a["coding_tokens_lower"]:
            token_ranking = ["dojo", "plain"]
    review_path = root / "evidence/final-review.json"
    review = read_json(review_path) if review_path.exists() else {}
    reviewed = all(
        review.get(k) is True
        for k in (
            "local_isolation",
            "data_lineage_reviewed",
            "dojo_calls_reviewed",
            "baseline_contracts_reviewed",
            "frozen_assets_unchanged",
            "usage_reconciled",
        )
    )
    summary = {
        "status": ("complete" if reviewed else "evaluated_review_pending")
        if complete_cost_evidence and len(eligible) == 2
        else "evaluated_evidence_incomplete",
        "scientific_runs_complete": all(
            all(r["hidden"]["status"] == "evaluated" for r in g["rounds"]) for g in groups.values()
        ),
        "cost_evidence_complete": complete_cost_evidence,
        "accuracy_ranking": accuracy_ranking,
        "framework_efficiency_ranking": {
            "coding_seconds": coding_ranking,
            "coding_tokens": token_ranking,
        },
        "full_cost": costs,
        "accuracy": groups,
        "dojo_usage": [r["dojo_usage"] for r in groups["dojo"]["rounds"]],
        "training_diagnostics": {
            g: [r["training_diagnostics"] for r in groups[g]["rounds"]] for g in groups
        },
        "evidence_completeness": {g: costs[g]["status"] for g in groups},
        "final_review": review,
        "protocol_clarifications": [
            {"file": str(p.relative_to(root)), "record": read_json(p)}
            for p in sorted((root / "evidence").glob("protocol-clarification-*.json"))
        ],
        "hidden_test_reveal": "only after both final selections frozen; never copied into group roots",
        "contamination_audit": {
            "local_test_isolated": True,
            "public_data_reacquisition": "requires session/download provenance audit; TLS content not inspected",
        },
        "limits": [
            "两条连续轨迹，不是五次独立重复",
            "没有同问题JOREK求解器测速，不计算CAE加速比",
            "最初三次主控验证区间缺少独立单调时钟记录，已以主控文件时间估计并标明来源",
            "未独立标记的训练进程内部验证不能宣称已精确拆分；训练进程耗时须结合源码和日志说明范围",
            "初始主指标与可复用工具说明有对称补充；实际阅读时机及对工具选择的影响属于实验限制",
        ],
    }
    write_json(result_dir / "accuracy.json", groups)
    write_json(result_dir / "cost.json", costs)
    write_json(result_dir / "comparison.json", summary)
    plot(groups, costs, result_dir)
    lines = [
        "# JOREK RMHD 双组五轮结果",
        "",
        f"状态：{summary['status']}。精度排序只包括最终推理 P95 ≤50ms 的方案。",
        "",
        "![精度曲线](results/accuracy.png)",
        "![最终六场误差](results/fields.png)",
        "![完整预测延迟](results/latency.png)",
        "![轮次开发成本](results/development-cost.png)",
        "",
        "隐藏测试在双方最终冻结后统一评价；测试事后最优不参与最终选择。",
        "",
    ]
    for group, data in groups.items():
        final = data["final"]
        accuracy = final.get("accuracy") or {}
        lines += [
            f"## {group}",
            "",
            f"最终选择 round-{data['final_selection']['round']:02d}；相对 L2 {accuracy.get('mean_field_relative_l2')}；P95 {final.get('latency_p95_seconds')} 秒。",
            f"第五轮相对 L2 {(data['round_05'].get('accuracy') or {}).get('mean_field_relative_l2')}；事后测试最优轮次 {data['posthoc_best_round']}，不替换最终选择。",
            "",
        ]
        lines += [
            f"- round-{r['round']:02d}：{r['method']}；隐藏误差 {(r['hidden'].get('accuracy') or {}).get('mean_field_relative_l2')}。"
            for r in data["rounds"]
        ]
        lines += [
            "",
            f"成本证据状态：{costs[group]['status']}。详细区间、请求usage及未知项见 results/cost.json。",
            f"编码 {costs[group]['time']['coding_seconds'] / 60:.2f} 分钟；已入账编码 token 范围 {costs[group]['tokens']['coding_tokens_lower']}–{costs[group]['tokens']['coding_tokens_upper']}。",
            "",
        ]
    lines += [
        "只对本案例和两条优化轨迹陈述结果。公开数据再获取须结合原始会话及网络目标记录审计；不声称公网绝对保密。"
    ]
    lines += ["", *[f"- {item}。" for item in summary["limits"]]]
    for group, cost in costs.items():
        if cost.get("connection_retry_events"):
            lines.append(
                f"- {group} 有 {len(cost['connection_retry_events'])} 次可观测连接重试，未回传请求 usage 的部分未知，不计作零；不据此给出完整编码 token 胜负。"
            )
    (root / "REPORT.md").write_text("\n".join(lines) + "\n")
    write_json(root / "state.json", {"phase": summary["status"], "formal_sessions_started": True})
    return summary


def plot(groups, costs, output):
    """导出可分享的科学曲线：验证与隐藏测试分图，标注实际最终选择。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    for ax, split in zip(axes, ("validation", "hidden"), strict=True):
        for group, data in groups.items():
            values = [
                (r[split].get("accuracy") or {}).get("mean_field_relative_l2", float("nan"))
                for r in data["rounds"]
            ]
            ax.plot(range(6), values, "o-", label=group)
            index = data["final_selection"]["round"]
            ax.scatter([index], [values[index]], marker="*", s=180, zorder=5)
        ax.set(
            title=f"{split.title()} relative L2",
            xlabel="Round (0 = baseline)",
            ylabel="Six-field mean relative L2",
        )
        ax.set_xticks(range(6))
        ax.grid(alpha=0.25)
        ax.legend()
    fig.savefig(output / "accuracy.png", dpi=180)
    plt.close(fig)
    import numpy as np

    fields = ("Psi", "u", "zj", "omega", "rho", "T")
    fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
    for i, (group, data) in enumerate(groups.items()):
        accuracy = data["final"].get("accuracy") or {}
        values = [accuracy.get("per_field_relative_l2", {}).get(f, float("nan")) for f in fields]
        ax.bar(np.arange(6) + (i - 0.5) * 0.35, values, width=0.35, label=group)
    ax.set_xticks(np.arange(6), fields)
    ax.set(ylabel="Relative L2", title="Final selected candidates: hidden test")
    ax.legend()
    fig.savefig(output / "fields.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
    for group, data in groups.items():
        values = [
            r["hidden"].get("latency_p95_seconds", float("nan")) * 1000 for r in data["rounds"]
        ]
        ax.plot(range(6), values, "o-", label=group)
        n = data["final_selection"]["round"]
        ax.scatter([n], [values[n]], marker="*", s=180, zorder=5)
    ax.axhline(50, color="red", linestyle="--", label="50 ms eligibility limit")
    ax.set(
        title="Complete 40-frame prediction: hidden inputs, batch 1",
        xlabel="Round",
        ylabel="Median of three batch P95 values (ms)",
    )
    ax.set_xticks(range(6))
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(output / "latency.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    for group, cost in costs.items():
        if not cost.get("time") or not cost.get("tokens"):
            continue
        intervals = cost["time"]["intervals"]
        requests = cost["tokens"]["raw_requests"]
        seconds = [
            union_seconds(
                [
                    (e["start"], e["end"])
                    for e in intervals
                    if e.get("round") == n and e["phase"] == "coding"
                ]
            )
            for n in range(6)
        ]
        tokens = [
            sum(
                r["input_tokens"] + r["output_tokens"]
                for r in requests
                if r.get("round") == n
                and r["phase"] == "coding"
                and r.get("input_tokens") is not None
                and r.get("output_tokens") is not None
            )
            for n in range(6)
        ]
        axes[0].plot(range(6), np.cumsum(seconds) / 60, "o-", label=group)
        axes[1].plot(range(6), np.cumsum(tokens), "o-", label=group)
        uncertain = [
            sum(
                r["input_tokens"] + r["output_tokens"]
                for r in requests
                if r.get("round") == n
                and r["phase"] in {"mixed", "unclassified"}
                and r.get("input_tokens") is not None
                and r.get("output_tokens") is not None
            )
            for n in range(6)
        ]
        axes[1].fill_between(
            range(6), np.cumsum(tokens), np.cumsum(np.array(tokens) + uncertain), alpha=0.15
        )
    for ax, title in zip(
        axes, ("Cumulative coding minutes", "Accounted coding tokens (bounds)"), strict=True
    ):
        ax.set(title=title, xlabel="Round (excludes final selection)")
        ax.set_xticks(range(6))
        ax.grid(alpha=0.25)
        ax.legend()
    fig.savefig(output / "development-cost.png", dpi=180)
    plt.close(fig)
