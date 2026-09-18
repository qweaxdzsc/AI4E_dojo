"""通过可复制 recipe 执行迁移验收；不实现另一套训练或采样循环。"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

from tools.verification.wdno.protocol import digest, write_json

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "train", "infer", "compare"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--updates", type=int, default=2000)
    parser.add_argument("--resume", default=None)
    args = parser.parse_args()
    directory = args.root.resolve()
    code = directory / "recipe"
    if not code.exists():
        shutil.copytree(ROOT / "recipes/wdno", code, ignore=shutil.ignore_patterns("__pycache__"))
    sys.path.insert(0, str(code))
    from configuration import load_configuration
    from infer import infer
    from post import post
    from rawprep import rawprep
    from train import train
    from trainprep import trainprep

    from ai4e_core import run
    from ai4e_core.abilities.data.save.array_manifest import read_arrays

    config = directory / "config.yaml"
    if not config.exists():
        cfg = load_configuration(code / "config.yaml")
        cfg["run_root"] = str(directory / "runs")
        cfg["data_root"] = str(directory / "data")
        config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    cfg = load_configuration(config)
    protocol = json.loads(Path(cfg["inputs"]["rawprep"]["source"]).read_text())
    if args.stage in ("train", "infer", "compare"):
        for key, actual in {
            "seed": cfg["seed"],
            "batch_size": cfg["train"]["batch_size"],
            "dim": cfg["model"]["dim"],
            "groups": cfg["model"]["groups"],
            "dim_mults": cfg["model"]["dim_mults"],
            "learning_rate": cfg["train"]["lr"],
            "sampling_steps": cfg["model"]["ddim_steps"],
            "device": cfg["train"]["device"],
        }.items():
            if actual != protocol[key]:
                raise ValueError(f"对照参数与冻结协议不同: {key}")
        if digest(cfg["inputs"]["rawprep"]["indices"]) != protocol["indices_sha256"]:
            raise ValueError("对照样本名单与冻结协议不同")
    if args.stage == "prepare":

        def prepare(current):
            physical = run.stage("rawprep", rawprep, current)
            return run.stage("trainprep", trainprep, current, physical)

        selected, stages = prepare, ["rawprep", "trainprep"]
    elif args.stage == "train":
        cfg["train"].update(updates=args.updates)
        cfg["inputs"]["train"]["resume"] = args.resume
        selected, stages = lambda current: run.stage("train", train, current), ["train"]
    elif args.stage == "infer":

        def predict(current):
            results = run.stage("infer", infer, current)
            return run.stage("post", post, current, results)

        selected, stages = predict, ["infer", "post"]
    else:
        source = torch.load(
            args.reference / "checkpoints/latest.pt", map_location="cpu", weights_only=False
        )
        state = torch.load(
            cfg["inputs"]["infer"]["checkpoint"], map_location="cpu", weights_only=False
        )
        if source["step"] != 2000 or state["updates"] != 2000:
            raise AssertionError("完整对照要求双方各完成2000更新")
        if set(source["model"]) != set(state["model"]):
            raise AssertionError("两侧模型状态字段不同")

        def same_tree(a, b):
            if isinstance(a, torch.Tensor):
                return isinstance(b, torch.Tensor) and torch.equal(a, b)
            if isinstance(a, dict):
                return (
                    isinstance(b, dict)
                    and a.keys() == b.keys()
                    and all(same_tree(a[k], b[k]) for k in a)
                )
            if isinstance(a, (list, tuple)):
                return (
                    type(a) is type(b)
                    and len(a) == len(b)
                    and all(same_tree(x, y) for x, y in zip(a, b))
                )
            return a == b

        optimizer_equal = same_tree(source["opt"], state["optimizer"])
        max_abs = max(
            float((source["model"][key] - value).abs().max())
            for key, value in state["model"].items()
        )
        losses = json.loads((args.reference / "losses.json").read_text())
        loss_error = float(np.max(np.abs(np.array([x["loss"] for x in losses]) - state["history"])))
        ema_error = max(
            float((source["ema"][key].to(torch.float64) - value.to(torch.float64)).abs().max())
            for key, value in state["ema"].items()
        )
        report = {
            "updates": state["updates"],
            "parameters_max_abs": max_abs,
            "loss_max_abs": loss_error,
            "ema_max_abs": ema_error,
            "optimizer_equal": optimizer_equal,
            "source_checkpoint_sha256": digest(args.reference / "checkpoints/latest.pt"),
            "dojo_checkpoint_sha256": digest(cfg["inputs"]["infer"]["checkpoint"]),
            "torch": torch.__version__,
            "paper_reproduced": False,
            "evaluation": {},
        }
        del state, source
        for split, path in cfg["inputs"]["post"].items():
            _, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
            with np.load(args.reference / f"{split}-results.npz") as original:
                np.testing.assert_array_equal(arrays["ids"], original["ids"])
                truth = arrays["target"][:, 1:]
                mse = ((arrays["prediction"][:, 1:] - truth) ** 2).mean(
                    axis=(1, 2), dtype=np.float32
                )
                error = float(np.max(np.abs(arrays["prediction"] - original["prediction"])))
                report["evaluation"][split] = {
                    "samples": len(mse),
                    "mse": float(np.mean(mse.tolist())),
                    "reference_mse": float(np.mean(original["mse"])),
                    "prediction_max_abs": error,
                    "forcing_max_abs": float(
                        np.max(np.abs(arrays["forcing"] - original["forcing"]))
                    ),
                    "target_max_abs": float(np.max(np.abs(arrays["target"] - original["target"]))),
                }
        report["passed"] = (
            max_abs == 0
            and loss_error == 0
            and ema_error == 0
            and optimizer_equal
            and all(
                x["prediction_max_abs"] == 0
                and x["target_max_abs"] == 0
                and x["forcing_max_abs"] == 0
                for x in report["evaluation"].values()
            )
        )
        write_json(directory / "comparison.json", report)
        if not report["passed"]:
            raise AssertionError("严格数值对照未通过，见 comparison.json")
        return
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    code_status = run.run_recipe(
        cfg,
        stages=selected,
        script=code / f"{'pipeline' if args.stage == 'prepare' else args.stage}.py",
        only=stages,
        source_config=config,
    )
    summary_path = max(
        (directory / "runs").glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns
    )
    summary = json.loads(summary_path.read_text())
    write_json(directory / f"{args.stage}-summary.json", summary)
    if code_status:
        raise RuntimeError("recipe 阶段失败：" + str(summary_path))
    reports = summary["reports"]
    if args.stage == "prepare":
        cfg["inputs"]["trainprep"] = {
            "dataset": reports["rawprep"]["train"],
            **{k: reports["rawprep"][k] for k in ("validation", "test")},
        }
        for stage in ("train", "infer"):
            cfg["inputs"][stage].update(
                preparation=reports["trainprep"]["train"],
                **{k: reports["trainprep"][k] for k in ("validation", "test")},
            )
        _, arrays = read_arrays(reports["trainprep"]["train"], kind="spatiotemporal-prepared-v1")
        original = np.load(args.reference / "train.npy", mmap_mode="r")
        max_abs = 0.0
        for start in range(0, len(original), 256):
            max_abs = max(
                max_abs,
                float(
                    np.max(
                        np.abs(
                            arrays["values"][start : start + 256] - original[start : start + 256]
                        )
                    )
                ),
            )
        write_json(
            directory / "preparation-comparison.json",
            {"max_abs": max_abs, "samples": len(original)},
        )
        if max_abs != 0:
            raise AssertionError("Dojo 与原准备不一致")
    elif args.stage == "train":
        cfg["inputs"]["infer"]["checkpoint"] = reports["train"]["checkpoint"]
    else:
        cfg["inputs"]["post"] = reports["infer"]
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))


if __name__ == "__main__":
    main()
