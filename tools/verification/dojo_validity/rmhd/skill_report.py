"""单组 Skill 研究的主控报告；不将适应性轨迹解释为随机对照因果结果。"""

import argparse
import json
from pathlib import Path

from ..io import read_json, write_json
from ..ledger import union_seconds
from .accounting import collect
from .controller import verify_frozen
from .report import training_diagnostics


def internal_evaluation(root, intervals):
    """核对冻结回调区间与主控训练区间；组内时钟只作有来源的补充分解。"""
    rows, gaps = [], []
    seen = set()
    for number in range(6):
        candidate = Path(root) / f"frozen/dojo/round-{number:02d}"
        paths = sorted(candidate.glob("training-logs/*validation-events.jsonl"))
        if not paths:
            gaps.append({"round": number, "reason": "no frozen internal-validation intervals"})
        for path in paths:
            pending = {}
            for record in map(json.loads, path.read_text().splitlines()):
                key = (record.get("updates"), record.get("variant"))
                when = record["monotonic"]
                if record["event"] == "start":
                    if key in pending:
                        raise ValueError("重复内部验证开始事件")
                    pending[key] = when
                elif record["event"] == "end":
                    if key not in pending:
                        raise ValueError("内部验证结束缺少开始")
                    start = pending.pop(key)
                    union_seconds([(start, when)])
                    identity = (number, start, when)
                    if identity in seen:
                        continue
                    seen.add(identity)
                    enclosing = [
                        e
                        for e in intervals
                        if e["phase"] == "training"
                        and e.get("round") == number
                        and e["start"] <= start <= when <= e["end"]
                    ]
                    if not enclosing:
                        gaps.append(
                            {
                                "round": number,
                                "file": str(path),
                                "reason": "not enclosed by observed training",
                                "start": start,
                                "end": when,
                            }
                        )
                        continue
                    rows.append(
                        {
                            "round": number,
                            "start": start,
                            "end": when,
                            "source": str(path),
                            "evidence_level": "frozen agent callback clock, enclosed by controller-observed training",
                        }
                    )
            if pending:
                gaps.append(
                    {"round": number, "file": str(path), "reason": "unfinished validation callback"}
                )
    return {
        "intervals": rows,
        "seconds": union_seconds([(r["start"], r["end"]) for r in rows]),
        "gaps": gaps,
        "independently_instrumented": False,
    }


