"""能力盘点文档的源码覆盖、入口定位与导航检查，不替代算法验收。"""

import ast
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / "docs/abilities-inventory.md"


def test_ability_inventory_source_coverage():
    """每个实现文件均有独立行，直接定义的公开函数与类型可从该行发现。"""
    text = DOCUMENT.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if re.match(r"\| A\d{3} \|", line)]
    expected = set()
    for directory in ("packages/ai4e-core/abilities", "packages/ai4e-contrib/ability"):
        for path in sorted((ROOT / directory).rglob("*.py")):
            if path.name == "__init__.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            public = [
                node
                for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and not node.name.startswith("_")
            ]
            if not public:
                continue
            target = f"../{path.relative_to(ROOT).as_posix()}"
            matches = [row for row in rows if f"]({target})" in row]
            assert len(matches) == 1, f"实现文件缺失或重复：{target}"
            expected.add(target)
            for node in public:
                assert f"`{node.name}`" in matches[0], f"遗漏入口：{target}:{node.name}"
                if isinstance(node, ast.ClassDef):
                    for method in node.body:
                        if isinstance(
                            method, (ast.FunctionDef, ast.AsyncFunctionDef)
                        ) and not method.name.startswith("_"):
                            assert f"`{method.name}`" in matches[0]
    assert len(rows) == len(expected), "清单包含未与当前实现对应的条目"


def test_ability_inventory_links_and_navigation():
    """能力表引用均落在仓内文件，并可从全仓及两个模块索引发现。"""
    text = DOCUMENT.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        path = (DOCUMENT.parent / unquote(target.split("#", 1)[0])).resolve()
        assert path.is_relative_to(ROOT), target
        assert path.is_file(), target
    for relative in (
        ".context/index.md",
        ".context/modules/ai4e-core.md",
        ".context/modules/ai4e-contrib.md",
    ):
        assert DOCUMENT.name in (ROOT / relative).read_text(encoding="utf-8")
    assert "未重新运行算法或训练验收" in text
    assert "core abilities/report" in text
