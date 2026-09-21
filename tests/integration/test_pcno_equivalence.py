"""PCNO 源码拆分后的真实网络、损失、物理与经济等价性。"""

import ast
import importlib.util
import json
import os
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(
    os.environ.get(
        "DOJO_PCNO_SOURCE", "/Users/zonghui/work/new_code_project/PCNO/capsule-8000337-code"
    )
)


@pytest.fixture
def original():
    if not SOURCE.is_dir():
        pytest.skip("Explicit original PCNO source required")
    spec = importlib.util.spec_from_file_location("pcno_original", SOURCE / "PCNO_Model_4D.py")
    module = importlib.util.module_from_spec(spec)
    source = SOURCE / "PCNO_Model_4D.py"
    exec(compile(source.read_text(), str(source), "exec"), module.__dict__)  # noqa: S102 -- 只读原源码，不写pycache
    return module


def test_extracted_computations_retain_source_expressions():
    metadata = json.loads(
        (ROOT / "packages/ai4e-contrib/ability/model/pcno/source.json").read_text()
    )

    class StripDocs(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if ast.get_docstring(node):
                node.body.pop(0)
            return node

        visit_ClassDef = visit_FunctionDef

    for item in metadata["modules"]:
        source = ast.parse((SOURCE / item["source"]).read_text())
        actual = ast.parse((ROOT / item["file"]).read_text())
        before = {n.name: n for n in source.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
        after = {n.name: n for n in actual.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
        for name in item["definitions"]:
            a, b = before[name], after[name]
            if name == "TrainConfig":
                a.body = [
                    n
                    for n in a.body
                    if not isinstance(n, ast.FunctionDef) or n.name != "async_prefetch"
                ]
            if name == "technical_results":
                a.args.args.append(ast.arg(arg="stats"))
            if name == "PDE_F":
                from tools.verification.pcno.numerical_repair import repair_vis

                a = repair_vis(a)
            assert ast.dump(StripDocs().visit(a)) == ast.dump(StripDocs().visit(b)), (
                item["file"],
                name,
            )


def test_viscosity_preserves_forward_and_active_derivative(original):
    from ai4e_core.abilities.constraint.geothermal import PDE_F

    x = torch.tensor([-70.0, -45.0, 0.0, 39.0, 40.0, 99.0, 100.0, 200.0], requires_grad=True)
    before = original.PDE_F.vis(x)
    after = PDE_F.vis(x)
    torch.testing.assert_close(after, before, rtol=0, atol=0)
    old_gradient = torch.autograd.grad(before.sum(), x, retain_graph=True)[0]
    new_gradient = torch.autograd.grad(after.sum(), x)[0]
    assert not torch.isfinite(old_gradient[:2]).any()
    assert torch.isfinite(new_gradient).all()
    torch.testing.assert_close(new_gradient[2:], old_gradient[2:], rtol=0, atol=0)
    expected = 1.787 * torch.exp(x[:2] * (-0.033 + 0.0001962 * x[:2])) * 0.001
    torch.testing.assert_close(new_gradient[:2], torch.autograd.grad(expected.sum(), x)[0][:2])


@pytest.mark.parametrize("branch", ["pres", "temp"])
def test_real_network_forward_and_backward(original, branch):
    from ai4e_contrib.ability.model.pcno import build_model

    torch.set_num_threads(2)
    torch.manual_seed(7)
    reference = original.EnhancedP_T_Net(1, 1, 1, 1, 8, 8, train_mode=branch)
    actual = build_model(branch=branch)
    actual.load_state_dict(reference.state_dict())
    x = torch.randn(1, 4, 4, 5, 3, 14)
    g = torch.randn(1, 4)
    expected = reference(x, g)
    obtained = actual(x, g)
    torch.testing.assert_close(obtained, expected, rtol=1e-5, atol=1e-6)
    expected.square().mean().backward()
    obtained.square().mean().backward()
    for left, right in zip(reference.parameters(), actual.parameters()):
        torch.testing.assert_close(left.grad, right.grad, rtol=1e-5, atol=1e-6)


def test_loss_values_and_gradients(original):
    from ai4e_core.abilities.constraint import spatiotemporal_field as actual

    x = torch.randn(1, 4, 4, 5, 3, requires_grad=True)
    truth = torch.randn_like(x)
    d = torch.rand_like(x)
    for task in ["pressure", "temperature"]:
        a = original.create_smooth_weight_map(x, truth, d, d, task=task)
        b = actual.create_smooth_weight_map(x, truth, d, d, task=task)
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    for name, args in [
        ("compute_enhanced_gradient_loss", (x, truth)),
        ("weighted_mse", (x, truth, d)),
    ]:
        a = getattr(original, name)(*args)
        b = getattr(actual, name)(*args)
        torch.testing.assert_close(a, b, rtol=0, atol=0)
        torch.testing.assert_close(
            torch.autograd.grad(a, x, retain_graph=True)[0],
            torch.autograd.grad(b, x, retain_graph=True)[0],
            rtol=0,
            atol=0,
        )
