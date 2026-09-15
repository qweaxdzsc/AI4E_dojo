"""重新读取六组完整实验的权重、数据和预测，输出可审查比较证据。"""

import argparse
import html
import json
import pickle
from pathlib import Path

import numpy as np
import torch
from neumann_advection_trials import VARIANTS, sha, write


def equal_tree(a, b):
    """递归核验原数据和初始权重，不以种子相同代替逐值相同。"""
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and np.array_equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal_tree(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(equal_tree(x, y) for x, y in zip(a, b))
    return a == b


def verify(root):
    """仅完整预算和全测试输出通过后发布报告；原指标和FP64重算分别记录。"""
    protocol = json.loads((root / "protocol.json").read_text())
    baseline = Path(protocol["baseline"])
    rows = []
    for variant, (case, physical, instance, epochs, updates) in VARIANTS.items():
        run = root / variant / case
        state = json.loads((run / "status.json").read_text())
        result = json.loads((run / "result.json").read_text())
        if (
            state["status"] != "complete"
            or result["epochs_completed"] != epochs
            or result["updates"] != updates
        ):
            raise ValueError(f"预算未完成：{variant}")
        history = [
            json.loads(line) for line in (run / "logs/epochs.jsonl").read_text().splitlines()
        ]
        if len(history) != epochs or history[-1]["updates"] != updates:
            raise ValueError(f"逐轮记录不完整：{variant}")
        if not np.isfinite([r["loss"] for r in history]).all():
            raise ValueError(f"损失非有限：{variant}")
        initial = torch.load(run / "checkpoints/initial.pt", weights_only=False)["model"]
        reference = torch.load(baseline / case / "checkpoints/initial.pt", weights_only=False)[
            "model"
        ]
        if not equal_tree(initial, reference):
            raise ValueError(f"初始化与原基线不同：{variant}")
        for name in (
            ["checkpoints/dataset_seed42.pkl"]
            if case == "neumann_diffusion"
            else ["data/train.pt", "data/test.pt"]
        ):
            if name.endswith(".pkl"):
                with (run / name).open("rb") as f:
                    a = pickle.load(f)
                with (baseline / case / name).open("rb") as f:
                    b = pickle.load(f)
            else:
                a = torch.load(run / name, weights_only=False)
                b = torch.load(baseline / case / name, weights_only=False)
            if not equal_tree(a, b):
                raise ValueError(f"数据与原基线不同：{variant}/{name}")
        predictions = sorted((run / "predictions").glob("test-*.npz"))
        if len(predictions) != (10 if case == "neumann_diffusion" else 30):
            raise ValueError(f"预测缺失：{variant}")
        errors, max_reference_difference = [], 0.0
        amplitude_ratios, initial_errors = [], []
        for file in predictions:
            with np.load(file) as item, np.load(baseline / case / "predictions" / file.name) as old:
                p, t = item["prediction"].astype("float64"), item["target"].astype("float64")
                if (
                    p.shape != t.shape
                    or not np.isfinite(p).all()
                    or not np.array_equal(item["target"], old["target"])
                ):
                    raise ValueError(f"预测、真值或身份不一致：{file}")
                errors.append(float(np.linalg.norm(p - t) / np.linalg.norm(t)))
                amplitude_ratios.append(float(np.linalg.norm(p) / np.linalg.norm(t)))
                initial_errors.append(float(np.linalg.norm(p[0] - t[0]) / np.linalg.norm(t[0])))
                max_reference_difference = max(
                    max_reference_difference, float(np.max(np.abs(p - old["prediction"])))
                )
        if not np.isclose(np.mean(errors), result["mean_relative_l2"], rtol=1e-5, atol=1e-8):
            raise ValueError(f"原评价与完整场重算不一致：{variant}")
        last = torch.load(run / "checkpoints/last.pt", weights_only=False)
        if last["updates"] != updates or last["epochs_completed"] != epochs:
            raise ValueError(f"检查点预算缺损：{variant}")
        if not all(torch.isfinite(t).all() for t in last["model"].values()):
            raise ValueError(f"检查点非有限：{variant}")
        row = {
            "variant": variant,
            "case": case,
            "physical": physical,
            "instance_updates": instance,
            "epochs": epochs,
            "updates": updates,
            "mean_relative_l2": float(np.mean(errors)),
            "std_relative_l2": float(np.std(errors)),
            "per_sample": errors,
            "source_metric": result["mean_relative_l2"],
            "mean_predicted_to_true_norm": float(np.mean(amplitude_ratios)),
            "mean_initial_relative_l2": float(np.mean(initial_errors)),
            "source_prediction_max_difference": max_reference_difference,
            "dataset_and_initial_exact": True,
            "checkpoint_sha256": sha(run / "checkpoints/last.pt"),
            "seconds": state["elapsed_seconds"],
        }
        if variant in ["neumann_source_epoch", "advection_source"]:
            old = torch.load(baseline / case / "checkpoints/last.pt", weights_only=False)["model"]
            row["source_final_weights_exact"] = equal_tree(last["model"], old)
        rows.append(row)
    write(
        root / "reports/verified_evidence.json",
        {"status": "complete", "rows": rows, "protocol": protocol},
    )
    lines = [
        "# Neumann 与 Advection：迁移前六组完整测试",
        "",
        "所有结果均为独立验证脚本结果，尚未迁移到 Dojo。原数据和初权重与锁定原基线逐值核验；保持原轮数、权重、学习率及测试名单。",
        "",
        "论文 Neumann 平均相对 L2 为 0.01932；Advection 为 0.1444 ± 0.1352。真值分别为解析扩散解与周期平移正弦解。以下误差从保存的完整场以 FP64 重新计算，越低越好。",
        "",
    ]
    for r in rows:
        lines += [
            f"## {r['variant']}",
            "",
            f"平均相对 L2：**{r['mean_relative_l2']:.10f}**；测试实例标准差 {r['std_relative_l2']:.10f}。",
            f"完整预算：{r['epochs']}轮 / {r['updates']}更新。数据与初权重逐值相同。",
            f"预测/真值场范数之比均值：{r['mean_predicted_to_true_norm']:.6f}；初始时间面相对L2均值：{r['mean_initial_relative_l2']:.6f}。",
            f"相对旧原基线完整预测最大差异：{r['source_prediction_max_difference']:.10g}。",
            "",
        ]
    values = {r["variant"]: r["mean_relative_l2"] for r in rows}
    lines += [
        "## 本轮能支持的判断",
        "",
        (
            f"Neumann 原导数的整轮/逐实例结果分别为 {values['neumann_source_epoch']:.8f} / {values['neumann_source_instance']:.8f}；"
            f"物理导数分别为 {values['neumann_physical_epoch']:.8f} / {values['neumann_physical_instance']:.8f}。"
            "若两种原导数更新均接近论文而物理组均偏离，说明更新分组不是物理组失败的充分解释。"
        ),
        (
            f"Advection 原导数为 {values['advection_source']:.8f}，物理导数为 {values['advection_physical']:.8f}。"
            "本轮两组都保留同一个首行插值初值；它们的差别不能归咎于 Dojo 旧 lifting。"
        ),
        (
            "Neumann 原参数导数没有物理尺度换算且二阶递推非标准；Advection 时间/空间尺度不同，换算后改变两项的相对比例。"
            "沿用原损失权重时，这会改变优化器面对的物理项与数据项平衡，而不是只改显示单位。"
        ),
        (
            "迁移建议需同时考虑目标：复刻源码训练路径使用原组；解释论文 Algorithm1 的 Neumann 更新可参考原导数逐实例组。"
            "不能因为某组末位更贴近论文就证明作者使用了该组。标准物理导数组是否适合作为新的研究实现，应与原论文精度复现分开讨论。"
        ),
        "",
    ]
    lines += [
        "## 解释与选择边界",
        "",
        "四组 Neumann 用来区分导数解释与更新分组；逐实例组在同样5000轮下有更多更新，不能称为同更新预算对照。两组 Advection 仅改变样条基矩阵及物理导数解释，均保留原首行插值和原目标。",
        "物理组采用标准样条值基、物理尺度及单侧端点；这是对论文物理方程的数学解释，并非论文作者逐行实现已知。论文式12阶数记号、随机名单和硬件差异仍未消除。",
        "原源码结果接近论文说明该运行路径能够得到相近精度，不代表其导数就是标准物理导数。物理组结果用于定位训练目标影响，不通过修改权重掩盖差异。单种子、不同论文测试名单不能证明论文统计复现。",
        "完整逐实例误差、原记录指标和检查点摘要见 verified_evidence.json；迁移方案待用户审查这些结果后决定。",
        "",
    ]
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    for ax, case, paper_value in zip(
        axes, ["neumann_diffusion", "advection"], [0.01932, 0.1444], strict=True
    ):
        selected = [r for r in rows if r["case"] == case]
        labels = [
            ("Physical" if r["physical"] else "Source")
            + "\n"
            + ("per instance" if r["instance_updates"] else "per epoch")
            for r in selected
        ]
        bars = ax.bar(
            labels,
            [r["mean_relative_l2"] for r in selected],
            color=["#ba6537" if r["physical"] else "#326788" for r in selected],
        )
        ax.axhline(paper_value, color="black", linestyle="--", label=f"Paper mean: {paper_value}")
        ax.set_yscale("log")
        ax.set_ylim(0.01, 2)
        ax.set_ylabel("Mean test relative L2 (dimensionless, log scale)")
        ax.set_title(
            "Neumann (10 test instances)"
            if case == "neumann_diffusion"
            else "Advection (30 test instances)"
        )
        ax.legend(loc="upper left", fontsize=8)
        for bar, r in zip(bars, selected, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() * 1.08,
                f"{r['mean_relative_l2']:.5f}",
                ha="center",
                fontsize=9,
            )
    fig.suptitle(
        "Independent full-budget trials; seed 42; original environment; not migrated to Dojo",
        fontsize=11,
    )
    fig.savefig(root / "reports/relative-l2.png", dpi=170)
    plt.close(fig)
    lines += [
        "",
        "![Six full-budget comparisons](relative-l2.png)",
        "",
        "图为保存场的误差重算，纵轴为对数尺度。Advection论文标准差0.1352未画成置信区间；单次运行不替代论文统计。",
    ]
    (root / "reports/六组独立验证报告.md").write_text("\n".join(lines))
    headings = "<tr><th>独立实验</th><th>导数</th><th>更新</th><th>实际平均相对L2</th><th>论文平均相对L2</th></tr>"
    cells = "".join(
        f"<tr><td>{r['variant']}</td><td>{'标准物理' if r['physical'] else '原参数'}</td>"
        f"<td>{'逐实例' if r['instance_updates'] else '整轮'}</td>"
        f"<td>{r['mean_relative_l2']:.8f}</td><td>{'.01932' if r['case'] == 'neumann_diffusion' else '.1444 ± .1352'}</td></tr>"
        for r in rows
    )
    document = (
        '<!doctype html><html lang="zh"><meta charset="utf-8">'
        "<title>Neumann 与 Advection 六组独立验证</title><style>"
        "body{font:16px/1.7 system-ui;max-width:1100px;margin:40px auto;padding:0 24px;color:#18212c}"
        "table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccd4dc;padding:10px;text-align:left}"
        "th{background:#eef2f5}pre{white-space:pre-wrap;font:inherit}</style>"
        "<h1>Neumann 与 Advection：六组独立验证</h1>"
        "<p>完整预算；相同原数据、初权重和环境。尚未迁移到 Dojo。</p>"
        "<table>"
        + headings
        + cells
        + '</table><p><img src="relative-l2.png" alt="Six full-budget comparisons" style="max-width:100%"></p><pre>'
        + html.escape("\n".join(lines))
        + "</pre></html>"
    )
    (root / "reports/六组独立验证报告.html").write_text(document)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    verify(args.root)
