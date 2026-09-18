"""共享训练执行的冻结源码对照与入口盘点；产物写到显式实验目录。"""

import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[2]


def entries(root: Path = ROOT) -> list[dict]:
    """枚举含配置的模板/案例/覆盖集，不把目录存在说成数值验收。"""
    result = []
    for section in ("recipes", "examples"):
        for config in sorted((root / section).rglob("config.yaml")):
            value = yaml.safe_load(config.read_text())
            if not isinstance(value, dict):
                raise TypeError(f"配置不是对象: {config}")
            folder = config.parent
            result.append(
                {
                    "path": str(folder.relative_to(root)),
                    "kind": "standalone" if (folder / "configuration.py").exists() else "overlay",
                    "pipeline": (folder / "pipeline.py").exists(),
                    "configuration": "parsed",
                    "handoff": "pending runtime verification",
                    "components": value.get("components", {}),
                }
            )
    return result


def validate_entries(root: Path = ROOT) -> list[dict]:
    """逐目录在独立解释器中运行实际加载器和组件解析，不启动训练。"""
    results = entries(root)
    for item in results:
        folder = root / item["path"]
        if (folder / "configuration.py").exists():
            base = folder
        elif "parametric_pde" in folder.parts:
            base = root / "recipes/parametric_pde"
        elif "gencp" in folder.parts:
            base = root / "recipes/gencp"
        elif "wdno" in folder.parts:
            base = root / "recipes/wdno"
        else:
            raise ValueError(f"缺少明确基础模板: {folder}")
        code = """import importlib, json, sys
from pathlib import Path
sys.path[:0] = sys.argv[1:3]
module = importlib.import_module('configuration')
cfg = module.load_configuration(Path(sys.argv[1]) / 'config.yaml')
resolved = []
def visit(value):
    if isinstance(value, dict):
        for child in value.values(): visit(child)
    elif isinstance(value, (list, tuple)):
        for child in value: visit(child)
    elif isinstance(value, str) and value.startswith(('ai4e_', 'variants.')):
        try: importlib.import_module(value)
        except ModuleNotFoundError as error:
            parent, name = value.rsplit('.', 1)
            getattr(importlib.import_module(parent), name)
        resolved.append(value)
visit(dict(cfg.get('components', {})))
print(json.dumps({'configuration': 'loaded', 'components_resolved': resolved}))
"""
        proc = subprocess.run(
            [sys.executable, "-B", "-c", code, str(folder), str(base)],
            cwd=root,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        item["returncode"] = proc.returncode
        if proc.returncode:
            item["handoff"] = "blocked"
            item["error"] = proc.stderr
        else:
            item.update(json.loads(proc.stdout.splitlines()[-1]))
            item["handoff"] = "configuration and components checked; numerical test separate"
    return results


def _reference(directory):
    package = types.ModuleType("dojo_training_reference")
    package.__path__ = [str(directory)]
    sys.modules[package.__name__] = package
    result = {}
    for name in ("loop", "iterations"):
        spec = importlib.util.spec_from_file_location(
            f"{package.__name__}.{name}", directory / f"{name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        result[name] = module
    return result


def _equal(a, b):
    if isinstance(a, torch.Tensor):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            _equal(a[key], b[key])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            _equal(x, y)
    else:
        assert a == b, (a, b)


def trajectory(function, *, epochs):
    """记录每次真实更新的权重、优化器、调度与EMA，保持两边同一随机输入。"""
    from ai4e_core.abilities.training.iteration_stream import IterationStream
    from ai4e_core.abilities.training.moving_average import MovingAverage

    torch.manual_seed(381)
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.7)
    ema = MovingAverage(model, 0.9)
    trace, saved = [], []
    values = torch.arange(20, dtype=torch.float32).reshape(10, 2) / 20

    def observe():
        trace.append(
            copy.deepcopy(
                {
                    "model": model.state_dict(),
                    "optimizer": optimizer.state_dict(),
                    "scheduler": scheduler.state_dict(),
                    "ema": ema.state,
                }
            )
        )

    if epochs:

        class Run:
            def checkpoint(self, name, state):
                saved.append((name, state["epoch"], state["updates"]))

        def callback(event, **kwargs):
            if event == "update":
                observe()

        report = function(
            model,
            optimizer,
            lambda e: values.split(2),
            lambda m, x: {"loss": m(x).square().mean()},
            lambda: {"loss": 1.0},
            Run(),
            config={"max_epochs": 3, "accumulate": 2, "validation_interval": 2},
            contract={},
            ema=ema,
            scheduler=scheduler,
            callbacks=[callback],
        )
        losses = [record["loss"] for record in report["history"]]
    else:
        losses = function(
            model,
            optimizer,
            IterationStream(10, 2),
            lambda ids: values[ids],
            lambda m, x: m(x).square().mean(),
            updates=6,
            ema=ema,
            scheduler=scheduler,
            after_update=lambda i, m: observe(),
            checkpoint=lambda i, h, s: saved.append((i, list(h), s)),
            evaluate_every=2,
        )
    return {"trace": trace, "losses": losses, "checkpoints": saved}


def compare(baseline: Path) -> dict:
    """读取预先冻结的原实现，与当前入口逐值对照，不重写冻结基线。"""
    from ai4e_core.abilities.training.iterations import fit_iterations
    from ai4e_core.abilities.training.loop import fit

    reference = _reference(baseline / "ai4e-core/abilities/training")
    results = {}
    for name, current, previous, epochs in (
        ("epochs", fit, reference["loop"].fit, True),
        ("updates", fit_iterations, reference["iterations"].fit_iterations, False),
    ):
        original = trajectory(previous, epochs=epochs)
        actual = trajectory(current, epochs=epochs)
        _equal(original, actual)
        results[name] = {
            "updates": len(actual["trace"]),
            "exact": True,
            "losses": actual["losses"],
            "checkpoints": actual["checkpoints"],
        }
    return results


def main():
    """输出源码对照与入口清单；入口轻量盘点不冒充模型实跑。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-entries", action="store_true")
    args = parser.parse_args()
    result = {
        "numerical": compare(args.baseline),
        "entries": validate_entries() if args.check_entries else entries(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
