"""从已验收的Dojo完整实验生成迁移报告、固定参数评价和科学场图。"""

import argparse
import html
import json
from pathlib import Path

import matplotlib
import numpy as np
import torch
import yaml
from source_dojo import report

from ai4e_contrib.ability.model.pibsnet import component
from ai4e_contrib.application.datasets.parametric import component as generator
from ai4e_core.applications.parametric_pde.model import build_model

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def create(root):
    """重新逐值验证完整实验后才发布汇总；不会启动或替代训练。"""
    rows = [report(root / case) for case in ["neumann_diffusion", "advection"]]
    output = root / "reports"
    output.mkdir(exist_ok=True)
    cfg = yaml.safe_load((root / "neumann_diffusion/config.yaml").read_text())
    model = build_model(cfg, component)
    model.load_state_dict(torch.load(rows[0]["checkpoint"], weights_only=False)["model"])
    model.eval()
    fixed = []
    with torch.no_grad():
        for nu in [0.2, 0.4, 1.2]:
            sample = generator("neumann_diffusion").make_sample(
                np.random.RandomState(42),
                {"nx": 128, "nt": 128, "parameters": {"nu": nu}},
                index=0,
                split="test",
            )
            sample.update(case="neumann_diffusion", id=f"fixed-nu-{nu}")
            prediction = component.predictions(model, component.prepare(sample, cfg), cfg)["u"]
            error = float(
                (prediction.double() - sample["u"].double()).norm() / sample["u"].double().norm()
            )
            torch.save(
                {
                    "prediction": prediction,
                    "target": sample["u"],
                    "parameters": sample["parameters"],
                },
                output / f"fixed-nu-{nu}.pt",
            )
            fixed.append({"nu": nu, "relative_l2": error})
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for i, row in enumerate(rows):
        data = torch.load(root / row["case"] / "predictions/test-00000.pt", weights_only=False)
        truth = data["target"].numpy()
        pred = data["prediction"].numpy()
        for j, (name, values) in enumerate(
            [
                ("Analytical truth", truth),
                ("Dojo prediction", pred),
                ("Absolute error", np.abs(pred - truth)),
            ]
        ):
            image = axes[i, j].imshow(
                values,
                origin="lower",
                aspect="auto",
                extent=[0, 1, 0, 1 if i == 0 else 2],
                cmap="viridis",
                vmin=0 if j == 2 else -1,
                vmax=None if j == 2 else 1,
            )
            axes[i, j].set_title(("Neumann: " if i == 0 else "Advection: ") + name)
            axes[i, j].set_xlabel("x")
            axes[i, j].set_ylabel("t")
            fig.colorbar(image, ax=axes[i, j], label="u" if j < 2 else "|prediction - truth|")
    fig.savefig(output / "fields.png", dpi=150)
    plt.close(fig)
    lines = [
        "# Neumann与Advection：Dojo原代码迁移验收",
        "",
        "两例已在Dojo内重新生成数据、准备、完整训练及独立后处理。采用用户确认的原代码数值行为，以精度接近论文为目标。",
        "",
        f"- Neumann：Dojo平均相对L2 **{rows[0]['mean_relative_l2']:.8f}（{rows[0]['mean_relative_l2'] * 100:.3f}%）**；论文 **1.932%**。5000轮/5000更新，50训练/10测试，40×40五次样条，隐藏128。",
        f"- Advection：Dojo平均相对L2 **{rows[1]['mean_relative_l2']:.8f}（{rows[1]['mean_relative_l2'] * 100:.3f}%）**；论文 **14.44% ± 13.52个百分点**。2000轮/200000更新，100训练/30测试，150×150五次样条，隐藏64。",
        "",
        "两例的数据与初权重均与锁定原基线逐值一致；同环境独立原函数与Dojo的全部最终权重、每轮损失和40个完整测试场逐值一致。",
        "",
        "## 实际迁移内容",
        "",
        "Neumann保留原参数空间导数、二阶递推和端点，重放原初始化随机消耗，整轮损失顺序求和后一次反传。Advection恢复原初始控制行插值、参数导数和融合MSELoss，逐实例Adam更新。两例数据使用连续MT19937流，FP32轴/参数/标签，保留原计算精度和取模流程。",
        "独立生成器位于contrib，不依赖训练模型；core继续装配rawprep→trainprep→train→post。普通物理方程函数不改变；原参数导数明确命名，不伪装成标准物理导数。",
        "",
        "## 环境与历史资产",
        "",
        "当前Dojo为Python3.12/NumPy2.5.3/Torch2.14，CPU、FP32、单计算线程。旧独立原环境Neumann为1.875%，当前同环境原函数及Dojo为1.881%；末位变化不通过调参消除。Advection约10.427%。不是论文RTX4090或作者未公开随机名单的逐行复刻。",
        "旧数据协议、准备和检查点不直接续用。当前共享模型组件来源变更时，其他案例历史准备仍需旧源码快照消费；不批量重写历史证据。",
        "",
        "## 五案例口径",
        "",
        "Neumann、Advection：本报告已迁移并完成全预算验证。梯形：保留用户选定十实例方案，既有Dojo结果0.5405%，同环境原函数逐值一致，旧独立环境0.3053%，论文0.3172%。",
        "对流扩散、Burgers：此次未切换模型与数据算法；公共整轮求和的算术顺序修正也作用于对流扩散，历史精度不能冒称为新配置实跑结果；是否全部恢复原代码已单独询问，不能把之前的独立原结果写成新Dojo结果。",
        "",
        "## 固定参数补充评价",
        "",
        *["- ν=" + str(r["nu"]) + "：相对L2 " + str(r["relative_l2"]) for r in fixed],
        "",
        "固定参数评价独立保存，不混入十个随机测试实例均值。图为固定第一个测试实例，预测与真值共用色标；误差图独立色标。",
        "",
        "![Dojo fields](fields.png)",
        "",
    ]
    (output / "迁移验收报告.md").write_text("\n".join(lines))
    (output / "迁移验收报告.html").write_text(
        '<!doctype html><html lang="zh"><meta charset="utf-8"><title>Dojo迁移验收</title><style>body{max-width:1050px;margin:40px auto;font:16px/1.7 system-ui;padding:24px}pre{white-space:pre-wrap;font:inherit}img{max-width:100%}</style><pre>'
        + html.escape("\n".join(lines))
        + '</pre><img src="fields.png" alt="Dojo fields"></html>'
    )
    (output / "verification.json").write_text(
        json.dumps({"cases": rows, "fixed_neumann": fixed}, ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    create(args.root)