def report(root):
    """六轮冻结与隐藏评分后汇总真实结果；证据缺口不会阻止如实交付。"""
    root = Path(root)
    if read_json(root / "state.json")["phase"] not in {
        "single_hidden_evaluated_review_pending",
        "single_science_complete_evidence_partial",
        "single_complete",
    }:
        raise ValueError("隐藏评价尚未完成")
    rounds = []
    for number in range(6):
        verify_frozen(root, "dojo", number)
        paths = sorted(
            (root / f"validation/dojo/round-{number:02d}").glob("*/result.json"),
            key=lambda p: p.stat().st_mtime,
        )
        validation = next(
            read_json(p) for p in reversed(paths) if read_json(p)["status"] == "evaluated"
        )
        receipt = read_json(root / f"receipts/dojo/round-{number:02d}.json")
        review = read_json(root / f"reviews/round-{number:02d}.json")
        rounds.append(
            {
                "round": number,
                "validation": validation,
                "hidden": read_json(root / f"hidden-results/dojo/round-{number:02d}/result.json"),
                "review": review,
                "skill": read_json(root / f"skill-revisions/round-{number:02d}.json"),
                "training": training_diagnostics(root, "dojo", number, receipt),
            }
        )
    selection = read_json(root / "final-selections/dojo.json")
    cost = collect(root, "dojo")
    nested = internal_evaluation(root, cost["time"]["intervals"])
    cost["internal_evaluation_supplement"] = nested
    process_seconds = union_seconds(
        [
            (e["start"], e["end"])
            for e in cost["time"]["intervals"]
            if e["phase"] == "training" and e["event_id"].startswith("activity:")
        ]
    )
    cost["training_time_evidence"] = {
        "observed_command_envelope_seconds": cost["time"]["training_seconds"],
        "corroborated_activity_process_seconds": process_seconds,
        "envelope_outside_activity_seconds": cost["time"]["training_seconds"] - process_seconds,
        "limit": "外层工具区间不能全部当实际训练；内部验证补充未独立计量，基线还缺细分",
    }
    usage_audit = root / "reviews/usage-attempt-reconciliation.json"
    if usage_audit.exists():
        cost["usage_attempt_audit"] = read_json(usage_audit)
    cost["main_session_cost"] = {
        "coding_seconds": None,
        "tokens": None,
        "reason": "main review/Skill work was not separately instrumented; never zero-filled",
    }
    for row in rounds:
        n = row["round"]
        events = [e for e in cost["time"]["intervals"] if e.get("round") == n]
        times = {
            p: union_seconds([(e["start"], e["end"]) for e in events if e["phase"] == p])
            for p in ("coding", "training", "evaluation", "environment_setup", "data_preparation")
        }
        internal = union_seconds(
            [(e["start"], e["end"]) for e in nested["intervals"] if e["round"] == n]
        )
        requests = [q for q in cost["tokens"]["raw_requests"] if q.get("round") == n]
        known = [
            q
            for q in requests
            if q.get("input_tokens") is not None and q.get("output_tokens") is not None
        ]
        lo = sum(q["input_tokens"] + q["output_tokens"] for q in known if q["phase"] == "coding")
        hi = lo + sum(
            q["input_tokens"] + q["output_tokens"]
            for q in known
            if q["phase"] in {"mixed", "unclassified"}
        )
        row["cost"] = {
            "observed_seconds": times,
            "internal_evaluation_supplement_seconds": internal,
            "training_excluding_supplement_seconds": times["training"] - internal,
            "coding_tokens_accounted_lower": lo if requests else None,
            "coding_tokens_accounted_upper": hi if requests else None,
            "total_accounted_tokens": sum(q["input_tokens"] + q["output_tokens"] for q in known)
            if requests
            else None,
            "missing_usage_requests": len(requests) - len(known),
        }
    result = {
        "rounds": rounds,
        "final_selection": selection,
        "cost": cost,
        "causal_claim": False,
        "holdout": "reused protocol holdout; hidden from this research session, previously evaluated by main in an earlier study",
        "posthoc_best_round": min(
            (r for r in rounds if r["hidden"].get("accuracy")),
            key=lambda r: r["hidden"]["accuracy"]["mean_field_relative_l2"],
        )["round"],
    }
    output = root / "results"
    write_json(output / "study.json", result)
    write_json(output / "cost.json", cost)
    plot(result, output)
    final = rounds[selection["round"]]["hidden"]
    lines = [
        "# Dojo Skill 隔离五轮研究报告",
        "",
        "已完成一个全新隔离 Codex CLI 会话的 round-00 与五轮优化；主会话逐轮审查并在轮间交付 Skill。",
        "",
        f"最终按验证集选择 round-{selection['round']:02d}；隐藏测试主误差 **{final['accuracy']['mean_field_relative_l2']:.8f}**，完整40帧 P95 **{1000 * final['latency_p95_seconds']:.2f} ms**，50ms准入：**{final['eligible']}**。",
        "",
        "本次为单条适应性研究轨迹。精度变化同时受到方法、训练量、会话学习和Skill影响，不能单独归因Skill，也没有新的白板组对照。",
        "",
        "![精度与延迟](results/accuracy-latency.png)",
        "",
        "![职责复用](results/utilization.png)",
        "",
        "## 各轮方法与结果",
        "",
    ]
    for r in rounds:
        v, h, u = r["validation"], r["hidden"], r["review"]["summary"]
        lines += [
            f"- **round-{r['round']:02d}**：{r['review']['method']}。验证 {v['accuracy']['mean_field_relative_l2']:.8f}；隐藏 {h['accuracy']['mean_field_relative_l2']:.8f}；隐藏完整预测 P95 {1000 * h['latency_p95_seconds']:.2f}ms；职责复用 {u['reused_known_applicable']}/{u['known_applicable']}。"
        ]
    lines += [
        "",
        f"事后隐藏最优轮次为 round-{result['posthoc_best_round']:02d}，不能替换已冻结的最终选择。",
        "",
        "## Skill 与实际使用",
        "",
        "逐轮改动依据、实际调用和合理自写原因见 [利用率分析](reviews/UTILIZATION_ANALYSIS.md)。",
        "",
        "Skill承担框架优先评估、每个实质实现决策同时参考Dojo与Web、具体不适配理由及公开扩展边界；Guide保留能力地图，详细API仍在唯一帮助中心。轮间版本、改动理由和摘要见 skill-revisions/；逐项调用证据见 reviews/。",
        "",
        "利用率分母为预先列出的职责中经审查可适用的10项，按职责计一次，不是代码比例、导入次数或Dojo全库覆盖率。一个职责中的部分复用也须阅读详细说明；统计资产沿用round00，不计为每轮重新运行。网络构造/参数统计属于辅助工具，不算复用既有U-Net算法。HDF5来源适配、网络算法和本组未单独执行的后处理不进入这10项分母；这不表示Dojo库内没有网络或后处理能力。合理自写仍留在可适用分母。",
        "",
        "双来源覆盖依据读取正文、实现决策与实际调用的主控审查；直接定位官方文档属于外部资料阅读，不代表全面文献检索。",
        "",
        "## 六场与开发成本",
        "",
        "![六场](results/fields.png)",
        "",
        f"最终隐藏集保持最后帧的主误差为 {final['persistence']['mean_field_relative_l2']:.8f}；最终模型的密度/温度相对保持法改善分别为 {final['per_field_improvement_over_persistence']['rho']} / {final['per_field_improvement_over_persistence']['T']}（比例；null为不可定义）。逐预测步与变化量误差保存在逐窗口结果中。",
        "",
        "![编码成本](results/development-cost.png)",
        "",
        f"研究会话已观测编码区间并集 {cost['time']['coding_seconds'] / 60:.2f} 分钟；已入账编码 token 范围 {cost['tokens']['coding_tokens_lower']}–{cost['tokens']['coding_tokens_upper']}。全部已入账 token {cost['tokens']['total_accounted_tokens']}。范围仅覆盖已报告usage，连接失败未返回usage的消费未知。",
        "",
        f"端到端 {cost['time']['end_to_end_seconds'] / 3600:.2f} 小时，主控调度/审查间隔 {cost['time']['orchestration_wait_seconds'] / 60:.2f} 分钟。训练进程区间含内部验证，内部验证补充记录 {nested['seconds'] / 60:.2f} 分钟；详情与来源见cost.json，不能将其当独立可信时钟。",
        "",
        f"按观测标签的区间并集：训练 {cost['time']['training_seconds'] / 60:.2f} 分钟（仍含上述内部验证）；外部评价 {cost['time']['evaluation_seconds'] / 60:.2f} 分钟；数据准备 {cost['time']['data_preparation_seconds'] / 60:.2f} 分钟；环境 {cost['time']['environment_setup_seconds'] / 60:.2f} 分钟；等待 {cost['time']['idle_or_wait_seconds'] / 60:.2f} 分钟。重叠活动不能直接加总。",
        "",
        f"其中训练活动进程证据支持 {process_seconds / 60:.2f} 分钟；外层工具记录多出的 {(cost['time']['training_seconds'] - process_seconds) / 60:.2f} 分钟不直接认作实际训练，归属保留未知。报告同时保留原始区间与这一细分，不能用训练标签时长冒充净更新耗时。",
        "",
        "按尝试对账见 reviews/usage-attempt-reconciliation.json：中止的CLI没有完整turn合计，其已返回请求usage仍保留在总量中；不删除这部分来强行凑齐两种合计。未返回usage的重试消费仍未知。",
        "",
        "编码按原始活动事件统计，没有使用组内的总时间减训练时间估算。训练失败、重试、准备、环境、评价均留档；活动重叠不相加。主会话最初的审查/改Skill时间和token未独立计量，标为未知，不记零。",
        "",
        "## 隔离与证据边界",
        "",
        "正式会话绑定全新组根；整进程文件边界、公网代理、恢复与子进程预检见 evidence/。隐藏推理在最终选择冻结之后执行，推理执行器无未来真值、无网络，评分器不执行候选代码，结果不写回组目录。公开网络仍不能证明全球公开数据绝对不可获取；下载与来源审计另见最终审计。",
        "",
        "隐藏分片复用前次协议，主会话在旧实验见过该分片结果，因此本报告称复用隐藏集，不宣称全新全局盲测。当前研究Agent未收到旧代码、结果、预处理张量或统计。",
        "",
        f"成本证据状态：{cost['status']}；观察到连接重试 {len(cost['connection_retry_events'])} 次。科学五轮完成与完整成本验收分别陈述，缺失不能追认为零。",
        "",
        "完整数据：results/study.json；原始请求与命令：evidence/sessions/；冻结提交及收据：frozen/、receipts/；利用率审查：reviews/。",
    ]
    (root / "REPORT.md").write_text("\n".join(lines) + "\n")
    write_json(
        root / "state.json",
        {
            "phase": "single_science_complete_evidence_partial",
            "formal_sessions_started": True,
            "scientific_rounds_complete": True,
            "cost_evidence_complete": False,
        },
    )
    return result


