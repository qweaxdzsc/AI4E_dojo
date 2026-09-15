"""从三组完整论文参数实验重算指标并生成独立报告，不挑选最好结果。"""

import argparse
import ast
import base64
import html
import json
import time
from pathlib import Path

import numpy as np
from paper_parameters import VARIANTS, amend_cell, sha, write_json


def prediction_metrics(prediction, target, *, time_average=False):
    """保留原评价浮点减法与归约口径，同时输出逐实例指标。"""
    if prediction.shape != target.shape or not (
        np.isfinite(prediction).all() and np.isfinite(target).all()
    ):
        raise ValueError("预测形状不匹配或包含非有限数")
    if time_average:
        error = (prediction - target).reshape(len(target), -1).astype("float64")
        reference = target.reshape(len(target), -1).astype("float64")
        return float(
            np.mean(np.linalg.norm(error, axis=1) / (np.linalg.norm(reference, axis=1) + 1e-12))
        )
    return float(np.linalg.norm((prediction - target).ravel()) / np.linalg.norm(target.ravel()))


def verify_variant(root, variant):
    """完整轮次、更新次数、预测覆盖和源码差异全部符合才返回验收证据。"""
    case, epochs, updates = VARIANTS[variant]
    directory = root / variant
    status = json.loads((directory / "status.json").read_text())
    result = json.loads((directory / "result.json").read_text())
    if status["status"] != "complete" or (status["epochs_completed"], status["updates"]) != (
        epochs,
        updates,
    ):
        raise ValueError(f"{variant} 未完成预算")
    if (result["epochs_completed"], result["updates"]) != (epochs, updates):
        raise ValueError(f"{variant} 结果与运行状态不一致")
    history = [
        json.loads(line) for line in (directory / "logs/epochs.jsonl").read_text().splitlines()
    ]
    if len(history) != epochs or history[-1]["updates"] != updates:
        raise ValueError(f"{variant} 轮次记录不完整")
    if not np.isfinite([item["loss"] for item in history]).all():
        raise ValueError(f"{variant} 训练损失包含非有限数")
    predictions, metrics = [], []
    files = sorted((directory / "predictions").glob("*.npz"))
    expected_count = 20 if case == "burgers" else result["trials"] + 1
    if len(files) != expected_count:
        raise ValueError(f"{variant} 预测记录缺失")
    if case != "burgers" and len(result["accepted_alphas"]) != 10:
        raise ValueError(f"{variant} 没有10个有效测试实例")
    if case != "burgers" and result["trials"] != 10:
        raise ValueError("存在筛选试验，须单独核对每次筛选与有效名单，不能盲目平均")
    for path in files:
        with np.load(path) as data:
            metric = prediction_metrics(
                data["prediction"], data["target"], time_average=case != "burgers"
            )
            shape = list(data["target"].shape)
        predictions.append(
            {"file": str(path), "shape": shape, "relative_l2": metric, "sha256": sha(path)}
        )
        if "single" not in path.name:
            metrics.append(metric)
    mean = float(np.mean(metrics))
    if not np.isclose(mean, result["mean_relative_l2"], rtol=1e-6, atol=1e-9):
        raise ValueError(f"{variant} 原指标与预测重算不一致")
    definitions = []
    for path in (directory / "logs").glob("*.original.py"):
        index = int(path.name.split(".")[0].split("-")[1])
        approved = amend_cell(path.read_text(), case, index, variant).replace(
            "!pip install shapely", "# install"
        )
        actual = path.with_name(path.name.replace(".original.py", ".executed.py")).read_text()
        trees = [ast.parse(text) for text in (approved, actual)]
        declarations = [
            sorted(
                ast.dump(n)
                for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))
            )
            for tree in trees
        ]
        if declarations[0] != declarations[1]:
            raise ValueError(f"{variant} 函数定义超出确认变更范围")
        definitions.append({"cell": index, "matches_approved_definitions": True})
    return {
        "status": status,
        "source_result": result,
        "mean_relative_l2": mean,
        "test_instance_std": float(np.std(metrics)),
        "per_test": metrics,
        "predictions": predictions,
        "definitions": definitions,
        "checkpoints": {p.name: sha(p) for p in (directory / "checkpoints").glob("*.pt")},
        "data": {p.name: sha(p) for p in (directory / "data").glob("*.pt")},
    }


