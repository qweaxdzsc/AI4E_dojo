"""已授权的快速参考切片：保留250轮原调度，仅在明确更新边界结束。"""

import argparse
import json
import sys
from pathlib import Path

import torch

from tools.verification.pcno.reference import Observer, adapt, digest


class SliceComplete(Exception):
    """明确完成短切片预算，不表示原250轮训练完成。"""


class SliceObserver(Observer):
    def __init__(self, output, updates):
        super().__init__(output)
        self.target = updates

    def step(self, scope):
        super().step(scope)
        if self.updates == self.target:
            self.save("slice.pt", self.state(scope))
            raise SliceComplete()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "data", "output"]:
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--branch", choices=["pres", "temp"], required=True)
    parser.add_argument("--updates", type=int, default=21)
    parser.add_argument("--stable-vis", action="store_true", help="显式应用未选黏度分支数值修正")
    args = parser.parse_args()
    if not 1 <= args.updates <= 42:
        raise ValueError("本快速切片只执行最多两轮，不启动长训练")
    args.output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.source.resolve()))
    if args.stable_vis:
        import PCNO_Model_4D

        from tools.verification.pcno.numerical_repair import apply_to_source_module

        apply_to_source_module(PCNO_Model_4D)
    source = args.source / "PCNO_Train_4D.py"
    tree = adapt(source.read_text(), args.data.resolve(), args.output.resolve(), args.branch)
    observer = SliceObserver(args.output, args.updates)
    (args.output / "identity.json").write_text(
        json.dumps(
            {
                "source_sha256": digest(source),
                "branch": args.branch,
                "updates": args.updates,
                "schedule_epochs": 250,
                "stable_vis": args.stable_vis,
                "scope": "short integration check, not paper reproduction",
            },
            indent=2,
        )
    )
    try:
        exec(compile(tree, str(source), "exec"), {"__name__": "__main__", "_observer": observer})  # noqa: S102
    except SliceComplete:
        observer.status(state="slice_complete", target_updates=args.updates)


if __name__ == "__main__":
    main()
