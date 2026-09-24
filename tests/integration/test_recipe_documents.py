"""Recipe 规范与现行索引；历史计划核对迁移前正文，行为另由实跑验收。"""

import ast
import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_scientific_chains_are_explicit_in_documentation():
    text = (ROOT / "docs/PRD/recipes/aero_cfd/PRD.md").read_text()
    assert "缺少该配置时保持原锚点" not in text
    assert "三个 Transolver" in text and "只负责图缓存" in text


def test_authoring_rule_and_development_entry():
    path = ROOT / ".cursor/rules/ai4e-recipe-authoring.mdc"
    header = yaml.safe_load(path.read_text().split("---")[1])
    assert header["alwaysApply"] is False
    assert "examples/recipe_extensions/**/*" in header["globs"]
    agents = (ROOT / "AGENTS.md").read_text()
    assert "ai4e-recipe-authoring.mdc" in agents
    assert "不以脚本行数少作为目标" in agents
    assert "仓库外复制" in agents
    rule = (ROOT / ".cursor/rules/plan-business-alignment.mdc").read_text()
    assert "典型文件写法" in rule and "已有接口和拟新增接口" in rule


def test_historical_plan_matches_registered_pre_infer_bodies():
    plan = (ROOT / ".cursor/plans/显式_recipe_步骤_9ea01c80.plan.md").read_text()
    baseline = json.loads((ROOT / "recipes/aero_cfd/legacy-profile.json").read_text())["profiles"][
        "recipes/aero_cfd"
    ]
    signatures = {
        hashlib.sha256(ast.dump(ast.parse(body), include_attributes=False).encode()).hexdigest()
        for body in re.findall(r"```python\n(.*?)```", plan, re.DOTALL)
    }
    for name, signature in baseline.items():
        if name.endswith(".py"):
            assert signature in signatures, name
    files = list((ROOT / "recipes/aero_cfd").glob("*.py")) + [ROOT / "recipes/aero_cfd/config.yaml"]
    files += [
        ROOT / "examples/recipe_extensions" / kind / name
        for kind in ("field_mapping", "sampling")
        for name in ("custom_abilities.py", "config.yaml")
    ]
    for path in files:
        if path.suffix == ".py":
            ast.parse(path.read_text())
            if path.name not in {"configuration.py", "custom_abilities.py"}:
                assert ".workflow" not in path.read_text()


def test_indexes_and_current_responsibilities():
    for file in (
        ".context/index.md",
        ".context/modules/recipes.md",
        ".context/modules/ai4e-core.md",
        ".context/modules/ai4e-contrib.md",
    ):
        assert "recipe-explicit-acceptance.md" in (ROOT / file).read_text()
    architecture = (ROOT / "docs/AI4E_Dojo_ARCHITECTURE (1).md").read_text()
    assert "不以行数限制装配正文" in architecture
    assert "recipe 保持极薄" not in architecture
    assert "map_fields" in (ROOT / "recipes/aero_cfd/README.md").read_text()
    for directory in ("field_mapping", "sampling"):
        root = ROOT / "examples/recipe_extensions" / directory
        assert (root / "custom_abilities.py").is_file()
        assert (root / "README.md").is_file()
        assert not (root / "__init__.py").exists()
