"""在没有观察插桩的原训练函数上独立复放首步，验证观察器未改变数值。"""

import argparse
import ast
import json
import sys
from pathlib import Path

import torch

from tools.verification.pcno.reference import adapt, digest


class Captured(Exception):
    """首步状态已抓取后结束本次独立诊断，不是训练完成。"""


def compare(actual, expected, location="state"):
    """比较嵌套状态；浮点误差使用预先约定的固定容差。"""
    if isinstance(actual, torch.Tensor):
        torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-6, msg=location)
    elif isinstance(actual, dict):
        if actual.keys() != expected.keys():
            raise AssertionError(location + " keys differ")
        for key in actual:
            compare(actual[key], expected[key], location + "/" + str(key))
    elif isinstance(actual, (tuple, list)):
        if len(actual) != len(expected):
            raise AssertionError(location + " lengths differ")
        for i, (a, b) in enumerate(zip(actual, expected)):
            compare(a, b, location + "/" + str(i))
    elif actual != expected:
        raise AssertionError(f"{location}: {actual} != {expected}")


def verify(source: Path, data: Path, reference: Path, output: Path):
    """从原始主函数重建相同初值和调度，比较前向、裁剪前梯度和更新状态。"""
    identity = json.loads((reference / "identity.json").read_text())
    for name, checksum in identity["source"].items():
        if digest(source / name) != checksum:
            raise ValueError("Reference source changed: " + name)
    for name, checksum in identity["data"].items():
        if digest(data / name) != checksum:
            raise ValueError("Reference data changed: " + name)
    torch.set_num_threads(identity["threads"])
    torch.set_num_interop_threads(1)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(source.resolve()))
    tree = adapt(
        (source / "PCNO_Train_4D.py").read_text(),
        data.resolve(),
        output.resolve(),
        identity["branch"],
    )

    class Unobserve(ast.NodeTransformer):
        def visit_For(self, node):
            self.generic_visit(node)
            if isinstance(node.target, ast.Name) and node.target.id == "ep":
                node.iter.args[0] = ast.Constant(1)
            return node

        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and ast.unparse(node.value.func).startswith(
                "_observer."
            ):
                return None
            return node

    tree = ast.fix_missing_locations(Unobserve().visit(tree))
    namespace = {"__name__": "reference_unobserved"}
    exec(compile(tree, str(source / "PCNO_Train_4D.py"), "exec"), namespace)  # noqa: S102 — 已核对冻结源码摘要。
    original = namespace["train"]
    seen = {}
    expected = torch.load(reference / "first-update.pt", weights_only=False)
    gradients = torch.load(reference / "first-gradient.pt", weights_only=False)
    initial = torch.load(reference / "initial.pt", weights_only=False)
    prediction = torch.load(reference / "first-prediction.pt", weights_only=False)

    def intercept(model, all_paths, optimizer, scheduler, **kwargs):
        compare(model.state_dict(), initial, "initial")

        def forward_hook(module, inputs, result):
            bounds = (-3.0, 9.0) if identity["branch"] == "pres" else (-2.0, 4.0)
            actual = torch.nan_to_num(result.detach(), nan=0.0, posinf=1e4, neginf=-1e4).clamp(
                *bounds
            )
            compare(actual, prediction, "prediction")
            seen["prediction"] = True

        model.register_forward_hook(forward_hook)
        clip = torch.nn.utils.clip_grad_norm_

        def checked_clip(parameters, *args, **kwargs):
            compare(
                {k: p.grad for k, p in model.named_parameters()}, gradients, "gradient_before_clip"
            )
            seen["gradients"] = True
            return clip(parameters, *args, **kwargs)

        torch.nn.utils.clip_grad_norm_ = checked_clip
        original_step = scheduler.step

        def step(self, *args, **kwargs):
            original_step(*args, **kwargs)
            for name, value in [
                ("model", model),
                ("optimizer", optimizer),
                ("scheduler", scheduler),
            ]:
                compare(value.state_dict(), expected[name], name)
            seen["state"] = True
            raise Captured()

        scheduler_type = type(scheduler)
        own_step = scheduler_type.__dict__.get("step")
        scheduler_type.step = step
        try:
            original(model, all_paths, optimizer, scheduler, **kwargs)
        finally:
            torch.nn.utils.clip_grad_norm_ = clip
            if own_step is None:
                del scheduler_type.step
            else:
                scheduler_type.step = own_step

    namespace["train"] = intercept
    try:
        namespace["main"]()
    except Captured:
        pass
    if seen != {"prediction": True, "gradients": True, "state": True}:
        raise AssertionError("Did not observe a complete update")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(
            {
                "passed": True,
                "rtol": 1e-5,
                "atol": 1e-6,
                "checks": seen,
                "reference": str(reference),
                "scope": "one full-resolution update; not convergence",
            },
            stream,
            indent=2,
        )


def main():
    """命令行独立数值复放。"""
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "data", "reference", "output"]:
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    verify(args.source, args.data, args.reference, args.output)


if __name__ == "__main__":
    main()
