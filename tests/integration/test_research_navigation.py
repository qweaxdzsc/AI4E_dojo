"""研究任务的导航、源码签名和配置入口盘点。"""

import ast
import re
from pathlib import Path
from urllib.parse import unquote

from tools.verification.architecture_inventory import declarations
from tools.verification.training_execution import entries

ROOT = Path(__file__).resolve().parents[2]


def test_research_task_routes_and_links():
    path = ROOT / ".context/tasks/research.md"
    text = path.read_text()
    for title in ("训练已有模型", "组装 recipe", "接入新模型", "研究原模型变体"):
        assert f"## {title}" in text
    for file in (
        path,
        ROOT / ".agents/skills/dojo-research/SKILL.md",
        ROOT / ".agents/skills/dojo-integrate-model/SKILL.md",
        ROOT / "docs/model-integration-goals.md",
        ROOT / "examples/recipe_extensions/README.md",
        ROOT / "recipes/README.md",
    ):
        for value in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            if not value.startswith(("http", "#")):
                assert (file.parent / unquote(value.split("#", 1)[0])).exists(), (file, value)


def test_inventory_signatures_are_locatable():
    path = ROOT / "packages/ai4e-core/abilities/training/iterations.py"
    details = declarations(ast.parse(path.read_text()))
    function = next(item for item in details if item["name"] == "fit_iterations")
    assert "update_step=None" in function["signature"]
    assert path.read_text().splitlines()[function["line"] - 1].startswith("def fit_iterations(")
    assert function["end_line"] > function["line"]


def test_every_configuration_is_classified_without_claiming_runtime():
    found = entries()
    expected = {
        str(p.parent.relative_to(ROOT))
        for section in ("recipes", "examples")
        for p in (ROOT / section).rglob("config.yaml")
    }
    assert {item["path"] for item in found} == expected
    assert all(item["handoff"] == "pending runtime verification" for item in found)
    assert (
        next(item for item in found if item["path"] == "examples/recipe_extensions/wdno")["kind"]
        == "overlay"
    )


def test_history_remains_accessible_and_current_rules_are_small():
    current = (ROOT / "AGENTS.md").read_text()
    assert "共享训练执行" in current
    assert ".context/history/development-updates-20260917.md" in current
    history = (ROOT / ".context/history/development-updates-20260917.md").read_text()
    assert "训练运行实时曲线与评估" in history
    assert "推理页目录预加载与过期批次误报" not in current
    assert "未获当次明确同意" in current