def plot(result, output):
    """绘制可导出的静态科学图；保留最终选择标记及token计量缺口。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    rows, selected = result["rounds"], result["final_selection"]["round"]
    x = np.arange(6)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    for key, label in (("validation", "Validation"), ("hidden", "Reused hidden holdout")):
        ys = [r[key]["accuracy"]["mean_field_relative_l2"] for r in rows]
        axes[0].plot(x, ys, "o-", label=label)
        axes[0].scatter(selected, ys[selected], marker="*", s=170, zorder=5)
        axes[1].plot(x, [1000 * r[key]["latency_p95_seconds"] for r in rows], "o-", label=label)
    axes[0].set(
        ylabel="Mean field relative L2 (lower is better)",
        title="Baseline + five optimization rounds",
    )
    axes[1].axhline(50, color="red", linestyle="--", label="50 ms limit")
    axes[1].set(ylabel="Complete 40-frame P95 (ms)", title="Host-to-host, batch 1", ylim=(0, 55))
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xlabel("Round (0 = baseline)")
        ax.grid(alpha=0.25)
        ax.legend()
    fig.savefig(output / "accuracy-latency.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    values = [r["review"]["summary"]["utilization_known"] * 100 for r in rows]
    ax.plot(x, values, "o-", color="#007f73")
    for n, v in enumerate(values):
        s = rows[n]["review"]["summary"]
        ax.annotate(
            f"{s['reused_known_applicable']}/{s['known_applicable']}",
            (n, v),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
        )
    ax.set(
        ylim=(0, 105),
        ylabel="Applicable workflow responsibilities reused (%)",
        xlabel="Round",
        title="Actual Dojo use: direct tools + framework adaptations",
    )
    ax.set_xticks(x)
    ax.grid(alpha=0.25)
    fig.savefig(output / "utilization.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    for field in rows[0]["hidden"]["accuracy"]["per_field_relative_l2"]:
        ax.plot(
            x,
            [r["hidden"]["accuracy"]["per_field_relative_l2"][field] for r in rows],
            "o-",
            label=field,
        )
    ax.set(
        yscale="log",
        xlabel="Round",
        ylabel="Relative L2 (log scale)",
        title="Six fields on reused hidden holdout",
    )
    ax.set_xticks(x)
    ax.grid(alpha=0.25)
    ax.legend(ncol=3)
    fig.savefig(output / "fields.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    axes[0].plot(x, np.cumsum([r["cost"]["observed_seconds"]["coding"] for r in rows]) / 60, "o-")
    lo = (
        np.cumsum(
            [
                r["cost"]["coding_tokens_accounted_lower"]
                if r["cost"]["coding_tokens_accounted_lower"] is not None
                else float("nan")
                for r in rows
            ]
        )
        / 1e6
    )
    hi = (
        np.cumsum(
            [
                r["cost"]["coding_tokens_accounted_upper"]
                if r["cost"]["coding_tokens_accounted_upper"] is not None
                else float("nan")
                for r in rows
            ]
        )
        / 1e6
    )
    axes[1].plot(x, lo, "o-", label="Known coding")
    axes[1].plot(x, hi, "o--", label="Including mixed/unknown activity")
    axes[1].fill_between(x, lo, hi, alpha=0.15)
    axes[0].set(ylabel="Cumulative coding minutes", title="Controller event intervals")
    axes[1].set(
        ylabel="Cumulative accounted tokens (millions)", title="Unreported retry usage excluded"
    )
    axes[1].legend()
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xlabel("Round (final selection excluded)")
        ax.grid(alpha=0.25)
    fig.savefig(output / "development-cost.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    report(parser.parse_args().root)
