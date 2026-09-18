"""从固定预测、原始真值和累计账本复算切片报告，不加载模型或再次采样。"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

from tools.verification.wdno.protocol import digest, write_json


def check_arrays(arrays, expected_ids):
    """完整样本身份与原 MSE 归约必须同时吻合。"""
    ids = arrays["ids"].tolist()
    if ids != expected_ids:
        raise ValueError("固定评价名单或顺序不完整")
    prediction, target = arrays["prediction"], arrays["target"]
    if prediction.shape != target.shape or prediction.shape != (len(ids), 81, 120):
        raise ValueError("固定物理轨迹形状不符")
    if arrays["forcing"].shape != (len(ids), 80, 120) or arrays["mse"].shape != (len(ids),):
        raise ValueError("力项或逐样本指标形状不符")
    if not all(
        np.isfinite(arrays[key]).all() for key in ("prediction", "target", "forcing", "mse")
    ):
        raise ValueError("固定结果包含非有限数值")
    recomputed = ((prediction[:, 1:] - target[:, 1:]) ** 2).mean(axis=(1, 2))
    if not np.allclose(recomputed, arrays["mse"], rtol=2e-6, atol=1e-6):
        raise ValueError("固定结果重算与原函数 MSE 不符")
    persistence = ((target[:, :1] - target[:, 1:]) ** 2).mean(axis=(1, 2))
    return {
        "count": len(ids),
        "mse": float(np.asarray(arrays["mse"]).mean()),
        "numpy_recomputed_mse": float(recomputed.mean()),
        "reduction_max_abs_difference": float(np.max(np.abs(recomputed - arrays["mse"]))),
        "persistence_mse": float(persistence.mean()),
        "initial_condition_max_abs": float(np.max(np.abs(prediction[:, 0] - target[:, 0]))),
    }


def plot_results(output, losses):
    """保存训练曲线和固定测试场对照；坐标仅标原数组索引。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(9, 3.8), layout="constrained")
    values = np.asarray([item["loss"] for item in losses])
    axis.plot(
        np.arange(1, len(values) + 1), values, alpha=0.45, lw=0.8, label="Source training loss"
    )
    if len(values) >= 50:
        axis.plot(
            np.arange(50, len(values) + 1),
            np.convolve(values, np.ones(50) / 50, mode="valid"),
            label="50-update mean",
        )
    axis.set(
        xlabel="Completed updates",
        ylabel="Diffusion loss",
        yscale="log",
        title="WDNO source model / local trajectory slice",
    )
    axis.legend()
    axis.grid(alpha=0.2)
    fig.savefig(output / "training-curve.png", dpi=160)
    plt.close(fig)
    with np.load(output / "test-results.npz", allow_pickle=False) as data:
        fig, axes = plt.subplots(3, 3, figsize=(11, 9), layout="constrained")
        for row in range(3):
            truth, prediction = data["target"][row], data["prediction"][row]
            bound = max(float(np.abs(truth).max()), float(np.abs(prediction).max()))
            for column, (field, title) in enumerate(
                (
                    (truth, "Original truth"),
                    (prediction, "Prediction"),
                    (np.abs(truth - prediction), "Absolute error"),
                )
            ):
                axis = axes[row, column]
                options = (
                    {"vmin": -bound, "vmax": bound, "cmap": "RdBu_r"}
                    if column < 2
                    else {"cmap": "magma", "vmin": 0}
                )
                picture = axis.imshow(field, origin="lower", aspect="auto", **options)
                axis.set(
                    title=f"{title} / sample {data['ids'][row]}",
                    xlabel="Space index",
                    ylabel="Time index",
                )
                fig.colorbar(picture, ax=axis, shrink=0.8)
        fig.savefig(output / "test-fields.png", dpi=150)
        plt.close(fig)


