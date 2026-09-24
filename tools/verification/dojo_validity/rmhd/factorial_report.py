"""四会话只读汇总：科学曲线、成本区间与有证据的代码复用，不生成缺失结果。"""

import argparse
import csv
import math
from pathlib import Path

from ..io import inside, read_json, write_json
from ..ledger import union_seconds
from .accounting import collect
from .factorial import verify_frozen
from .factorial_materials import CELLS
from .report import training_diagnostics

GROUP_LABELS = {
    "BP": "BP：给定U-Net·白板",
    "BD": "BD：给定U-Net·Dojo",
    "NP": "NP：自主选模·白板",
    "ND": "ND：自主选模·Dojo",
}
PLOT_CAPTIONS = {
    "accuracy": "越低越好；左为开发时可见的验证集，右为全部最终方案锁定后才评分的隐藏测试集。\n黑虚线为保持最后一帧的参考预测；连续五轮属于同一会话，不是五次独立实验。",
    "latency": "每次输入10帧，输出完整未来40帧；包含前后处理、设备传输与主控通信。\n展示三批P95的中位数，红线为50毫秒门槛；不包含模型冷启动和磁盘归档。",
    "coding-time": "仅累计第0～5轮可观察编码活动：规划、检索、阅读、修改与调试；训练、准备及未知活动另列。\n包含模型生成与工具响应的墙钟，不能视为纯思考时间；最终选择等未归轮成本另计。",
    "coding-tokens": "实线为明确编码请求的token，虚线再包含可能属于编码的混合/未知请求，阴影不是置信区间。\n累计第0～5轮输入＋输出；缓存输入已含在内。未报告请求及最终选择等未归轮成本不在曲线中。",
    "coding-per-round": "每个点只表示本轮，不是累计值；左图单位为分钟，右图单位为token。\n右图阴影为已报告请求的分类上下界；训练、准备及未能确认的活动不冒充编码时间。",
    "relative-improvement": "改善率＝1－本轮误差/本组初始误差，越高越好；0%表示没有改善。\n各组起点可能不同，改善率不能替代绝对误差；左为验证，右为隐藏测试。",
    "six-fields": "上排为验证集，下排为隐藏测试；六个字段分别计算完整40帧相对L2，越低越好。\n各面板纵轴范围不同，请读数值，不按曲线的视觉高度跨字段比较。",
    "dojo-reuse": "左列数用了多少类适用功能；中列数本地代码中已核验原样保留的案例源码；右列展开实际调用的Dojo函数体。\n上排为相关准备/训练/评价流程，下排只看加载与最终推理。中列是来源下界，0%不等于从未复制案例。\n右列包含被调用函数内未执行的分支，既不是逐行执行覆盖率，也不是节省的手写工作量。",
    "implementation-volume": "L＝相关本地有效行，D＝实际调用的Dojo函数体及保留案例源码；右列为L＋D－同源交集。\n排除公共基线、纯导入、未调用定义和第三方库内部；不同组的功能范围不同，不能直接据此计算节省比例。",
}


