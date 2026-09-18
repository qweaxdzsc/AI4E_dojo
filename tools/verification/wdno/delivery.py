"""固定迁移产物的独立报告与安装来源记录，不触发训练或采样。"""

import argparse
import importlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from ai4e_core.abilities.data.save.array_manifest import read_arrays
from tools.verification.wdno.protocol import digest, write_json

REPO = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--wheels", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / "dojo-final"
    comparison = json.loads((output / "comparison.json").read_text())
    if not comparison["passed"]:
        raise ValueError("数值比较尚未通过，不能发布迁移完成报告")
    cfg = yaml.safe_load((output / "config.yaml").read_text())
    # 只读历史报告可按其冻结版本消费旧树，新产物必须取当前明确输入。
    results = cfg["inputs"]["post"] if "inputs" in cfg else cfg["post"]["results"]
    checkpoint = (
        cfg["inputs"]["infer"]["checkpoint"] if "inputs" in cfg else cfg["infer"]["checkpoint"]
    )
    training = json.loads((output / "train-summary.json").read_text())["reports"]["train"]
    reference = json.loads((root / "reference-current-2/losses.json").read_text())
    current = np.array(training["history"])
    original = np.array([x["loss"] for x in reference])
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    ax.semilogy(
        np.arange(1, len(original) + 1),
        original,
        color="#475569",
        alpha=0.4,
        label="Original Trainer",
    )
    ax.semilogy(
        np.arange(50, len(current) + 1),
        np.convolve(current, np.ones(50) / 50, mode="valid"),
        color="#0284c7",
        label="Dojo, 50-update mean",
    )
    ax.set(
        xlabel="Completed optimizer updates",
        ylabel="Diffusion loss",
        title="WDNO Burgers: same environment, seed 0, 2000 updates",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.savefig(output / "training-comparison.png", dpi=170)
    plt.close(fig)
    _, arrays = read_arrays(results["test"], kind="spatiotemporal-result-v1")
    prediction, target = arrays["prediction"][0], arrays["target"][0]
    limit = max(float(np.abs(target).max()), float(np.abs(prediction).max()))
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), layout="constrained")
    for ax, value, title in zip(
        axes,
        [target, prediction, prediction - target],
        ["Target", "Dojo prediction", "Prediction - target"],
    ):
        bound = float(np.abs(value).max()) if title.startswith("Prediction -") else limit
        im = ax.imshow(value, origin="lower", aspect="auto", cmap="RdBu_r", vmin=-bound, vmax=bound)
        ax.set(title=title, xlabel="Spatial index", ylabel="Time index")
        fig.colorbar(im, ax=ax, shrink=0.85)
    fig.suptitle(f"Fixed test trajectory {int(arrays['ids'][0])}; initial frame is not clamped")
    fig.savefig(output / "test-comparison.png", dpi=170)
    plt.close(fig)
    installed = {}
    for name in [
        "ai4e_core.applications.spatiotemporal_pde.train",
        "ai4e_contrib.application.spatiotemporal_pde.wdno.training",
        "ai4e_contrib.ability.inference.wdno.diffusion",
    ]:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        installed[name] = {"path": str(path), "sha256": digest(path)}
        if "installed-final" not in str(path):
            raise ValueError("报告必须使用实际安装副本")
    wheels = {str(path.resolve()): digest(path) for path in args.wheels.glob("*.whl")}
    if len(wheels) != 3:
        raise ValueError("交付需包含spec/core/contrib三份wheel")
    source_directory = output / "delivery-code"
    source_directory.mkdir(exist_ok=False)
    for filename in (
        "migration.py",
        "finish.py",
        "delivery.py",
        "vendor.py",
        "variant.py",
        "import_replay.py",
        "audit.py",
    ):
        shutil.copy2(Path(__file__).parent / filename, source_directory / filename)
    delivery = {
        "dojo_migrated": True,
        "scope": "Burgers base local slice",
        "paper_reproduced": False,
        "installed_modules": installed,
        "wheels": wheels,
        "comparison": comparison,
        "checkpoint": checkpoint,
        "configuration_sha256": digest(output / "config.yaml"),
        "ledger": str(root / "budget.json"),
        "source_environment": "Python3.12.14/Torch2.14.0/Accelerate1.0.1",
        "exact_resume": "2 -> 50 -> 2000 updates on MPS",
        "tests": "See migration-final-tests.xml after the cumulative ledger closes",
    }
    write_json(output / "delivery.json", delivery)
    val, test = comparison["evaluation"]["validation"], comparison["evaluation"]["test"]
    text = f"""# WDNO 基础预测迁移结果

Dojo 已完成本地 Burgers 基础预测缩小迁移。双方在同一环境从同一原数据切片完成 2000 次更新；Dojo 实际经历 2 → 50 → 2000 的检查点恢复。

- 原Trainer与Dojo的全部模型权重、优化器状态、EMA状态和2000个训练损失逐值一致。
- 18000条模型准备逐值一致；固定64条验证和128条测试的状态预测、驱动力与真值逐值一致。
- 验证MSE：**{val["mse"]:.12g}**；测试MSE：**{test["mse"]:.12g}**。这里采用原评价的初帧排除和样本等权定义。
- 前/后50步平均训练损失：{current[:50].mean():.10g} → {current[-50:].mean():.10g}。
- 主网络140748553参数、dim128/groups1、batch16、训练seed0（划分seed42）、Adam1e-4、cosine10000、EMA .995/10、MPS FP32、DDIM50 eta1、普通权重。

## 使用与证据

实际配置：[config.yaml]({output / "config.yaml"})；检查点：[latest.pt]({checkpoint})。

安装来源与wheel摘要：[delivery.json]({output / "delivery.json"})；逐项比较：[comparison.json]({output / "comparison.json"})；原版：[reference-current-2]({root / "reference-current-2"})。

可复制入口：[recipes/wdno/README.md]({REPO / "recipes/wdno/README.md"})；普通函数变体：[variants.py]({REPO / "examples/recipe_extensions/wdno/variants.py"})。网络、损失和能量输出已通过实际wheel和仓库外复制测试。

## 结论范围

这是基础预测切片的完整迁移一致性验收。论文表中Burgers MSE0.00014所用协议与当前本地切片不同；论文精度、超分、控制、Smoke以及其它系统均未完成。旧Torch2.4.1的原版2000步结果继续保留在main，不用它代替本次同环境参考。原版依旧使用冻结原Trainer/数值定义，但物理数据来源、单进程读取、日志和保存位置有明确本地适配；不称未经适配的论文全程序。

主环境和正式8000/5173服务未更新。此次实际入口是隔离安装副本和Python recipe。

三小时预算沿用原账本，覆盖原版、Dojo、准备、评价和失败重试；并行短验收发生在原版计账时段。最终累计数字见[budget.json]({root / "budget.json"})，报告生成完成后由监督器记入；不以生成报告时尚未关闭的账本数字作为最终累计值。

![训练对照]({output / "training-comparison.png"})

![固定测试场]({output / "test-comparison.png"})
"""
    (output / "REPORT.md").write_text(text)


if __name__ == "__main__":
    main()
