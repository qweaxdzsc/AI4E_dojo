"""在真实安装解释器中串行验证完整复制案例与Task worker。"""

import argparse
import json
import os
from pathlib import Path

from .budget import DEFAULT_LEDGER, Budget
from .run_acceptance import ROOT, WORK


def main():
    """三个独立工作目录，全部计算进入主预算；不修改正式运行环境。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=WORK / "installed-replay")
    args = parser.parse_args()
    paths = json.loads((WORK / "implementation/preparations.json").read_text())
    python = WORK / "installed/venv/bin/python"
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
    env["OMP_NUM_THREADS"] = "4"
    budget = Budget(DEFAULT_LEDGER)
    for case, extension in [("darcy", False), ("bumper_beam", False), ("darcy", True)]:
        label = case + ("-extension" if extension else "")
        root = args.root / label
        command = [
            "uv",
            "run",
            "--no-project",
            "--python",
            str(python),
            "python",
            str(ROOT / "tools/verification/geotransolver/task_replay.py"),
            "--case",
            case,
            "--preparation",
            paths[case],
            "--root",
            str(root),
        ]
        if extension:
            command.append("--extension")
        if budget.run(command, label="installed-task-" + label, training=True, env=env):
            raise RuntimeError(label)


if __name__ == "__main__":
    main()
