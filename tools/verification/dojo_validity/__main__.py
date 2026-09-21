"""Neumann 实验工具：准备、独立环境、命令探针、调度、评价和汇总。"""

import argparse
from pathlib import Path

from .baseline import measure_baseline, verify_baseline
from .environment import install_environment
from .io import read_json
from .isolation import probe_commands
from .metrics import evaluate
from .prepare import prepare_pair
from .runner import run, summarize


def main():
    """解析明确路径；正式 run 必须经会话隔离 gate，无不受控回退。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--base", type=Path, required=True)
    prep.add_argument("--reference-source", type=Path, required=True)
    env = sub.add_parser("environment")
    env.add_argument("--experiment", type=Path, required=True)
    probe = sub.add_parser("probe")
    probe.add_argument("--experiment", type=Path, required=True)
    probe.add_argument("--codex", required=True)
    probe.add_argument("--forbidden", type=Path, action="append", required=True)
    execute = sub.add_parser("run")
    execute.add_argument("--experiment", type=Path, required=True)
    execute.add_argument("--truth", type=Path, required=True)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--experiment", type=Path, required=True)
    baseline.add_argument("--truth", type=Path, required=True)
    baseline.add_argument("--epochs", type=int, default=5000)
    verify = sub.add_parser("verify-baseline")
    verify.add_argument("--baseline", type=Path, required=True)
    verify.add_argument("--output", type=Path, required=True)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--predictions", type=Path, required=True)
    ev.add_argument("--truth", type=Path, required=True)
    ev.add_argument("--output", type=Path, required=True)
    summary = sub.add_parser("summarize")
    summary.add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "prepare":
        print(prepare_pair(args.base, args.reference_source))
    elif args.action == "environment":
        protocol = read_json(args.experiment / "protocol.json")
        print(install_environment(args.experiment, dojo=protocol["group"] == "dojo"))
    elif args.action == "probe":
        protocol = read_json(args.experiment / "protocol.json")
        print(
            probe_commands(
                args.codex,
                protocol["session_workspace_root"],
                args.forbidden,
                args.experiment / "evidence/command-isolation.json",
            )
        )
    elif args.action == "run":
        from .formal import CliRunner, evaluator

        protocol = read_json(args.experiment / "protocol.json")
        run(args.experiment, CliRunner(), evaluator(protocol, args.truth))
    elif args.action == "baseline":
        print(measure_baseline(args.experiment, args.truth, epochs=args.epochs)["status"])
    elif args.action == "verify-baseline":
        print(verify_baseline(args.baseline, args.output))
    elif args.action == "evaluate":
        print(evaluate(args.predictions, args.truth, args.output))
    else:
        from .finish import seal

        config = read_json(args.comparison / "comparison-protocol.json")
        if all(
            (Path(location) / "final/selection.json").exists()
            for location in config["experiments"].values()
        ):
            print(seal(args.comparison)["status"])
        else:
            print(summarize(args.comparison)["status"])


if __name__ == "__main__":
    main()
