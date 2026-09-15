"""选定梯形实验在 Dojo 的独立生成、逐层预检、正式阶段与结果核验。"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

from ai4e_contrib.ability.model.pibsnet import component
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import generate
from ai4e_contrib.application.datasets.parametric import Dataset
from ai4e_core.abilities.data.save.bundle import file_digest, save_json
from ai4e_core.applications.parametric_pde.model import build_model

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "recipes/parametric_pde"))
from configuration import defaults


def launch(root, stage):
    """调用实际可复制 recipe 入口，不另写训练循环。"""
    command = [
        "uv",
        "run",
        "--no-project",
        "--python",
        sys.executable,
        "python",
        str(REPO / "recipes/parametric_pde" / f"{stage}.py"),
        "--config",
        str(root / "config.yaml"),
    ]
    if stage == "post":
        checkpoints = list((root / "runs").glob("*/checkpoints/last.pt"))
        if len(checkpoints) != 1:
            raise ValueError("正式训练检查点数量不为一")
        command += ["--set", f"post.checkpoint={checkpoints[0]}"]
    with (root / f"{stage}.log").open("w") as log:
        subprocess.run(
            command,
            cwd=root,
            env={**os.environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def prepare(root, reference, *, existing=False):
    """新生成标签/名单/初始化逐值对照，通过后才允许正式运行。"""
    root.mkdir(parents=True, exist_ok=existing)
    cfg = defaults("diffusion_trapezoid")
    cfg["dataset"]["manifest"] = str(root / "datasets/manifest.json")
    cfg["trainprep"]["output"] = str(root / "prepared")
    cfg["run_root"] = str(root / "runs")
    cfg["post"]["output"] = str(root / "predictions")
    cfg["train"].update(device="cpu", log_every=100)
    if existing:
        if yaml.safe_load((root / "config.yaml").read_text()) != cfg:
            raise ValueError("继续预检的配置已改变，不能覆盖后冒充同一个实验")
    else:
        (root / "config.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    if not existing:
        generate({"output": str(root / "datasets"), "train": 10, "test": 10, "seed": 42})
    dataset = Dataset(cfg["dataset"]["manifest"])
    original = torch.load(reference / "data/train.pt", weights_only=False)
    errors = []
    for record, (a, t, truth) in zip(dataset.records("train"), original, strict=True):
        sample = dataset.read(record)
        assert sample["parameters"]["a"] == a
        np.testing.assert_array_equal(sample["axes"]["t"].numpy(), t)
        np.testing.assert_array_equal(sample["u"].float().numpy(), truth)
        errors.append({"id": record["id"], "a": a, "max_absolute_difference": 0})
    parameters = [
        json.loads(s)
        for s in (reference / "predictions/parameters.jsonl").read_text().splitlines()
        if "trial-" in s
    ]
    for record, expected in zip(dataset.records("test"), parameters, strict=True):
        assert dataset.read(record)["parameters"] == expected["parameters"]
    network = build_model(cfg, component)
    initial = torch.load(reference / "checkpoints/initial.pt", weights_only=False)["model"]
    for key, tensor in network.state_dict().items():
        torch.testing.assert_close(tensor, initial[key], rtol=0, atol=0)
    # 相同既有权重、完整网格的新计算也必须逐值一致；不是正式重训精度。
    sample = dataset.read(dataset.records("test")[0])
    prepared = component.prepare(sample, cfg)
    network.load_state_dict(
        torch.load(reference / "checkpoints/last.pt", weights_only=False)["model"]
    )
    with torch.no_grad():
        prediction = component.predictions(network, prepared, cfg)["u"].numpy()
    file = reference / "predictions/test-trial-0.npz"
    with np.load(file) as saved:
        np.testing.assert_array_equal(sample["u"].float().numpy(), saved["target"])
        max_error = float(np.max(np.abs(prediction - saved["prediction"])))
        np.testing.assert_allclose(prediction, saved["prediction"], atol=1e-6, rtol=1e-6)
    save_json(
        root / "preflight.json",
        {
            "status": "passed",
            "reference": str(reference),
            "train_arrays": errors,
            "test_parameters_equal": True,
            "initial_weights_equal": True,
            "same_checkpoint_forward_max_error": max_error,
            "reference_checkpoint_sha256": file_digest(reference / "checkpoints/last.pt"),
            "python": sys.version,
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "threads": torch.get_num_threads(),
        },
    )
    launch(root, "rawprep")
    launch(root, "trainprep")


def report(root, reference):
    """检查全部3000轮/30000次更新和十个预测，再交付可重算证据。"""
    checkpoints = list((root / "runs").glob("*/checkpoints/last.pt"))
    if len(checkpoints) != 1:
        raise ValueError("正式检查点缺失或不唯一")
    state = torch.load(checkpoints[0], weights_only=False)
    assert (state["epoch"], state["updates"]) == (3000, 30000)
    assert len(state["history"]) == 3000
    summary = json.loads((root / "predictions/predictions.json").read_text())
    assert summary["status"] == "complete" and len(summary["samples"]) == 10
    values, diffs = [], []
    for i, row in enumerate(summary["samples"]):
        actual = torch.load(root / "predictions" / f"{row['id']}.pt", weights_only=False)
        pred, truth = actual["prediction"].numpy(), actual["target"].numpy()
        with np.load(reference / "predictions" / f"test-trial-{i}.npz") as expected:
            np.testing.assert_array_equal(truth, expected["target"])
            diffs.append(float(np.max(np.abs(pred - expected["prediction"]))))
        d = (pred - truth).reshape(len(truth), -1).astype("float64")
        r = truth.reshape(len(truth), -1).astype("float64")
        values.append(np.linalg.norm(d, axis=1) / (np.linalg.norm(r, axis=1) + 1e-12))
    mean, std = float(np.mean(values)), float(np.std(values))
    assert np.isclose(mean, summary["mean_time_relative_l2"], atol=1e-12)
    baseline = json.loads((reference / "result.json").read_text())["mean_relative_l2"]
    evidence = {
        "status": "complete",
        "epochs": state["epoch"],
        "updates": state["updates"],
        "mean_time_relative_l2": mean,
        "std_over_samples_and_times": std,
        "whole_spacetime_relative_l2": summary["mean_relative_l2"],
        "independent_reference_mean": baseline,
        "prediction_max_differences": diffs,
        "checkpoint": str(checkpoints[0]),
        "checkpoint_sha256": file_digest(checkpoints[0]),
        "preflight": json.loads((root / "preflight.json").read_text()),
    }
    same = root / "same_environment_reference"
    comparison = None
    if (same / "result.json").exists():
        comparison = json.loads((same / "result.json").read_text())
        assert (comparison["epochs"], comparison["updates"]) == (3000, 30000)
        actual = torch.load(same / "last.pt", weights_only=False)
        assert actual["history"] == [row["loss"] for row in state["history"]]
        for key in state["model"]:
            torch.testing.assert_close(actual["model"][key], state["model"][key], rtol=0, atol=0)
        for row in summary["samples"]:
            dojo = torch.load(root / "predictions" / f"{row['id']}.pt", weights_only=False)
            with np.load(same / f"{row['id']}.npz") as other:
                np.testing.assert_array_equal(other["prediction"], dojo["prediction"].numpy())
                np.testing.assert_array_equal(other["target"], dojo["target"].numpy())
        evidence["same_environment_reference"] = comparison
        evidence["same_environment_training_equivalence"] = (
            "all_weights_history_and_ten_fields_exact"
        )
    save_json(root / "verification.json", evidence)
    text = f"""# 梯形十实例 Dojo 接入验证

