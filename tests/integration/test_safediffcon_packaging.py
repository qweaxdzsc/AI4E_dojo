"""上游数值定义、依赖边界及可复制模板声明验收。"""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_vendored_source_hashes_and_numerical_definitions():
    """不以同一实现自比较代替原始数值定义核对。"""
    ability = ROOT / "packages/ai4e-contrib/ability"
    record = json.loads((ability / "model/safediffcon/source.json").read_text())
    snapshot = Path(
        "/Users/zonghui/work/project_simulation/dojo_train/safediffcon/admission/20260916/source"
    )
    for name, entry in record["files"].items():
        path = ability / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        if snapshot.exists():
            source = snapshot / entry["source"]
            assert hashlib.sha256(source.read_bytes()).hexdigest() == entry["original_sha256"]

            def definitions(p):
                return {
                    n.name: ast.dump(n, include_attributes=False)
                    for n in ast.parse(p.read_text()).body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                }

            origin, migrated = definitions(source), definitions(path)
            for key, value in migrated.items():
                assert origin[key] == value, (name, key)


def test_runtime_has_no_external_source_dependency():
    for root in [
        ROOT / "packages/ai4e-core/applications/pde_control",
        ROOT / "packages/ai4e-contrib",
    ]:
        for path in root.rglob("*.py"):
            if "safediffcon" not in str(path).lower() and "pde_control" not in str(path):
                continue
            text = path.read_text()
            assert "sys.path.insert" not in text
            assert "new_code_project/SafeDiffCon" not in text
            if "ai4e-core" in str(path):
                assert "ai4e_contrib" not in text


def test_recipe_phase_order_and_post_boundary():
    root = ROOT / "recipes/safediffcon"
    tree = ast.parse((root / "pipeline.py").read_text())
    phases = [
        n.value.args[0].value
        for n in ast.walk(tree)
        if isinstance(n, ast.Assign)
        and isinstance(n.value, ast.Call)
        and isinstance(n.value.func, ast.Attribute)
        and n.value.func.attr == "stage"
    ]
    assert phases == ["rawprep", "trainprep", "train", "posttrain", "infer"]
    post = (root / "post.py").read_text()
    assert "analyze(" in post and "generate(" not in post and "solve(" not in post
