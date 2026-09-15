"""按已提交完整预测汇总文献参数验证，未完成或精度差距均如实保留。"""

import argparse
import json
import os
import statistics
import time
from pathlib import Path

from compare import compare

CASES = ("convection_diffusion", "neumann_diffusion", "advection", "burgers", "diffusion_trapezoid")


def process_alive(pid):
    """只读检查本批已启动进程，不发送终止信号或重启训练。"""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def build(root, output):
    """重算完整实例对照；当前报告允许部分结果但不会标为验收通过。"""
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    for case in CASES:
        dojo = root / case / "predictions_paper_v3"
        reference = root / "reference_paper_v3" / case
        row = {"case": case}
        if not (dojo / "predictions.json").exists() or not (reference / "reference.json").exists():
            row.update(status="pending", reason="完整 Dojo 或参考预测尚未提交")
        else:
            # compare 本身拒绝覆盖历史结果；本次报告先写独立临时比较，再原子提交。
            temporary = output / f".{case}.json"
            if temporary.exists():
                raise FileExistsError(temporary)
            try:
                result = compare(dojo, reference, temporary)
            except (ValueError, KeyError, FileNotFoundError) as exc:
                row.update(status="incomparable", reason=str(exc))
            else:
                temporary.replace(output / f"{case}.json")
                row.update(
                    status="compared",
                    epochs=result["epochs"],
                    updates=result["updates"],
                    test_samples=len(result["samples"]),
                    dojo_mean_relative_l2=statistics.mean(s["dojo"] for s in result["samples"]),
                    reference_mean_relative_l2=statistics.mean(
                        s["reference"] for s in result["samples"]
                    ),
                )
        cases.append(row)
    result = {
        "status": "partial"
        if any(r["status"] != "compared" for r in cases)
        else "comparisons_complete",
        "precision_acceptance": "not_established",
        "cases": cases,
    }
    lines = [
        "# PI-BSNet 文献参数验证",
        "",
        "这是当前已提交结果的汇总。完整运行与精度复现分别验收；不通过调参掩盖差距。",
        "",
        "文献未给出的参数由锁定源码补足。对照共享修正物理数据，原分支保留其导数和条件算法；不是原数据生成流程逐元素复现。",
        "",
    ]
    for row in cases:
        lines += [f"## {row['case']}", ""]
        if row["status"] == "compared":
            lines += [
                f"{row['epochs']}轮，{row['updates']}次更新，全部{row['test_samples']}个测试实例。平均相对L2：Dojo {row['dojo_mean_relative_l2']:.8g}；原分支 {row['reference_mean_relative_l2']:.8g}。",
                "",
            ]
        else:
            lines += [f"{row['status']}：{row['reason']}。", ""]
    lines += [
        "## 结论边界",
        "",
        "Neumann 正确物理导数版本与独立原生PyTorch目标/梯度吻合，但原文献参数下精度未复现。CD的自由控制系数和初值施加也与原分支不同，必须披露。其他案例未提交完整结果时不推断精度。",
        "",
        "梯形：文献50训练实例、控制网格100×20×20、PDE权重0.001，训练采用近似Eq.84；真值使用完整变换。Burgers保留已披露的符号与周期网格修正。",
        "",
    ]
    (output / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (output / "report.md").write_text("\n".join(lines))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--wait-for-pids", nargs="*", type=int, default=[])
    args = parser.parse_args()
    deadline = time.monotonic() + 24 * 60 * 60
    while any(process_alive(pid) for pid in args.wait_for_pids):
        if time.monotonic() >= deadline:
            break
        time.sleep(30)
    result = build(args.root, args.output)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    if result["status"] != "comparisons_complete":
        raise SystemExit(1)
