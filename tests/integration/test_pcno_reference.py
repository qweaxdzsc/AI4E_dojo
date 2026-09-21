"""参考适配只能改变路径、设备、分支及观察，不能改变科学表达式。"""

import ast
from pathlib import Path

import pytest

from tools.verification.pcno.reference import adapt, digest

TRAINER = """
import torch

def train(model, epochs):
    for ep in range(1, epochs + 1):
        model.train()
        loss = objective(model)
        loss.backward()
        clip(model)
        optimizer.step()
        scheduler.step()
        if ep >= 30 and ep % 5 == 0:
            model.eval()
            evaluate(model)
        path = f"/data/MODEL_{ep}.pth"
        save(path)

def main():
    device = torch.device("cuda" if available() else "cpu")
    stats = read('/data/stats.json')
    chunks = glob('/data/chunk_*.pt')
    model = build(train_mode='pres')
    train(model, epochs=250, train_mode='pres')
"""


def test_only_declared_transformations():
    tree = adapt(TRAINER, Path("/inputs"), Path("/outputs"), "temp")
    code = ast.unparse(tree)
    assert "/data" not in code
    assert "/inputs/stats.json" in code
    assert "/inputs/chunk_*.pt" in code
    assert "/outputs/MODEL_" in code
    assert "torch.device('cpu')" in code
    assert code.count("train_mode='temp'") == 2
    assert (
        code.index("loss.backward()") < code.index("_observer.gradient") < code.index("clip(model)")
    )
    assert code.index("scheduler.step()") < code.index("_observer.step")

    class RemoveObservations(ast.NodeTransformer):
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

    original = next(
        n for n in ast.parse(TRAINER).body if isinstance(n, ast.FunctionDef) and n.name == "train"
    )
    actual = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "train")
    actual = RemoveObservations().visit(actual)
    # The sole non-observation change in train is its checkpoint destination.
    expected = ast.parse(ast.unparse(original).replace("/data/MODEL_", "/outputs/MODEL_")).body[0]
    assert ast.dump(actual) == ast.dump(expected)


def test_digest_tracks_content_without_writing(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"abc")
    stamp = source.stat().st_mtime_ns
    assert digest(source) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert source.read_bytes() == b"abc"
    assert source.stat().st_mtime_ns == stamp


def test_real_source_transformation_if_available():
    source = Path("/Users/zonghui/work/new_code_project/PCNO/capsule-8000337-code/PCNO_Train_4D.py")
    if not source.is_file():
        pytest.skip("Author checkout is required for real-source audit")
    tree = adapt(source.read_text(), Path("/inputs"), Path("/outputs"), "pres")
    compile(tree, str(source), "exec")
    original = ast.parse(source.read_text())
    # ModelConfig contains loss weights, physical input decoding and LR schedule.
    before = next(
        n for n in original.body if isinstance(n, ast.ClassDef) and n.name == "ModelConfig"
    )
    after = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ModelConfig")
    assert ast.dump(before) == ast.dump(after)


def test_epoch_resume_restores_rng_order_and_next_update(tmp_path):
    import random

    import numpy as np
    import torch

    from tools.verification.pcno.reference import Observer

    def construct():
        model = torch.nn.Linear(2, 1)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1, 0.99)
        return {
            "model": model,
            "optimizer": optimizer,
            "scheduler": scheduler,
            "all_paths": [f"/data/chunk_{i:02d}.pt" for i in range(8)],
            "ep": 1,
        }

    def update(scope):
        random.shuffle(scope["all_paths"])
        x = torch.rand(3, 2) + float(np.random.rand())
        scope["optimizer"].zero_grad()
        scope["model"](x).square().sum().backward()
        scope["optimizer"].step()
        scope["scheduler"].step()

    random.seed(7)
    np.random.seed(7)
    torch.manual_seed(7)
    scope = construct()
    for _ in range(21):
        update(scope)
    observer = Observer(tmp_path)
    observer.updates = 21
    observer.save("saved.pt", observer.state(scope))
    update(scope)
    expected = {k: v.clone() for k, v in scope["model"].state_dict().items()}
    expected_order = scope["all_paths"][:]
    expected_rng = torch.get_rng_state().clone()
    random.seed(10)
    np.random.seed(10)
    torch.manual_seed(10)
    resumed = construct()
    restored = Observer(tmp_path, tmp_path / "saved.pt")
    restored.start(resumed)
    assert restored.first_epoch == 2
    assert restored.updates == 21
    update(resumed)
    for key, value in resumed["model"].state_dict().items():
        torch.testing.assert_close(value, expected[key], rtol=0, atol=0)
    assert resumed["all_paths"] == expected_order
    assert torch.equal(torch.get_rng_state(), expected_rng)
    assert resumed["scheduler"].state_dict() == scope["scheduler"].state_dict()


def test_author_checkpoint_is_not_exact_resume(tmp_path):
    import torch

    from tools.verification.pcno.reference import Observer

    path = tmp_path / "author.pt"
    torch.save({"model": {}, "epoch": 50, "optimizer": {}, "scheduler": {}}, path)
    with pytest.raises(ValueError, match="author weights alone cannot resume"):
        Observer(tmp_path, path).start({})
