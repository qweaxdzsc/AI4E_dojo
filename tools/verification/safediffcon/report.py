"""从已冻结验收结果生成续接报告；不训练、不推理、不选优。"""

import argparse
import hashlib
import json
from pathlib import Path

PAPER = {"burgers": 0.0011, "tokamak": 0.0094}


def build_report(root: Path) -> dict:
    """分别报告工程一致、学习效果、论文口径和累计成本。"""
    work = root / "continuation"
    cases = {}
    for case in ["burgers", "tokamak"]:
        current = json.loads((work / f"{case}-final-acceptance.json").read_text())
        baseline = json.loads((root / "short" / f"{case}-acceptance.json").read_text())
        ledger = json.loads((root / "budget" / f"{case}.json").read_text())
        if (
            current["status"] != "passed"
            or current["samples"] != 50
            or current.get("diagnostic_only", False)
        ):
            raise ValueError("正式报告需要完整50样本验收")
        if any(r["status"] == "running" for r in ledger["runs"]):
            raise ValueError("预算账本仍有运行中任务")
        replay = json.loads((work / f"{case}-installed-replay/replay.json").read_text())
        if replay["status"] != "passed":
            raise ValueError("最终安装包尚未通过重放")
        weights = json.loads((work / f"{case}-reweight-diagnostic.json").read_text())
        before, after = baseline["metrics"], current["metrics"]
        objectives = ["J"] if case == "burgers" else ["J_source_outputs", "J_dataset_targets"]
        differences = {
            key: {
                "baseline": before[key],
                "current": after[key],
                "absolute_change": after[key] - before[key],
                "relative_change_percent": 100 * (after[key] / before[key] - 1),
                "paper_reference": PAPER[case],
                "paper_ratio_reference_only": after[key] / PAPER[case],
            }
            for key in objectives
        }
        rates = {
            key: {
                "baseline": before[key],
                "current": after[key],
                "percentage_point_change": 100 * (after[key] - before[key]),
            }
            for key in after
            if key.startswith("R_")
        }
        cases[case] = {
            "engineering_status": current["status"],
            "reference_scope": current["scope"],
            "shared_boundaries": current["shared_boundaries"],
            "metrics": after,
            "objective_comparison": differences,
            "safety_comparison": rates,
            "paper_reproduction": False,
            "paper_comparable": case == "burgers",
            "paper_boundary": "缩小网络/预算；Tokamak目标来源与时间积分离散归约仍未解决"
            if case == "tokamak"
            else "同定义指标；缩小训练不代表原论文设置复现",
            "accounted_minutes": ledger["seconds"] / 60,
            "remaining_minutes": (10800 - ledger["seconds"]) / 60,
            "budget_passed": ledger["seconds"] <= 10800,
            "freeze": json.loads((work / f"{case}-training-freeze.json").read_text()),
            "acceptance": str(work / f"{case}-final-acceptance.json"),
            "installed_replay": replay,
            "reweight_diagnostic": weights,
        }
    payload = {
        "scope": "code integration continuation within original 180 minute per-case ledgers",
        "cases": cases,
        "sources": {},
    }
    for path in [
        work / "scientific-protocol.md",
        work / "paper.html",
        work / "tests-complete.log",
        work / "public-api-tests.log",
        work / "budget-delivery-tests.log",
    ]:
        payload["sources"][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return payload


def write_report(root: Path) -> Path:
    """写独立交付目录，历史4000步报告保持不变。"""
    payload = build_report(root)
    directory = root / "continuation/delivery"
    directory.mkdir(exist_ok=True)
    (directory / "report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    lines = [
        "# SafeDiffCon 续接实施结果",
        "",
        "本轮复用已集成代码，补独立原定义后训练/适配编排和原 Trainer 恢复连接，并执行冻结预算内的双侧训练及全部50测试样本评价。",
        "",
        "## 两案例结果",
        "",
    ]
    for case, item in payload["cases"].items():
        lines += [
            f"### {case}",
            "",
            f"- 预训练总更新：{item['freeze']['total']}；两轮后训练各320次、DDIM50、校准200、实际适配1次。",
            f"- 工程对照：{item['engineering_status']}；50样本完整评价。",
            f"- 累计核算：{item['accounted_minutes']:.2f}/180分钟；剩余{item['remaining_minutes']:.2f}分钟。",
        ]
        for metric, delta in item["objective_comparison"].items():
            lines += [
                f"- {metric}：原4000步 {delta['baseline']:.10f} → 本次 {delta['current']:.10f}；相对变化 {delta['relative_change_percent']:+.2f}%；对论文参考数值约 {delta['paper_ratio_reference_only']:.2f} 倍。"
            ]
        for metric, delta in item["safety_comparison"].items():
            lines += [
                f"- {metric}：{delta['baseline'] * 100:.5f}% → {delta['current'] * 100:.5f}%，变化 {delta['percentage_point_change']:+.5f} 个百分点。"
            ]
        for check in item["reweight_diagnostic"]["rounds"]:
            lines += [
                f"- 后训练第{check['round'] + 1}轮：Q={check['q']:.8f}，原指数非零权重{check['raw_nonzero']}/{check['count']}；全零后均匀回退={check['uniform_fallback']}。"
            ]
        lines += [f"- 论文边界：{item['paper_boundary']}。", ""]
    lines += [
        "## 验收边界",
        "",
        "- 独立原 Trainer 预训练、原校准类及原后训练/适配方法与 Dojo 比较；双方共享准备数组、批次流、检查点容器、响应求解与指标/存储。不能说两套实现没有共享边界。",
        "- 历史诊断的4样本结果只验证数值；本报告仅使用冻结配置的最终50样本结果，未按测试成绩选优。",
        "- 所有失败重试沿用原账本；共享验证保守预留与实测计算在账本中分别记录，不把预留说成实测训练。",
        "- 已有可复制模板及三种扩展按相关代码未变的来源证据复用；新增配置与安装另验。预训练恢复与完整阶段交接有效，不保证后训练任意轮内恢复。",
        "- 最新独立安装包57项圈定测试与9项公开接口/架构测试通过；安装包逐值重放最终控制、预测、校准值及适配权重，复用响应的依据逐案例保存。",
        "- Tokamak仍分别报告源码目标和数据目标，论文达标口径未解决；完整论文规模未执行。",
        "- Burgers两轮原指数权重均下溢为零，按原算法回退等权，因此本次后训练没有发挥样本安全重加权；这是已证实的数值状态，不足以单独解释全部精度差距。未为改善测试成绩修改原算术。",
        "",
        "依据：同目录report.json、上级scientific-protocol.md、*-final-acceptance.json，以及原delivery/REPORT.md。",
    ]
    result = directory / "REPORT.md"
    result.write_text("\n".join(lines) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    print(write_report(parser.parse_args().root))