def chinese_plot_style():
    """选择已安装中文字体，让静态图可独立阅读；不下载或修改系统字体。"""
    import matplotlib
    from matplotlib import font_manager

    families = {f.name for f in font_manager.fontManager.ttflist}
    selected = next(
        (
            f
            for f in (
                "Arial Unicode MS",
                "Noto Sans CJK SC",
                "Hiragino Sans GB",
                "Microsoft YaHei",
                "SimHei",
            )
            if f in families
        ),
        None,
    )
    if selected:
        matplotlib.rcParams["font.sans-serif"] = [selected, "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def plot_caption(fig, name):
    """每幅导出图内直接附中文口径，避免离开报告就失去解释。"""
    fig.text(0.5, 0.055, PLOT_CAPTIONS[name], ha="center", va="center", fontsize=8)
    fig.text(
        0.5,
        0.008,
        "来源：冻结RMHD第0～5轮记录；0为初始方案，星号为最终选择。各组缩写含义见图例。",
        ha="center",
        fontsize=8,
    )


def round_cost(cost, number):
    """按原始请求与活动归轮；未知token保持空值，混合请求给上下界。"""
    timing, tokens = cost.get("time"), cost.get("tokens")
    intervals = (timing or {}).get("intervals", [])
    seconds = {
        phase: union_seconds(
            [
                (e["start"], e["end"])
                for e in intervals
                if e.get("round") == number and e["phase"] == phase
            ]
        )
        if timing
        else None
        for phase in ("coding", "training", "evaluation", "data_preparation", "environment_setup")
    }
    known = [
        (e["start"], e["end"])
        for e in intervals
        if e.get("round") == number and e["phase"] in seconds
    ]
    unknown = [
        (e["start"], e["end"])
        for e in intervals
        if e.get("round") == number and e["phase"] == "unclassified"
    ]
    seconds["unclassified"] = (
        union_seconds(known + unknown) - union_seconds(known) if timing else None
    )
    requests = [r for r in (tokens or {}).get("raw_requests", []) if r.get("round") == number]
    known = [
        r
        for r in requests
        if r.get("input_tokens") is not None and r.get("output_tokens") is not None
    ]
    amount = lambda r: r["input_tokens"] + r["output_tokens"]
    lo = sum(amount(r) for r in known if r["phase"] == "coding")
    hi = lo + sum(amount(r) for r in known if r["phase"] in {"mixed", "unclassified"})
    return {
        "seconds": seconds,
        "coding_tokens_lower": lo if requests else None,
        "coding_tokens_upper": hi if requests and len(known) == len(requests) else None,
        "total_accounted_tokens": sum(map(amount, known)) if requests else None,
        "missing_fields_requests": len(requests) - len(known),
    }


def descriptive_effects(groups):
    """2×2终点对比与交互，仅描述四条轨迹；不生成显著性或置信区间。"""
    effects = {}
    for left, right in (("BD", "BP"), ("ND", "NP"), ("BP", "NP"), ("BD", "ND")):
        a, b = groups[left]["final"], groups[right]["final"]
        ae = (a.get("accuracy") or {}).get("mean_field_relative_l2")
        be = (b.get("accuracy") or {}).get("mean_field_relative_l2")
        eligible = bool(a.get("eligible") and b.get("eligible"))
        effects[f"{left}/{right}"] = {
            "both_eligible": eligible,
            "log_error_ratio": math.log(ae / be)
            if eligible and ae is not None and be is not None and ae > 0 and be > 0
            else None,
            "accuracy_difference": ae - be if ae is not None and be is not None else None,
            "note": "Raw difference remains descriptive if either candidate fails latency.",
        }
    given = effects["BD/BP"]["log_error_ratio"]
    open_model = effects["ND/NP"]["log_error_ratio"]
    effects["interaction_open_minus_given"] = {
        "log_error_ratio_difference": open_model - given
        if open_model is not None and given is not None
        else None,
        "formula": "log(ND/NP) - log(BD/BP)",
        "scope": "descriptive; four sessions, no independent replicates",
    }
    return effects


def classified_queue_gaps(timing):
    """调度间隙先扣除未知活动观察范围，再与其他组的执行窗口求交。"""
    intervals = timing.get("intervals", [])
    unknown = [e for e in intervals if e["phase"] == "unclassified"]
    result = []
    for event in intervals:
        if event["source"] != "controller scheduling gap":
            continue
        pieces = [(event["start"], event["end"])]
        for item in unknown:
            pieces = [
                (a, b)
                for start, stop in pieces
                for a, b in (
                    (start, min(stop, item["start"])),
                    (max(start, item["end"]), stop),
                )
                if a < b
            ]
        result.extend(pieces)
    return result


def summarize(root):
    """只在所有隐藏结果已交付后出完整科学报告，审计缺项明确保留。"""
    root = Path(root)
    if read_json(root / "state.json")["phase"] not in {
        "hidden_evaluated_audit_pending",
        "factorial_reported",
    }:
        raise ValueError("四组隐藏评价未完成")
    groups, costs, flat = {}, {}, []
    for group in CELLS:
        costs[group] = collect(root, group)
        final = read_json(root / f"final-selections/{group}.json")
        rounds = []
        for n in range(6):
            verify_frozen(root, group, n)
            paths = sorted(
                (root / f"validation/{group}/round-{n:02d}").glob("*/result.json"),
                key=lambda p: p.stat().st_mtime,
            )
            validation = next(
                read_json(p) for p in reversed(paths) if read_json(p)["status"] == "evaluated"
            )
            hidden = read_json(root / f"hidden-results/{group}/round-{n:02d}/result.json")
            receipt = read_json(root / f"receipts/{group}/round-{n:02d}.json")
            method = receipt["source_manifest"]["method"]
            try:
                path = inside(root / f"frozen/{group}/round-{n:02d}", method)
                if path.is_file():
                    method = path.read_text()
            except (ValueError, OSError):
                pass
            usage_file = root / f"reuse-audit/{group}/round-{n:02d}/summary.json"
            usage = (
                read_json(usage_file)
                if usage_file.exists()
                else {"status": "missing", "reason": "trace and provenance review pending"}
            )
            cost = round_cost(costs[group], n)
            row = {
                "round": n,
                "final_selected": n == final["round"],
                "method": method,
                "dojo_usage_declaration": receipt["source_manifest"]["dojo_usage"],
                "validation": validation,
                "hidden": hidden,
                "cost": cost,
                "reuse": usage,
                "training": training_diagnostics(root, group, n, receipt),
            }
            rounds.append(row)
            flat.append(
                {
                    "group": group,
                    "round": n,
                    "final_selected": row["final_selected"],
                    "validation_error": validation["accuracy"]["mean_field_relative_l2"],
                    "hidden_error": (hidden.get("accuracy") or {}).get("mean_field_relative_l2"),
                    "hidden_eligible": hidden.get("eligible"),
                    "hidden_p95_ms": 1000 * hidden["latency_p95_seconds"]
                    if hidden.get("latency_p95_seconds")
                    else None,
                    "coding_seconds": cost["seconds"]["coding"],
                    "unclassified_seconds": cost["seconds"]["unclassified"],
                    "coding_tokens_lower": cost["coding_tokens_lower"],
                    "coding_tokens_upper": cost["coding_tokens_upper"],
                    "reuse_status": usage["status"],
                }
            )
        eligible = [
            r for r in rounds if r["hidden"].get("eligible") and r["hidden"].get("accuracy")
        ]
        groups[group] = {
            "rounds": rounds,
            "final_selection": final,
            "final": rounds[final["round"]]["hidden"],
            "round_05": rounds[5]["hidden"],
            "posthoc_best_eligible_round": min(
                eligible, key=lambda r: r["hidden"]["accuracy"]["mean_field_relative_l2"]
            )["round"]
            if eligible
            else None,
        }
    for group, cost in costs.items():
        if not cost.get("time"):
            continue
        gaps = classified_queue_gaps(cost["time"])
        cost["time"]["executor_queue_seconds"] = union_seconds(
            [
                (max(start, a), min(stop, b))
                for start, stop in gaps
                for other, c in costs.items()
                if other != group
                for a, b in c.get("execution_windows", [])
                if max(start, a) < min(stop, b)
            ]
        )
    effects = descriptive_effects(groups)
    review_path = root / "evidence/final-review.json"
    review = read_json(review_path) if review_path.exists() else {}
    organization_path = root / "evidence/organization-cost.json"
    organization = (
        read_json(organization_path) if organization_path.exists() else {"status": "missing"}
    )
    result = {
        "groups": groups,
        "costs": costs,
        "paired_effects": effects,
        "science_complete": all(
            r["hidden"]["status"] == "evaluated" for g in groups.values() for r in g["rounds"]
        ),
        "cost_complete": all(c["status"] == "accounted" for c in costs.values())
        and review.get("phase_separation_confirmed") is True
        and review.get("request_retry_coverage_confirmed") is True,
        "final_review": review,
        "organization_cost": organization,
        "organization_cost_complete": organization.get("status") == "complete",
        "reuse_audit_complete": all(
            r["reuse"]["status"] == "complete" for g in groups.values() for r in g["rounds"]
        ),
        "limits": [
            "Four trajectories, no independent replicates or significance claims",
            "Historical deterministic holdout reused; locally hidden from current sessions",
            "Public-data download audit cannot inspect TLS payloads",
            "Expanded code volume is not labor savings or minimum standalone implementation",
        ],
    }
    out = root / "results"
    write_json(out / "comparison.json", result)
    write_json(out / "cost.json", costs)
    write_json(out / "accuracy.json", groups)
    with (out / "rounds.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    plot(groups, out)
    plot_details(groups, out)
    lines = [
        "# RMHD 四会话实验报告",
        "",
        "四条研究轨迹分别报告；不把五轮当独立重复。",
        "",
        f"科学完成：{result['science_complete']}；实验组成本证据完整：{result['cost_complete']}；组织成本完整：{result['organization_cost_complete']}；复用审计完整：{result['reuse_audit_complete']}。",
        "",
    ]
    for g, data in groups.items():
        final = data["final"]
        error = (final.get("accuracy") or {}).get("mean_field_relative_l2")
        lines += [
            f"- {g}：最终round-{data['final_selection']['round']:02d}，隐藏误差{error}，50ms合格{final.get('eligible')}。"
        ]
    for name in (
        "accuracy",
        "latency",
        "coding-time",
        "coding-tokens",
        "coding-per-round",
        "relative-improvement",
        "six-fields",
        "dojo-reuse",
        "implementation-volume",
    ):
        lines += ["", f"![{name}](results/{name}.png)", "", PLOT_CAPTIONS[name].replace("\n", " ")]
    lines += [
        "",
        "逐轮方法、六场指标、全部尝试成本与代码审计见 results/comparison.json；未知数据未填零。隐藏事后最优仅作描述，不替换最终选择。",
        "内部预实验、隔离诊断和被作废的基础设施尝试单列为组织成本，不并入本次四组轨迹；未对账的主控成本保持未知。",
    ]
    (root / "REPORT.md").write_text("\n".join(lines) + "\n")
    write_json(
        root / "state.json",
        {
            "phase": "factorial_reported",
            "formal_sessions_started": True,
            "science_complete": result["science_complete"],
            "cost_complete": result["cost_complete"],
            "reuse_audit_complete": result["reuse_audit_complete"],
        },
    )
    return result


def detail_series(groups):
    """导出细图对应数据；审计未交付的分子分母为None，不推断为零。

    reuse summary包含responsibilities、whole_pipeline、prediction三个独立范围。
    两个代码范围使用factorial_audit.reuse_sets的输出，职责使用responsibilities输出。
    """
    result = []
    for group, data in groups.items():
        for row in data["rounds"]:
            usage = row.get("reuse") or {}
            roles = usage.get("responsibilities") or {}
            record = {
                "group": group,
                "round": row["round"],
                "final_selected": row["final_selected"],
                "coding_seconds": row["cost"]["seconds"]["coding"],
                "unclassified_seconds": row["cost"]["seconds"].get("unclassified"),
                "coding_tokens_lower": row["cost"]["coding_tokens_lower"],
                "coding_tokens_upper": row["cost"]["coding_tokens_upper"],
                "responsibility_numerator": roles.get("adopted_executed"),
                "responsibility_denominator": roles.get("known_applicable"),
                "responsibility_lower": roles.get("lower"),
                "responsibility_upper": roles.get("upper"),
                "audit_status": usage.get("status", "missing"),
            }
            for scope in ("whole_pipeline", "prediction"):
                values = usage.get(scope) or {}
                for key in (
                    "local_implementation_sloc",
                    "dojo_copied_retained_sloc",
                    "local_source_reuse_ratio",
                    "expanded_dojo_sloc",
                    "expanded_implementation_sloc",
                    "expanded_dojo_reuse_ratio",
                ):
                    record[f"{scope}_{key}"] = values.get(key)
            for split in ("validation", "hidden"):
                accuracy = row[split].get("accuracy") or {}
                initial = (data["rounds"][0][split].get("accuracy") or {}).get(
                    "mean_field_relative_l2"
                )
                current = accuracy.get("mean_field_relative_l2")
                record[f"{split}_relative_reduction_from_initial"] = (
                    1 - current / initial
                    if initial is not None and initial > 0 and current is not None
                    else None
                )
                for field in ("Psi", "u", "zj", "omega", "rho", "T"):
                    record[f"{split}_{field}"] = (accuracy.get("per_field_relative_l2") or {}).get(
                        field
                    )
            result.append(record)
    return result


def plot_details(groups, output):
    """逐轮成本、六场误差和双范围复用图；缺失保留断点，附可复算CSV。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    chinese_plot_style()
    rows = detail_series(groups)
    with (output / "detail-series.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    chinese_plot_style()
    colors = {"BP": "#64748b", "BD": "#2563eb", "NP": "#a16207", "ND": "#16a34a"}

    def values(records, key):
        return np.array([r[key] if r[key] is not None else np.nan for r in records])

    specs = {
        "coding-per-round": (1, 2),
        "relative-improvement": (1, 2),
        "six-fields": (2, 6),
        "dojo-reuse": (2, 3),
        "implementation-volume": (2, 3),
    }
    for name, (nr, nc) in specs.items():
        fig, axes = plt.subplots(nr, nc, figsize=(5 * nc, 4.2 * nr + 0.6), squeeze=False)
        for group in groups:
            records = [r for r in rows if r["group"] == group]
            x = [r["round"] for r in records]
            color = colors[group]
            for i in range(nr):
                for j in range(nc):
                    ax = axes[i, j]
                    if name == "dojo-reuse" and i == 1 and j == 0:
                        ax.axis("off")
                        if group == next(iter(groups)):
                            ax.text(
                                0.02,
                                0.95,
                                "三个百分比回答不同问题\n\n左：已有功能，实际用了几类？\n中：本地源码，原样保留了多少？\n右：展开库内部后，Dojo占多少？\n\n三个分母不同，不能相互比较。\n职责阴影表示适用性尚有未知，\n不是统计置信区间。\n\nBD推理为0%不代表训练没用Dojo。",
                                va="top",
                                fontsize=10,
                            )
                        continue
                    upper = None
                    if name == "coding-per-round":
                        key = "coding_seconds" if j == 0 else "coding_tokens_lower"
                        title = (
                            "本轮可观察编码时间（分钟）"
                            if j == 0
                            else "本轮编码token（分类上下界）"
                        )
                        y = values(records, key) / (60 if j == 0 else 1)
                        if j == 1:
                            upper = values(records, "coding_tokens_upper")
                    elif name == "relative-improvement":
                        split = ("validation", "hidden")[j]
                        y = values(records, f"{split}_relative_reduction_from_initial") * 100
                        title = (
                            "验证集" if split == "validation" else "隐藏测试集"
                        ) + "：相对本组初始点的改善"
                        ax.axhline(0, color="gray", linewidth=0.5)
                    elif name == "six-fields":
                        field = ("Psi", "u", "zj", "omega", "rho", "T")[j]
                        split = ("validation", "hidden")[i]
                        y = values(records, f"{split}_{field}")
                        title = (
                            "验证" if split == "validation" else "隐藏测试"
                        ) + f"：{field} 相对L2"
                    else:
                        scope = ("whole_pipeline", "prediction")[i]
                        if name == "dojo-reuse":
                            keys = (
                                "responsibility_lower",
                                f"{scope}_local_source_reuse_ratio",
                                f"{scope}_expanded_dojo_reuse_ratio",
                            )
                            title = (
                                "适用功能采用率",
                                "原样保留案例源码占比（下界）",
                                "展开后的Dojo实现量占比",
                            )[j]
                            y = values(records, keys[j]) * 100
                            if j == 0:
                                upper = values(records, "responsibility_upper") * 100
                                title += ""
                            ax.set_ylim(0, 105)
                            ax.set_ylabel("占比（%）；缺失表示无证据")
                        else:
                            key = (
                                "local_implementation_sloc",
                                "expanded_dojo_sloc",
                                "expanded_implementation_sloc",
                            )[j]
                            y = values(records, f"{scope}_{key}")
                            title = (
                                "本地相关代码 L",
                                "调用的Dojo代码 D",
                                "去重后的总代码量",
                            )[j]
                            ax.set_ylabel("有效源码行数")
                        title = (
                            ("整流程" if scope == "whole_pipeline" else "最终推理") + "：" + title
                        )
                    ax.plot(x, y, "o-", color=color, label=GROUP_LABELS[group])
                    if upper is not None:
                        ax.fill_between(x, y, upper, color=color, alpha=0.15)
                        ax.plot(x, upper, ":", color=color)
                    for n, record in enumerate(records):
                        if record["final_selected"] and np.isfinite(y[n]):
                            ax.scatter(x[n], y[n], marker="*", s=150, c=color)
                    ax.set_title(title, fontsize=9)
                    ax.set_xlabel("优化轮次（0＝初始方案）")
                    if name == "coding-per-round":
                        ax.set_ylabel("可观察分钟数" if j == 0 else "已报告token数")
                    elif name == "relative-improvement":
                        ax.set_ylabel("误差降低比例（%）")
                    elif name == "six-fields":
                        ax.set_ylabel("相对L2误差（无量纲）")
                    ax.grid(alpha=0.2)
        for ax in axes.flat:
            if ax.axison:
                ax.legend(fontsize=8)
        plot_caption(fig, name)
        fig.tight_layout(rect=(0, 0.13, 1, 1))
        fig.savefig(output / f"{name}.png", dpi=170)
        plt.close(fig)


def plot(groups, output):
    """静态科学图保留失败断点、超延迟标记及最终选择；token绘上下界。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    chinese_plot_style()
    colors = {"BP": "#64748b", "BD": "#2563eb", "NP": "#a16207", "ND": "#16a34a"}
    for name in ("accuracy", "latency", "coding-time", "coding-tokens"):
        fig, axes = plt.subplots(
            1, 2 if name == "accuracy" else 1, figsize=(13, 5.6), squeeze=False
        )
        for group, data in groups.items():
            rounds = data["rounds"]
            x = np.arange(6)
            color = colors[group]
            selected = data["final_selection"]["round"]
            for idx, ax in enumerate(axes[0]):
                if name == "accuracy":
                    split = "validation" if idx == 0 else "hidden"
                    y = [
                        (r[split].get("accuracy") or {}).get("mean_field_relative_l2", np.nan)
                        for r in rounds
                    ]
                    ax.set_title(
                        ("验证集" if split == "validation" else "隐藏测试集")
                        + "：六场平均相对L2误差"
                    )
                    for n, r in enumerate(rounds):
                        if not r[split].get("eligible"):
                            ax.scatter(n, y[n], marker="x", s=95, c=color)
                    ax.scatter(selected, y[selected], marker="*", s=150, c=color)
                elif name == "latency":
                    y = [r["hidden"].get("latency_p95_seconds", np.nan) * 1000 for r in rounds]
                    ax.set_title("完整40帧预测延迟：P95（毫秒）")
                elif name == "coding-time":
                    y = (
                        np.cumsum(
                            [
                                r["cost"]["seconds"]["coding"]
                                if r["cost"]["seconds"]["coding"] is not None
                                else np.nan
                                for r in rounds
                            ]
                        )
                        / 60
                    )
                    ax.set_title("累计可观察编码时间（分钟）")
                else:
                    y = np.cumsum(
                        [
                            r["cost"]["coding_tokens_lower"]
                            if r["cost"]["coding_tokens_lower"] is not None
                            else np.nan
                            for r in rounds
                        ]
                    )
                    upper = np.cumsum(
                        [
                            r["cost"]["coding_tokens_upper"]
                            if r["cost"]["coding_tokens_upper"] is not None
                            else np.nan
                            for r in rounds
                        ]
                    )
                    ax.fill_between(x, y, upper, color=color, alpha=0.16)
                    ax.plot(x, upper, color=color, linestyle=":")
                    ax.set_title("累计编码token（分类上下界）")
                ax.plot(x, y, "o-", label=GROUP_LABELS[group], color=color)
                ax.set_xlabel("优化轮次（0＝初始方案）")
                ax.set_ylabel(
                    {
                        "accuracy": "相对L2误差（无量纲）",
                        "latency": "毫秒",
                        "coding-time": "可观察分钟数",
                        "coding-tokens": "已报告token数",
                    }[name]
                )
                ax.grid(alpha=0.2)
        for ax in axes[0]:
            if name == "latency":
                ax.axhline(50, color="#dc2626", linestyle="--", label="50毫秒准入门槛")
            ax.legend(fontsize=8)
        if name == "accuracy":
            for idx, ax in enumerate(axes[0]):
                split = "validation" if idx == 0 else "hidden"
                persistence = next(
                    (
                        r[split]["persistence"]["mean_field_relative_l2"]
                        for g in groups.values()
                        for r in g["rounds"]
                        if r[split].get("persistence")
                    ),
                    None,
                )
                if persistence is not None:
                    ax.axhline(
                        persistence, color="black", linestyle="--", label="保持最后一帧：参考预测"
                    )
                    ax.legend(fontsize=8)
        plot_caption(fig, name)
        fig.tight_layout(rect=(0, 0.13, 1, 1))
        fig.savefig(output / f"{name}.png", dpi=170)
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    summarize(parser.parse_args().root)
