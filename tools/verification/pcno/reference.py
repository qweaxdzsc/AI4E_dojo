"""PCNO 原仓库透明参考入口：仅适配路径、分支、CPU 与无随机观察。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
import resource
import sys
import time
import traceback
from pathlib import Path


def digest(path):
    """流式计算文件身份，不修改来源。"""
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def adapt(source, data, output, branch):
    """保留科学表达式，仅重定位来源/检查点并插入观察点。"""
    tree = ast.parse(source)

    class Adapter(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and node.value.startswith("/data"):
                target = (
                    output
                    if node.value == "/data" or node.value.startswith("/data/MODEL_")
                    else data
                )
                return ast.copy_location(ast.Constant(str(target) + node.value[5:]), node)
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if ast.unparse(node.func) == "torch.device":
                node.args = [ast.Constant("cpu")]
            for kw in node.keywords:
                if kw.arg == "train_mode":
                    kw.value = ast.Constant(branch)
            return node

        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if node.name == "train":
                node.body.insert(0, ast.parse("_observer.start(locals())").body[0])
            return node

        def visit_For(self, node):
            self.generic_visit(node)
            if isinstance(node.target, ast.Name) and node.target.id == "ep":
                node.iter.args[0] = ast.parse("_observer.first_epoch", mode="eval").body
                node.body.insert(0, ast.parse("_observer.begin_epoch(locals())").body[0])
                node.body.append(ast.parse("_observer.epoch(locals())").body[0])
            return node

        def visit_Expr(self, node):
            self.generic_visit(node)
            if (
                isinstance(node.value, ast.Call)
                and ast.unparse(node.value.func) == "scheduler.step"
            ):
                return [node, ast.parse("_observer.step(locals())").body[0]]
            if isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == "loss.backward":
                return [node, ast.parse("_observer.gradient(locals())").body[0]]
            return node

    return ast.fix_missing_locations(Adapter().visit(tree))


class Observer:
    """记录完整首步、每次损失与轮次状态，不改变随机流和张量。"""

    def __init__(self, output, resume=None):
        self.output = output
        self.started = time.monotonic()
        self.updates = 0
        self.resume = resume
        self.first_epoch = 1

    def status(self, **values):
        values.update(
            updates=self.updates,
            elapsed_seconds=time.monotonic() - self.started,
            peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        )
        path = self.output / "status.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(values, indent=2, allow_nan=False))
        tmp.replace(path)

    def save(self, name, value):
        import torch

        path = self.output / name
        tmp = path.with_suffix(".tmp")
        torch.save(value, tmp)
        tmp.replace(path)

    def start(self, scope):
        if self.resume is not None:
            import random

            import numpy as np
            import torch

            state = torch.load(self.resume, map_location="cpu", weights_only=False)
            required = {
                "model",
                "optimizer",
                "scheduler",
                "epoch",
                "updates",
                "paths",
                "random",
                "numpy",
                "torch",
            }
            if not required.issubset(state):
                raise ValueError(
                    "Not a complete epoch-boundary checkpoint; author weights alone cannot resume"
                )
            paths = {Path(p).name: p for p in scope["all_paths"]}
            if set(paths) != set(state["paths"]) or len(state["paths"]) != len(paths):
                raise ValueError("Resume chunk identities differ")
            if state["updates"] != state["epoch"] * 21 or not 0 <= state["epoch"] <= 250:
                raise ValueError("Checkpoint is not a completed 21-update epoch")
            scope["model"].load_state_dict(state["model"])
            scope["optimizer"].load_state_dict(state["optimizer"])
            scope["scheduler"].load_state_dict(state["scheduler"])
            scope["all_paths"][:] = [paths[name] for name in state["paths"]]
            random.setstate(state["random"])
            np.random.set_state(state["numpy"])
            torch.set_rng_state(state["torch"])
            self.updates = state["updates"]
            self.first_epoch = state["epoch"] + 1
            self.save("imported.pt", state)
            self.status(state="running", epoch=state["epoch"], resume=str(self.resume))
            return
        self.save("initial.pt", scope["model"].state_dict())
        self.status(state="running", epoch=0)

    def begin_epoch(self, scope):
        self.epoch_started = time.monotonic()
        self.status(state="running", epoch=scope["ep"])

    def gradient(self, scope):
        if self.updates == 0:
            self.save(
                "first-gradient.pt", {k: p.grad for k, p in scope["model"].named_parameters()}
            )

    def state(self, scope):
        import random

        import numpy as np
        import torch

        return {
            "model": scope["model"].state_dict(),
            "optimizer": scope["optimizer"].state_dict(),
            "scheduler": scope["scheduler"].state_dict(),
            "epoch": scope["ep"],
            "updates": self.updates,
            "paths": [Path(p).name for p in scope["all_paths"]],
            "random": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
        }

    def step(self, scope):
        self.updates += 1
        record = {
            name: scope[name].item()
            for name in ("loss", "mse_loss", "grad_loss", "weighted_loss", "loss_phys", "loss_task")
        }
        record.update(
            epoch=scope["ep"],
            update=self.updates,
            sample=f"{Path(scope['train_paths'][scope['idx'] - 1]).stem}/{scope['i']}",
            lr=scope["scheduler"].get_last_lr()[0],
            elapsed_seconds=time.monotonic() - self.started,
        )
        with (self.output / "updates.jsonl").open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")
        if self.updates == 1:
            self.save("first-update.pt", self.state(scope))
            self.save("first-prediction.pt", scope["pred_value"].detach())
        self.status(state="running", epoch=scope["ep"], last=record)

    def epoch(self, scope):
        self.save("latest.pt", self.state(scope))
        values = {
            "state": "running",
            "epoch": scope["ep"],
            "epoch_seconds": time.monotonic() - self.epoch_started,
            "loss": scope["avg_total_loss"],
            "validation": scope.get("avg_val_loss")
            if scope["ep"] >= 30 and scope["ep"] % 5 == 0
            else None,
        }
        with (self.output / "epochs.jsonl").open("a") as stream:
            stream.write(json.dumps(values, allow_nan=False) + "\n")
        self.status(**values)


def main():
    """执行固定 250 轮参考实验；已有输出目录拒绝覆盖。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--branch", choices=["pres", "temp"], required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument(
        "--resume", type=Path, help="Complete observed checkpoint; writes a new run directory"
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    import torch

    sys.dont_write_bytecode = True
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    paths = sorted(args.data.glob("chunk_*.pt"))
    if len(paths) != 8:
        raise ValueError("Reference requires eight published chunks")
    identity = {
        "branch": args.branch,
        "epochs": 250,
        "modes": [1] * 4,
        "width": 8,
        "device": "cpu",
        "threads": args.threads,
        "python": sys.version,
        "packages": {
            k: importlib.metadata.version(k) for k in ["torch", "numpy", "scipy", "pandas", "iapws"]
        },
        "source": {p.name: digest(p) for p in args.source.iterdir() if p.is_file()},
        "data": {p.name: digest(p) for p in args.data.iterdir() if p.is_file()},
        "adaptations": [
            "read-only data path remapping",
            "checkpoint output remapping",
            "CPU selection",
            "explicit branch construction and training",
            "RNG-free observations before clipping, after update, at epoch end",
        ],
    }
    if args.resume:
        previous = json.loads((args.resume.parent / "identity.json").read_text())
        for key in (
            "branch",
            "epochs",
            "modes",
            "width",
            "device",
            "threads",
            "python",
            "packages",
            "source",
            "data",
        ):
            if previous[key] != identity[key]:
                raise ValueError(f"Resume identity differs: {key}")
        identity["resume"] = {"path": str(args.resume.resolve()), "sha256": digest(args.resume)}
    (args.output / "identity.json").write_text(json.dumps(identity, indent=2))
    (args.output / "observer-source.py").write_text(Path(__file__).read_text())
    source = (args.source / "PCNO_Train_4D.py").read_text()
    tree = adapt(source, args.data.resolve(), args.output.resolve(), args.branch)
    (args.output / "adapted-trainer.py").write_text(ast.unparse(tree) + "\n")
    sys.path.insert(0, str(args.source.resolve()))
    observer = Observer(args.output, args.resume)
    try:
        exec(  # noqa: S102 — 显式授权的本地作者源码，摘要与适配后源码已保存。
            compile(tree, str(args.source / "PCNO_Train_4D.py"), "exec"),
            {"__name__": "__main__", "_observer": observer},
        )
        observer.status(state="complete", epoch=250)
    except BaseException:
        observer.status(state="failed", traceback=traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
