"""RMHD 主控命令，Neumann 旧入口保持原样；任何正式 run 都先过启动门槛。"""

import argparse
from pathlib import Path

from ..io import read_json, write_json
from .controller import evaluate_hidden, freeze_environment, run_pair
from .evaluate import evaluator_for
from .materials import prepare_groups
from .preflight import run_preflight
from .protocol import prepare_private
from .sessions import CliDriver
from .verification import verify_startup


def main():
    """显式主控路径，组 run 不接收 --truth 参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--base", type=Path, required=True)
    prepare.add_argument("--data-root", type=Path, required=True)
    for name in ("preflight", "materials", "probe", "run", "evaluate", "summarize"):
        sub.add_parser(name).add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "prepare":
        print(prepare_private(args.base, args.data_root))
    elif args.action == "preflight":
        print(run_preflight(args.comparison)["gate"])
    elif args.action == "materials":
        print(prepare_groups(args.comparison))
    elif args.action == "probe":
        print({k: v["passed"] for k, v in verify_startup(args.comparison).items()})
    elif args.action == "run":
        run_pair(args.comparison, CliDriver(args.comparison))
    elif args.action == "evaluate":
        state = read_json(args.comparison / "state.json")
        if state["phase"] not in {"both_finals_locked", "hidden_evaluating"}:
            raise ValueError("双方最终冻结前禁止进入隐藏评价")
        config = read_json(args.comparison / "comparison-protocol.json")
        for group, location in config["experiments"].items():
            destination = args.comparison / "frozen-environments" / group
            if not destination.exists():
                # 只复制环境到主控；worker 不能访问可变实验根。系统解释器链接物化为文件。
                files = freeze_environment(
                    Path(location) / "environment", destination, config["runtime_readonly_roots"]
                )
                write_json(args.comparison / "evidence" / f"{group}-frozen-environment.json", files)
        evaluate_hidden(args.comparison, evaluator_for(args.comparison))
    else:
        from .report import summarize

        print(summarize(args.comparison)["status"])


if __name__ == "__main__":
    main()