def report(root):
    """交付三组原始结果、与原基线和论文的差距、未决项及可读预测图。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import torch

    protocol = json.loads((root / "protocol.json").read_text())
    baseline = Path(protocol["baseline"])
    hashes = json.loads((root / "source/hashes.json").read_text())
    amendment_path = root / "source/epoch_logging_amendment.json"
    if amendment_path.exists():
        for item in json.loads(amendment_path.read_text()):
            name = str(Path(item["file"]).relative_to(root))
            if hashes[name] != item["before"]:
                raise ValueError("日志修订前摘要不匹配")
            hashes[name] = item["after"]
    for name, digest in hashes.items():
        if sha(root / name) != digest:
            raise ValueError(f"实验冻结来源发生未记录的变化：{name}")
    evidence = {variant: verify_variant(root, variant) for variant in VARIANTS}

    # 同数据/同初始化的证据只对 Burgers 声明；梯形名单按原随机流变化。
    def equal(left, right):
        if isinstance(left, torch.Tensor):
            return isinstance(right, torch.Tensor) and torch.equal(left, right)
        if isinstance(left, np.ndarray):
            return isinstance(right, np.ndarray) and np.array_equal(left, right)
        if isinstance(left, dict):
            return left.keys() == right.keys() and all(equal(left[key], right[key]) for key in left)
        if isinstance(left, (tuple, list)):
            return len(left) == len(right) and all(equal(a, b) for a, b in zip(left, right))
        return left == right

    matched = {}
    for name in ("train.pt", "test.pt"):
        data = [
            torch.load(p / "burgers/data" / name, weights_only=False, map_location="cpu")
            for p in (root, baseline)
        ]
        matched[name] = equal(*data)
    states = [
        torch.load(p / "burgers/checkpoints/initial.pt", weights_only=False, map_location="cpu")[
            "model"
        ]
        for p in (root, baseline)
    ]
    matched["initial_weights"] = equal(*states)
    evidence["burgers"]["baseline_identity"] = matched
    write_json(root / "reports/verified_evidence.json", evidence)
    title = "PI-BSNet 论文参数三组验证报告"
    lines = [
        f"# {title}",
        "本轮按用户确认的有限范围验证论文参数，完整预算三组均完成。不是完整论文算法复现，也未修改Dojo算法。",
        "Burgers：正对流项（PDF41式86）及MSE（PDF5式8/9）；其余按原代码，包括100训练/20测试、5000轮、100×100控制点及数据权重15。",
        "梯形：主文10实例、附录50实例分别运行；均采用100×20×20控制点、0.001 PDE权重、3000轮。原Euler数据、样条、初边界及逐实例更新保留。",
        "环境：Python3.9.25 / NumPy1.26.4 / SciPy1.13.1 / PyTorch2.8.0，CPU、FP32、单线程、种子42。无调参、早停或挑选最优轮次。",
        "## 数值结果",
    ]
    blocks = [f"<h1>{title}</h1>"]
    for variant, value in evidence.items():
        case, epochs, updates = VARIANTS[variant]
        paper = 0.07294 if case == "burgers" else 0.003172
        old = json.loads((baseline / case / "result.json").read_text())["mean_relative_l2"]
        mean = value["mean_relative_l2"]
        name = {
            "burgers": "Burgers",
            "trapezoid_10": "梯形扩散 · 主文10实例",
            "trapezoid_50": "梯形扩散 · 附录50实例",
        }[variant]
        lines += [
            f"### {name}",
            f"本次平均相对L2：{mean:.10g}；原仓库基线：{old:.10g}；论文所报均值：{paper:.10g}。",
            f"相对论文均值差距：{(mean / paper - 1) * 100:+.2f}%；相对原基线差距：{(mean / old - 1) * 100:+.2f}%。这是数值比值，不是复现通过阈值。",
            f"完整预算：{epochs}轮 / {updates}次更新；测试实例间标准差：{value['test_instance_std']:.10g}（不是训练种子置信区间）。",
            f"证据目录：{root / variant}。",
        ]
        if case != "burgers":
            lines += [
                "指标沿原代码：每时间片计算空间相对L2，再对时间及有效实例取平均；另保存单例预测。论文聚合细节未完全明确。",
                f"原评价尝试{value['source_result']['trials']}次，有效{len(value['source_result']['accepted_alphas'])}次；无事后排除失败样本。",
            ]
        path = Path(value["predictions"][0]["file"])
        with np.load(path) as data:
            pred, target = data["prediction"], data["target"]
            if case != "burgers":
                pred, target = pred[-1], target[-1]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), layout="constrained")
        for ax, array, label in zip(
            axes,
            (target, pred, np.abs(pred - target)),
            ("Original solver target", "Paper-parameter prediction", "Absolute error"),
        ):
            im = ax.imshow(
                array,
                origin="lower",
                aspect="auto",
                cmap="viridis" if label != "Absolute error" else "magma",
                vmin=min(float(pred.min()), float(target.min()))
                if label != "Absolute error"
                else 0,
                vmax=max(float(pred.max()), float(target.max()))
                if label != "Absolute error"
                else None,
            )
            ax.set(
                title=label,
                xlabel="Spatial grid index",
                ylabel="Time grid index" if case == "burgers" else "Eta grid index (final time)",
            )
            fig.colorbar(im, ax=ax)
        fig.savefig(root / "reports" / (variant + ".png"), dpi=150)
        plt.close(fig)
        lines.append(f"![{name}：按文件名排序的首个保存实例；梯形展示最终时刻。]({variant}.png)")
    lines += [
        "## 比较边界",
        f"Burgers 与原基线的实际数据及初始化逐值核对：{json.dumps(matched, ensure_ascii=False)}。两项训练目标同时修改，不能分离符号与损失归约的各自影响。",
        protocol["test_scope"],
        "本轮未解决：" + "；".join(protocol["unresolved"]) + "。",
        "不能因误差接近就证明设置与算法完全一致，也不能将论文测试实例间离散度作为本次训练的不确定区间。",
        "首次启动在任何数据生成或训练前因虚拟环境入口解析错误失败；旧目录保留日志，修复解释器入口后另建run2目录。未发生数值试跑后选优。",
        "依据：冻结原仓库提交40ffb6239d865b6b7a16538559939a990e6d9cd5；论文副本source/PI-BSNet.pdf；protocol.json；reports/verified_evidence.json。",
    ]
    md = "\n\n".join(lines) + "\n"
    (root / "reports/论文参数三组验证报告.md").write_text(md)
    for line in lines[1:]:
        if line.startswith("!["):
            filename = line.rsplit("(", 1)[1][:-1]
            caption = line[2 : line.index("]")]
            encoded = base64.b64encode((root / "reports" / filename).read_bytes()).decode()
            blocks.append(
                f'<figure><img src="data:image/png;base64,{encoded}"><figcaption>{html.escape(caption)}</figcaption></figure>'
            )
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            blocks.append(f"<h{level}>{html.escape(line.lstrip('# '))}</h{level}>")
        else:
            blocks.append(f"<p>{html.escape(line)}</p>")
    page = (
        '<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'
        + title
        + '</title><style>body{font:16px/1.8 -apple-system,"PingFang SC",sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;color:#263238}h1{font-size:26px}h2{border-bottom:1px solid #ddd}h3{margin-top:32px}p{overflow-wrap:anywhere}figure{margin:24px 0}img{width:100%}figcaption{color:#555;font-size:14px}</style><body>'
        + "".join(blocks)
        + "</body></html>"
    )
    (root / "reports/论文参数三组验证报告.html").write_text(page)
    print(json.dumps({key: value["mean_relative_l2"] for key, value in evidence.items()}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    while args.wait:
        status = json.loads((args.root / "batch.json").read_text())
        if status["status"] == "finished":
            if any(item["exit_code"] for item in status["finished"]):
                raise SystemExit("训练失败，保留日志，不发布完成报告")
            break
        time.sleep(5)
    report(args.root)