Dojo 完整训练：3000轮、30000次更新，CPU/FP32；独立 post 交付10个全网格预测。

- Dojo 原评价口径相对 L2：{mean:.12f}（跨实例/时间标准差 {std:.12f}）。
- 选定独立参考实验：{baseline:.12f}。
- 论文：0.003172 ± 0.001580；论文与源码仍存在未决数学差异，不宣称完整论文复现。
- Dojo 整体时空相对 L2：{summary["mean_relative_l2"]:.12f}，不能与逐时间平均混用。
- 同初权重、同训练参数及标签、同测试参数及标签已逐值核验。
- 重训预测与独立参考最大逐点差：{max(diffs):.12g}。

本轮独立生成新数据；保留原 Euler 近似空间模板、参数空间样条导数、完整输出头及初边界覆盖。只更换梯形案例，未改变 Neumann/Advection 算法。原参考 Python3.9/NumPy1.26/Torch2.8；Dojo 实际版本见 preflight.json。没有将独立实验权重当作新训练检查点；该权重只用于预检前向计算。

原评价先得到10个有效实例即停止，所选种子没有拒绝样本。本次固定重放这10个名单，不做预测后的筛选。

证据：verification.json、preflight.json、config.yaml、datasets/、prepared/、runs/、predictions/。旧实验和检查点保持原样，不支持直接续训旧结构。
"""
    if comparison:
        text += """
## 同环境完整训练对照

为定位与旧环境结果的差距，在当前Dojo环境独立运行锁定原数值函数，同数据、同初始化、同3000轮/30000次更新。原函数与Dojo最终全部权重、3000轮损失记录、10个完整预测场逐值一致，最大差异均为0。原函数同样得到相对L2=0.005404546049。

因此本次框架迁移的全训练数值等价性已经验证；当前环境未重现旧环境0.003053496246的精度。差异定位到跨环境数值轨迹，尚未拆分为具体库或算子原因，不擅自调整依赖、权重或预算。原函数对照的计时不含Dojo逐轮检查点及数据读盘开销，不能直接称为算法加速比。

对应证据为same_environment_reference/result.json、last.pt和十个npz；verification.json已从双方实际权重、历史、预测数组再次逐值复核。Neumann/Advection输入核查见仓库docs/pibsnet/Neumann与Advection输入核查.md，本轮未修改或重训这两例。
"""
    (root / "接入验证报告.md").write_text(text)
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "verify", "train", "report"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(1)
    if args.action in {"prepare", "verify"}:
        prepare(args.root, args.reference, existing=args.action == "verify")
    elif args.action == "train":
        if json.loads((args.root / "preflight.json").read_text())["status"] != "passed":
            raise ValueError("未通过预检")
        launch(args.root, "train")
        launch(args.root, "post")
        print(report(args.root, args.reference))
    else:
        print(report(args.root, args.reference))
