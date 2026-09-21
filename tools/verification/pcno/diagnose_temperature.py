"""只增加观察的原版非有限梯度定位，不修改源码或科学运算。"""

import argparse
import json
import sys
from pathlib import Path

import torch

from tools.verification.pcno.reference import Observer, adapt


class InvalidGradient(Exception):
    pass


class Diagnostic(Observer):
    def gradient(self, scope):
        super().gradient(scope)
        bad = [
            k
            for k, p in scope["model"].named_parameters()
            if p.grad is not None and not torch.isfinite(p.grad).all()
        ]
        if bad:
            self.save("before-invalid.pt", self.state(scope))
            report = {
                "next_update": self.updates + 1,
                "sample": f"{Path(scope['train_paths'][scope['idx'] - 1]).stem}/{scope['i']}",
                "bad_parameters": bad,
                "temperature_min": float(scope["pred_T_raw"].min()),
                "temperature_max": float(scope["pred_T_raw"].max()),
            }
            (self.output / "invalid.json").write_text(json.dumps(report, indent=2))
            raise InvalidGradient()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("data", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(a.source))
    torch.set_num_threads(4)
    o = Diagnostic(a.output)
    tree = adapt((a.source / "PCNO_Train_4D.py").read_text(), a.data, a.output, "temp")
    try:
        exec(compile(tree, "observed-original", "exec"), {"__name__": "__main__", "_observer": o})  # noqa: S102 -- 执行已固定的用户本地源码及显式AST修正
    except InvalidGradient:
        o.status(state="invalid_gradient_observed")


if __name__ == "__main__":
    main()