def create_report(root, *, supervised=False):
    """要求原运行完整收尾；训练步数和论文状态分别报告。"""
    import torch

    root = Path(root)
    output = root / "main"
    record = json.loads((output / "result.json").read_text())
    ledger = json.loads((root / "budget.json").read_text())
    indices = json.loads((root / "frozen" / "indices.json").read_text())
    protocol = json.loads((root / "frozen" / "protocol.json").read_text())
    if record["diagnostic"] or record["status"] != "slice_complete":
        raise ValueError("诊断或部分结果不能作完整切片验收")
    pending = [r for r in ledger["runs"] if r["status"] == "running"]
    own_worker = supervised and len(pending) == 1 and pending[0]["command"][-1] == "--worker"
    if (pending and not own_worker) or ledger["seconds"] > 10800:
        raise ValueError("账本未收尾或超过三小时")
    checkpoint = json.loads((output / "checkpoint.json").read_text())
    preparation = json.loads((output / "preparation.json").read_text())
    if preparation["samples"] != 18000 or preparation["sha256"] != digest(output / "train.npy"):
        raise ValueError("训练准备数量或保存内容变化")
    replay = json.loads((output / "checkpoint-replay.json").read_text())
    if replay["status"] != "passed" or replay["checkpoint_sha256"] != digest(checkpoint["path"]):
        raise ValueError("最终权重未通过独立进程重放或文件已变化")
    if checkpoint["completed_updates"] != record["updates"] or not 0 < record["updates"] <= 2000:
        raise ValueError("完成更新次数不一致")
    losses = json.loads((output / "losses.json").read_text())
    if [item["source_step"] for item in losses] != list(range(record["updates"])):
        raise ValueError("训练历史不是完整更新序列")
    results = {}
    for split in ("validation", "test"):
        source = protocol["sources"]["train" if split == "validation" else "test"]
        if digest(source["file"]) != source["sha256"]:
            raise ValueError("主实验后原始数据摘要变化")
        raw = torch.load(source["file"], map_location="cpu", mmap=True, weights_only=True)
        filename = output / (split + "-results.npz")
        with np.load(filename, allow_pickle=False) as arrays:
            metrics = check_arrays(arrays, indices[split])
            truth = raw["u"][indices[split]].numpy()
            if not np.array_equal(truth, arrays["target"]):
                raise ValueError("保存真值与原文件名单不一致")
            metrics["forcing_max_abs"] = float(
                np.max(np.abs(raw["f"][indices[split]].numpy() - arrays["forcing"]))
            )
            results[split] = {**metrics, "sha256": digest(filename)}
    window = min(50, len(losses))
    values = [item["loss"] for item in losses]
    report = {
        "scope": protocol["scope"],
        "slice_artifacts_verified": True,
        "updates": record["updates"],
        "planned_updates": 2000,
        "full_update_budget_completed": record["updates"] == 2000,
        "cumulative_seconds": ledger["seconds"],
        "first_window_loss": float(np.mean(values[:window])),
        "last_window_loss": float(np.mean(values[-window:])),
        "loss_window": window,
        "results": results,
        "checkpoint_sha256": digest(checkpoint["path"]),
        "checkpoint_replay": replay,
        "paper_reproduced": False,
        "dojo_migrated": False,
        "paper_burgers_mse_reference": 0.00014,
        "paper_comparable": False,
        "limitations": protocol["differences"]
        + [
            "Original checkpoint readback verified in diagnostic; exact data-stream resume not provided",
            "Separate conditioning channel is enforced; reconstructed u0 is not hard clamped by source algorithm",
            "Only local low-resolution fixed subset evaluated; no full-paper precision claim",
        ],
    }
    plot_results(output, losses)
    write_json(output / "acceptance.json", report)
    text = f"""# WDNO 原仓库三小时切片结果

本次完成原仓库基础预测切片的代码与产物验证。正式 Dojo 迁移和论文复现尚未完成。

- 完成更新：{record["updates"]} / 2000；累计计算：{ledger["seconds"] / 60:.2f} / 180 分钟，包含历史短测、诊断、失败及重试。
- 模型：原版 width128、groups1、140748553 参数、batch16、MPS float32；原 Trainer 和原 EMA 初始计数 0。
- 训练池：18000 条独立完整轨迹。固定验证 64、测试 128；原始数据没有改写。
- 前/后 {window} 次更新平均训练损失：{report["first_window_loss"]:.8g} → {report["last_window_loss"]:.8g}。
- 验证 MSE：{results["validation"]["mse"]:.8g}；测试 MSE：{results["test"]["mse"]:.8g}。按原函数排除初始帧，固定数组独立复算通过。
- 测试初值保持基线 MSE：{results["test"]["persistence_mse"]:.8g}。该基线只重复初态，不是原仓库重训对照。
- 测试重建初帧最大误差：{results["test"]["initial_condition_max_abs"]:.8g}；力项最大误差：{results["test"]["forcing_max_abs"]:.8g}。原模型通过单独条件通道提供初态，并不把预测初帧硬设为真值。

论文 Burgers MSE 参考值为 0.00014。本次使用脚本模型、缩小预算和本地基础测试子集，不能据此判定论文指标是否达成。高分辨率真值、论文 groups/预算、官方测试名单和权重选点仍需闭合。

完整文件：`acceptance.json`、`protocol.json`、`entry-source.json`、`preparation.json`、`losses.json`、`checkpoints/latest.pt`、`validation-results.npz`、`test-results.npz`。检查点保持原字段，并由 `checkpoint.json` 单独记录真实完成更新数；本阶段未提供精确数据流续训。

![训练损失]({output / "training-curve.png"})

![固定测试场对照]({output / "test-fields.png"})

后续按计划先完成原版论文协议及参考复现门槛，再进入 Dojo 正式迁移和 Agent 变体组合验收。
"""
    (output / "REPORT.md").write_text(text)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if os.environ.get("WDNO_REPORT_WORKER") != "1":
            raise RuntimeError("报告计算须由累计监督入口执行")
        print(json.dumps(create_report(args.root, supervised=True), ensure_ascii=False, indent=2))
    else:
        from tools.verification.gencp.budget import run_budgeted

        os.environ["WDNO_REPORT_WORKER"] = "1"
        command = [
            sys.executable,
            "-m",
            "tools.verification.wdno.report",
            "--root",
            str(args.root),
            "--worker",
        ]
        code = run_budgeted(args.root / "budget.json", command, soft=10740, hard=10790)
        if code:
            raise SystemExit(code)
        # 监督器已收尾，发布包含本次复算成本的最终账本数值。
        ledger = json.loads((args.root / "budget.json").read_text())
        output = args.root / "main"
        report = json.loads((output / "acceptance.json").read_text())
        previous = report["cumulative_seconds"]
        report["cumulative_seconds"] = ledger["seconds"]
        write_json(output / "acceptance.json", report)
        document = (
            (output / "REPORT.md")
            .read_text()
            .replace(f"{previous / 60:.2f} / 180 分钟", f"{ledger['seconds'] / 60:.2f} / 180 分钟")
        )
        (output / "REPORT.md").write_text(document)
        print(json.dumps(report, ensure_ascii=False, indent=2))
