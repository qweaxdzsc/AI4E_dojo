"""历史2000步产物经新旧隔离入口各续1步，固定首批预测严格比较。"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import torch
import yaml

from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from tools.verification.wdno.task_replay import assert_equal

REPO = Path(__file__).resolve().parents[3]


def execute(code, config, stage, installed):
    path = code / "config.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False))
    process = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(code / f"{stage}.py"),
        ],
        cwd=code.parent,
        env={**os.environ, "PYTHONPATH": str(installed)},
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    (code.parent / f"{stage}-console.txt").write_text(process.stdout + process.stderr)
    if process.returncode:
        raise AssertionError(process.stdout + process.stderr)
    path = max(Path(config["run_root"]).glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns)
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--installed", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    original = yaml.safe_load((args.root / "dojo-final/config.yaml").read_text())
    old = deepcopy(original)
    old["train"].update(resume=original["infer"]["checkpoint"], updates=2001)
    old["run_root"] = str(args.output / "old/runs")
    old["data"]["output"] = str(args.output / "old/data")
    # 只缩小评价，不改训练清单/合同；首批固定16保证采样随机序列相同。
    for split in ("validation", "test"):
        record, arrays = read_arrays(
            old["data"]["prepared"][split], kind="spatiotemporal-physical-v1"
        )
        old["data"]["prepared"][split] = save_arrays(
            args.output / "evaluation" / split,
            {k: v[:16] for k, v in arrays.items()},
            kind="spatiotemporal-physical-v1",
            metadata=record["metadata"],
        )
    new = migrate_legacy(old, base=args.root / "dojo-final")
    new["run_root"], new["data_root"] = str(args.output / "new/runs"), str(args.output / "new/data")
    for side, origin in (("old", args.root / "dojo-final/recipe"), ("new", REPO / "recipes/wdno")):
        shutil.copytree(
            origin, args.output / side / "recipe", ignore=shutil.ignore_patterns("__pycache__")
        )
    old_install = args.root.parent / "installed-final"
    summaries = {}
    for side, config, installed in (("old", old, old_install), ("new", new, args.installed)):
        trained = execute(args.output / side / "recipe", config, "train", installed)
        checkpoint = trained["reports"]["train"]["checkpoint"]
        if side == "old":
            config["infer"]["checkpoint"] = checkpoint
        else:
            config["inputs"]["infer"]["checkpoint"] = checkpoint
        inferred = execute(args.output / side / "recipe", config, "infer", installed)
        summaries[side] = {"train": trained, "infer": inferred}
    states = [
        torch.load(
            summaries[s]["train"]["reports"]["train"]["checkpoint"],
            map_location="cpu",
            weights_only=False,
        )
        for s in ("old", "new")
    ]
    for key in (
        "model",
        "optimizer",
        "ema",
        "scheduler",
        "stream",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "mps_rng",
        "history",
        "updates",
        "contract",
    ):
        assert_equal(states[0][key], states[1][key])
    assert states[0]["updates"] == 2001 and len(states[0]["history"]) == 2001
    results = {}
    for split in ("validation", "test"):
        _, first = read_arrays(
            summaries["old"]["infer"]["reports"]["infer"][split], kind="spatiotemporal-result-v1"
        )
        _, second = read_arrays(
            summaries["new"]["infer"]["reports"]["infer"][split], kind="spatiotemporal-result-v1"
        )
        assert_equal(first, second)
        results[split] = {
            "samples": len(first["ids"]),
            "max_abs": float(np.max(np.abs(first["prediction"] - second["prediction"]))),
        }
    (args.output / "acceptance.json").write_text(
        json.dumps(
            {
                "passed": True,
                "resume_from": 2000,
                "updates": 2001,
                "checkpoint_contract_equal": True,
                "training_states_equal": True,
                "evaluation": results,
                "original_config": str(args.root / "dojo-final/config.yaml"),
                "summaries": summaries,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
