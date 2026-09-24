"""物化既有完整 example 后叠加本地研究组件；仅创建独立主控验证目录。"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import ai4e_task
import yaml


def materialize(root, source):
    """复制 WDNO 时序流程与冻结目标材料；不读取隐藏测试。"""
    root, source = Path(root).resolve(), Path(source).resolve()
    root.mkdir(parents=True, exist_ok=True)
    case = root / "case"
    if not case.exists():
        receipt = ai4e_task.copy_example("wdno.burgers_base", case)
        (root / "base-copy-receipt.json").write_text(json.dumps(receipt, indent=2))
    if not (root / "base-example").exists():
        shutil.copytree(case, root / "base-example")
    overlay = Path(__file__).parent / "overlay"
    for path in overlay.glob("*.py"):
        shutil.copy2(path, case / path.name)
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copy2(source / "baseline/source/model.py", case / "baseline_model.py")
    shutil.copy2(source / "baseline/initial-checkpoint.pt", assets / "initial.pt")
    shutil.copy2(source / "round-05/submission/model.py", case / "residual_model.py")
    shutil.copy2(source / "round-05/submission/checkpoint.pt", assets / "final-reference.pt")
    config = {
        "run_root": "../records",
        "data_root": "../data",
        "pipeline": {"stages": ["rawprep", "trainprep", "train", "infer", "post"]},
        "inputs": {
            "rawprep": {
                "source": str(source / "data"),
                "manifest": str(source / "data/manifest.json"),
            },
            "trainprep": {"physical": None},
            "train": {"preparation": None, "initial": "../assets/initial.pt", "resume": None},
            "infer": {"preparation": None, "checkpoint": None},
            "post": {"predictions": None},
        },
        "science": {
            "fields": ["Psi", "u", "zj", "omega", "rho", "T"],
            "history": 10,
            "future": 40,
            "threads": 6,
        },
        "model": {},
        "train": {
            "updates": 2500,
            "batch_size": 16,
            "seed": 42,
            "device": "mps",
            "learning_rate": 0.001,
            "evaluate_every": 50,
            "mixed": False,
            "relative_objective": False,
            "ema": None,
            "snapshot": True,
        },
        "infer": {"device": "mps"},
        "components": {
            "reader": "local_data.JorekSource",
            "statistics": "local_data.fit_normalization",
            "model": "baseline_model.UNet",
            "optimizer": "torch.optim.Adam",
            "stream": "local_training.WindowStream",
            "batch": "local_training.WindowBatch",
            "objective": "local_training.block_mse",
            "advance": "local_training.predict_blocks",
            "post": "local_post.fixed_errors",
        },
    }
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    (case / "README.md").write_text("""# JOREK 六场 U-Net：Dojo 用户组件实跑

本目录实际由 wdno.burgers_base 完整复制后改写，pipeline.py 保留；数据、网络和训练语义已换成冻结 JOREK 协议，不是 WDNO 算法。
配置在 config.yaml，阶段正文明确 rawprep → trainprep → train → infer → post；本地组件位于 local_*.py。
从本目录用 uv run --no-sync python pipeline.py 启动，依赖由调用方已安装的 Dojo/torch/h5py/numpy 提供。可以使用 --set 点号覆盖。
这是主控工程验证，只有 train/validation 原始发布数据，未执行隐藏评分或新五轮实验。baseline_model 与 residual_model 是目标参考，不计作既有 Dojo 组件。
""")
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in case.glob("*.py")}
    (root / "materialization.json").write_text(
        json.dumps(
            {
                "base": "wdno.burgers_base",
                "source_experiment": str(source),
                "source_files": files,
                "pipeline_byte_identical": (case / "pipeline.py").read_bytes()
                == (root / "base-example/pipeline.py").read_bytes(),
                "scope": "main-controller engineering proof; training and validation only; no formal isolated agent",
            },
            indent=2,
        )
    )
    return case


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print(materialize(args.root, args.source))
