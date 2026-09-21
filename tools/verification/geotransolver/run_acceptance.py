"""串行计费执行成对研究，冻结准备身份与完整网格测速结论。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .budget import DEFAULT_LEDGER, Budget

ROOT = Path(__file__).resolve().parents[3]
WORK = DEFAULT_LEDGER.parent


def checked(budget, label, args, *, training=False):
    """全部子进程统一计费，失败立即停止，保留现有日志与产物。"""
    command = ["uv", "run", "--no-project", "--python", sys.executable, "python", *args]
    result = budget.run(command, label=label, training=training)
    if result:
        raise RuntimeError(f"{label} failed: {result}")


def preflight(paths):
    """先审计，再测速两套完整结构；每侧五轮只是预算估算上限。"""
    budget = Budget(DEFAULT_LEDGER)
    for case, path in paths.items():
        checked(
            budget,
            case + "-independent-preparation-audit",
            [
                "-m",
                "tools.verification.geotransolver.audit_preparation",
                "--case",
                case,
                "--raw",
                "/Users/zonghui/work/datasets/"
                + ("darcy_flow" if case == "darcy" else "bumper_beam_crash"),
                "--prepared",
                path,
                "--output",
                str(WORK / "implementation" / f"{case}-data-audit.json"),
            ],
        )
        for side in ("dojo", "reference"):
            checked(
                budget,
                case + "-" + side + "-full-network-benchmark",
                [
                    "-m",
                    "tools.verification.geotransolver.benchmark",
                    "--case",
                    case,
                    "--preparation",
                    path,
                    "--device",
                    "mps",
                    "--side",
                    side,
                    "--output",
                    str(WORK / "implementation" / f"{case}-{side}-benchmark.json"),
                ],
            )
    (WORK / "implementation/preparations.json").write_text(json.dumps(paths, indent=2) + "\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--darcy", required=True)
    p.add_argument("--bumper", required=True)
    a = p.parse_args()
    preflight({"darcy": a.darcy, "bumper_beam": a.bumper})
