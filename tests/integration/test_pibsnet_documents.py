"""122项来源保留、导航、公开案例与依赖边界的文档契约。"""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_inventory_122_rows_preserved_and_mapped():
    def rows(path):
        return [line for line in path.read_text().splitlines() if re.match(r"\| \d+ \|", line)]

    original = rows(ROOT / "docs/pibsnet/原始训练流程功能列表.md")
    mapped = rows(ROOT / "docs/pibsnet/实施映射.md")
    assert len(original) == len(mapped) == 122
    assert [int(r.split("|")[1]) for r in mapped] == list(range(1, 123))
    for line in mapped:
        path = line.split("|")[4].strip()
        assert (ROOT / path).exists(), path
    for name in ("原始训练流程功能列表.xlsx", "实施映射.xlsx"):
        assert (ROOT / "docs/pibsnet" / name).stat().st_size > 1000


def test_public_entries_and_source_provenance():
    lock = json.loads(
        (ROOT / "packages/ai4e-contrib/ability/model/pibsnet/source.json").read_text()
    )
    assert len(lock["reference_files"]) == 7
    assert all(re.fullmatch("[0-9a-f]{64}", value) for value in lock["reference_files"].values())
    for case in (
        "convection_diffusion",
        "neumann_diffusion",
        "advection",
        "burgers",
        "diffusion_trapezoid",
    ):
        assert (ROOT / f"examples/parametric_pde/{case}/generate.yaml").exists()
        assert (ROOT / f"examples/parametric_pde/{case}/config.yaml").exists()
        tree = ast.parse(
            (ROOT / f"packages/ai4e-contrib/application/datasets/{case}/generate.py").read_text()
        )
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "generate" for node in tree.body
        )
    for path in (ROOT / "packages/ai4e-core/applications/parametric_pde").glob("*.py"):
        tree = ast.parse(path.read_text())
        assert not any(
            isinstance(node, ast.ImportFrom) and (node.module or "").startswith("ai4e_contrib")
            for node in ast.walk(tree)
        )


def test_trapezoid_migration_and_input_audit_documentation():
    """迁移与只读核查有明确入口，不能混用历史完整映射的说明。"""
    text = (ROOT / "docs/pibsnet/Neumann与Advection输入核查.md").read_text()
    for required in ("C.4", "D.2", "单元0样条", "未重训", "1.3834418206", "0.8745400906"):
        assert required in text
    for index in (".context/index.md", ".context/modules/recipes.md"):
        assert "Neumann与Advection输入核查.md" in (ROOT / index).read_text()
    for path in (
        "docs/PRD/ai4e-contrib/ability/PRD.md",
        "docs/PRD/ai4e-contrib/application/PRD.md",
        "docs/PRD/recipes/parametric_pde/PRD.md",
    ):
        assert "梯形" in (ROOT / path).read_text()
    lines = (ROOT / "docs/pibsnet/实施映射.md").read_text().splitlines()
    migrated = [line for line in lines if re.match(r"\| (9[7-9]|10[0-9]|110) \|", line)]
    assert len(migrated) == 14
    assert not any("50/10文献数据已生成" in row for row in migrated)
    assert any("初始内部零" in row for row in migrated)


def test_selected_source_cases_and_migration_entries():
    lock = json.loads(
        (ROOT / "packages/ai4e-contrib/ability/model/pibsnet/source.json").read_text()
    )
    assert "selected_neumann_advection" in lock
    for name in ["source_cases.py", "neumann_numerics.py", "advection_numerics.py"]:
        assert (ROOT / "packages/ai4e-contrib/ability/model/pibsnet" / name).exists()
    for case in ["neumann_diffusion", "advection"]:
        text = (ROOT / f"examples/parametric_pde/{case}/config.yaml").read_text()
        assert "source_dojo_2026-09-14" in text and "device: cpu" in text
        assert "prepared_paper_v3" not in text
