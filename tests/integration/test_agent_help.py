"""Agent Help Center 的覆盖、源码漂移、案例和路径门禁。"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELP = ROOT / "docs/agent-help"


def _public_symbols(root: Path, package_root: Path, import_root: str) -> set[str]:
    symbols: set[str] = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(package_root).with_suffix("")
        parts = list(relative.parts)
        if parts[-1] == "__init__":
            parts.pop()
        module = ".".join([import_root, *parts])
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if node.name.startswith("_"):
                continue
            symbol = f"{module}.{node.name}"
            symbols.add(symbol)
            if isinstance(node, ast.ClassDef):
                symbols.update(
                    f"{symbol}.{method.name}"
                    for method in node.body
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not method.name.startswith("_")
                )
    return symbols


def _records() -> list[dict]:
    return [
        json.loads(line)
        for line in (HELP / "indexes/symbols.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]


def _all_names(path: Path) -> set[str]:
    """静态读取模块的全部 ``__all__`` 字面量，不导入包。"""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in tree.body:
        value = None
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
            )
            or (
                isinstance(node, ast.AugAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "__all__"
            )
        ):
            value = node.value
        if isinstance(value, (ast.List, ast.Tuple)):
            names.update(
                item.value
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    return names


def test_generated_help_is_current():
    subprocess.run(
        ["uv", "run", "--no-sync", "python", "tools/docs/build_agent_help.py", "--check"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_ability_application_and_recipe_symbols_are_covered():
    expected: set[str] = set()
    expected |= _public_symbols(
        ROOT / "packages/ai4e-core/abilities", ROOT / "packages/ai4e-core", "ai4e_core"
    )
    expected |= _public_symbols(
        ROOT / "packages/ai4e-core/applications", ROOT / "packages/ai4e-core", "ai4e_core"
    )
    expected |= _public_symbols(
        ROOT / "packages/ai4e-contrib/ability",
        ROOT / "packages/ai4e-contrib",
        "ai4e_contrib",
    )
    expected |= _public_symbols(
        ROOT / "packages/ai4e-contrib/application",
        ROOT / "packages/ai4e-contrib",
        "ai4e_contrib",
    )
    expected |= _public_symbols(ROOT / "recipes", ROOT / "recipes", "recipes")
    actual = {record["symbol"] for record in _records()}
    assert expected <= actual, sorted(expected - actual)[:20]


def test_core_run_and_task_public_exports_are_covered():
    actual = {record["symbol"] for record in _records()}
    expected = {
        *(
            f"ai4e_core.run.{name}"
            for name in _all_names(ROOT / "packages/ai4e-core/run/__init__.py")
        ),
        *(f"ai4e_task.{name}" for name in _all_names(ROOT / "packages/ai4e-task/__init__.py")),
    }
    assert expected <= actual, sorted(expected - actual)


def test_topic_schema_paths_and_coverage_counts_are_consistent():
    manifest = json.loads((HELP / "manifest.json").read_text(encoding="utf-8"))
    topics = json.loads((HELP / "indexes/topics.json").read_text(encoding="utf-8"))
    cases = json.loads((HELP / "indexes/cases.json").read_text(encoding="utf-8"))
    records = _records()
    required = {
        "topic_id",
        "kind",
        "layer",
        "domain",
        "title",
        "summary",
        "path",
        "anchor",
        "symbols",
        "tasks",
        "inputs",
        "outputs",
        "artifacts",
        "errors",
        "case_ids",
        "recipe_ids",
        "stability",
    }
    assert len({topic["topic_id"] for topic in topics}) == len(topics)
    for topic in topics:
        assert required <= set(topic), topic["topic_id"]
        page = (HELP / topic["path"]).resolve()
        assert page.is_relative_to(HELP.resolve()) and page.is_file(), topic["topic_id"]
        if topic["anchor"]:
            assert f'id="{topic["anchor"]}"' in page.read_text(encoding="utf-8")
    assert manifest["coverage"] == {
        "symbols": len(records),
        "topics": len(topics),
        "cases": len(cases),
    }


def test_every_symbol_has_page_anchor_and_required_sections():
    required = (
        "### 用途",
        "### 导入与签名",
        "### 参数",
        "### 返回值",
        "### 异常",
        "### 副作用与产物",
        "### 配置键",
        "### 最小可执行检查",
        "### Recipe 与案例",
        "### 源码位置",
        "### 相关 API",
        "### 不适用场景与证据边界",
    )
    cache: dict[str, str] = {}
    for record in _records():
        content = cache.setdefault(
            record["page"], (HELP / record["page"]).read_text(encoding="utf-8")
        )
        assert f'id="{record["anchor"]}"' in content, record["symbol"]
        assert all(section in content for section in required), record["page"]
        source = ROOT / record["source_path"]
        assert source.is_file(), record["source_path"]
        assert 1 <= record["source_line"] <= len(source.read_text(encoding="utf-8").splitlines())


def test_all_manifest_cases_have_help_pages():
    cases = json.loads((ROOT / "examples/case-manifest.json").read_text(encoding="utf-8"))["cases"]
    topics = json.loads((HELP / "indexes/topics.json").read_text(encoding="utf-8"))
    topic_ids = {topic["topic_id"] for topic in topics}
    assert {f"case:{case['id']}" for case in cases} <= topic_ids
    for case in cases:
        assert (HELP / "examples/cases" / (case["id"].replace(".", "/") + ".md")).is_file()


def test_installable_help_has_no_repository_only_dependency():
    checked = [ROOT / "DOJO_AGENT_GUIDE.md", ROOT / ".agents/skills/dojo-research/SKILL.md"]
    checked.extend(HELP.rglob("*.md"))
    forbidden = (".context/", "/Users/", "/private/tmp/")
    for path in checked:
        content = path.read_text(encoding="utf-8")
        assert not any(marker in content for marker in forbidden), path
