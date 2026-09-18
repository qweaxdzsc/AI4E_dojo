"""接续当前原版对照后，在同一账本串行执行 Dojo 训练、预测和比较。"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--installed", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    ledger = root / "budget.json"
    reference = root / "reference-current-2"
    dojo = root / "dojo-final"
    # 此等待只衔接本次正在执行的任务，不创建定时任务或后续自动重跑。
    while any(x["status"] == "running" for x in json.loads(ledger.read_text())["runs"]):
        time.sleep(2)
    source = json.loads((reference / "result.json").read_text())
    if source["status"] != "slice_complete" or source["updates"] != 2000:
        raise RuntimeError("原版未完成，停止扩大计算")
    cfg = yaml.safe_load((dojo / "config.yaml").read_text())
    resume = cfg["infer"]["checkpoint"]
    env = {**os.environ, "PYTHONPATH": str(args.installed.resolve()) + os.pathsep + str(Path.cwd())}
    for stage in ("train", "infer", "compare"):
        command = [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-m",
            "tools.verification.wdno.budget",
            "--ledger",
            str(ledger),
            "--",
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-m",
            "tools.verification.wdno.migration",
            stage,
            "--root",
            str(dojo),
            "--reference",
            str(reference),
        ]
        if stage == "train":
            command += ["--updates", "2000", "--resume", resume]
        with (dojo / f"{stage}-formal-console.txt").open("w") as output:
            result = subprocess.run(
                command, env=env, stdout=output, stderr=subprocess.STDOUT, check=False
            )
        if result.returncode:
            raise RuntimeError(f"{stage} 失败，见 {dojo / (stage + '-formal-console.txt')}")
        print(stage, "completed", flush=True)


if __name__ == "__main__":
    main()
