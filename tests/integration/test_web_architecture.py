"""源码依赖边界：服务不直接导入算法，Web 不越过微领域门面。"""

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_python_dependency_boundaries():
    for package, forbidden in [
        ("ai4e-server", {"ai4e_core", "ai4e_contrib", "ai4e_viz", "recipes"}),
        ("ai4e-viz", {"ai4e_core", "ai4e_contrib", "ai4e_task", "recipes"}),
    ]:
        for file in (ROOT / "packages" / package).rglob("*.py"):
            for node in ast.walk(ast.parse(file.read_text())):
                imports = (
                    [n.name for n in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else []
                )
                assert not {v.split(".")[0] for v in imports} & forbidden, file


def test_microdomain_boundaries():
    subprocess.run(
        ["node", str(ROOT / "packages/ai4e-web/scripts/check-boundaries.mjs")], check=True
    )
