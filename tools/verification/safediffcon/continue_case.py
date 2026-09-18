"""执行已冻结的双侧续训方案；逐阶段监督，最后验证全部50样本。"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tools.verification.safediffcon.budget import phase_limits


def execute(root: Path, case: str, total: int) -> None:
    """仅消费已冻结配置和原账本，任一步失败即停止该案例。"""
    repository = Path(__file__).resolve().parents[3]
    work = root / "continuation"
    frozen = json.loads((work / f"{case}-training-freeze.json").read_text())
    if total != frozen["total"]:
        raise ValueError("更新总数与冻结方案不符")
    ledger = root / "budget" / f"{case}.json"
    interpreter = root / "environments/reference/bin/python"
    base = ["uv", "run", "--no-project", "--python", str(interpreter), "python"]
    # 安装入口由调用方显式选择，不静默切回历史安装副本。
    configs = {}
    for side in ["reference", "dojo"]:
        config = work / f"{case}-{side}-{total}.yaml"
        if hashlib.sha256(config.read_bytes()).hexdigest() != frozen[side + "_config_sha256"]:
            raise ValueError("冻结配置改变")
        import yaml

        from ai4e_contrib.application.pde_control.safediffcon.migration import migrate_legacy

        converted = migrate_legacy(yaml.safe_load(config.read_text()), base=config.parent)
        current = work / f"{case}-{side}-{total}-public.yaml"
        with current.open("x") as stream:
            yaml.safe_dump(converted, stream, sort_keys=False)
        configs[side] = current

    def run(label, command, seconds, reserve):
        phase_limits(ledger, seconds=seconds, reserve=reserve)
        # stdout 由子进程自行落日志；监督器保留真实命令并负责整个进程组。
        with (work / f"{label}.log").open("x") as log:
            wrapper = base + [
                "-c",
                "import subprocess,sys;raise SystemExit(subprocess.call(sys.argv[1:]))",
                *command,
            ]
            # 将监督器运行放到独立包装进程，日志重定向只影响当前阶段。
            supervisor = [
                "uv",
                "run",
                "--no-sync",
                "python",
                "-m",
                "tools.verification.safediffcon.budget",
                "--ledger",
                str(ledger),
                "--seconds",
                str(seconds),
                "--reserve",
                str(reserve),
                "--",
                *wrapper,
            ]
            result = subprocess.run(
                supervisor, cwd=repository, stdout=log, stderr=subprocess.STDOUT, check=False
            )
        if result.returncode:
            raise RuntimeError(f"{label} 失败，检查日志；同一账本保留耗时")
        print(f"{label}: complete", flush=True)

    for side in ["reference", "dojo"]:
        label = f"{case}-{side}-{total}-pretrain"
        command = base + [
            str(repository / "tools/verification/safediffcon/compare.py"),
            "--config",
            str(configs[side]),
            "--snapshot",
            str(root / "admission/20260916/source"),
            "--side",
            side,
            "--pretrain-only",
            "--output",
            str(work / label),
        ]
        run(
            label, command, 1800 if case == "burgers" else 2400, 2100 if case == "burgers" else 2340
        )
    for side in ["reference", "dojo"]:
        label = f"{case}-{side}-{total}-final"
        command = base + [
            str(repository / "tools/verification/safediffcon/compare.py"),
            "--config",
            str(configs[side]),
            "--snapshot",
            str(root / "admission/20260916/source"),
            "--side",
            side,
            "--independent-stages",
            "--pretrained-summary",
            str(work / f"{case}-{side}-{total}-pretrain/summary.json"),
            "--output",
            str(work / label),
        ]
        run(label, command, 1200, 600)
    command = base + [
        str(repository / "tools/verification/safediffcon/acceptance.py"),
        "--case",
        case,
        "--reference",
        str(work / f"{case}-reference-{total}-final/summary.json"),
        "--dojo",
        str(work / f"{case}-dojo-{total}-final/summary.json"),
        "--output",
        str(work / f"{case}-final-acceptance.json"),
    ]
    run(f"{case}-final-acceptance", command, 120, 300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--case", choices=["burgers", "tokamak"], required=True)
    parser.add_argument("--total", type=int, required=True)
    args = parser.parse_args()
    execute(args.root, args.case, args.total)
