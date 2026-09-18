"""全仓当前导航和 PRD 结构；不能替代业务或数值验收。"""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]


def test_all_module_prds_have_numbered_six_sections():
    """所有现有模块正文使用同一六节结构，清单与详解编号对应。"""
    paths = list((ROOT / "docs/PRD").glob("*/*/PRD.md"))
    paths += [
        p
        for p in (ROOT / "packages/ai4e-viz/docs/PRD").glob("*.md")
        if p.stem not in {"README", "CHANGELOG"}
    ]
    for path in paths:
        text = path.read_text()
        assert "## 目录" in text, path
        chapters = [
            c
            for c in re.split(r"^## ", text, flags=re.MULTILINE)
            if re.search(r"^### \d+\.1 ", c, re.MULTILINE)
        ]
        assert chapters, path
        for number, chapter in enumerate(chapters, 1):
            assert re.findall(r"^### (\d+\.[1-6]) ", chapter, re.MULTILINE) == [
                f"{number}.{i}" for i in range(1, 7)
            ], path
            listing = chapter.split(f"### {number}.5 ", 1)[1].split(f"### {number}.6 ", 1)[0]
            assert re.findall(r"^(\d+)\. ", listing, re.MULTILINE) == re.findall(
                r"^#### (\d+)\. ", chapter, re.MULTILINE
            ), path


def test_current_repository_entry_links_and_package_navigation():
    """新当前导航无失效链接；所有正式包能定位到模块和长期产品说明。"""
    entry = ROOT / ".context/index.md"
    text = entry.read_text()
    for value in re.findall(r"\]\(([^)]+)\)", text):
        if value.startswith(("http", "#")):
            continue
        # 含括号的架构文件名单独核对，其余入口均为普通相对路径。
        if "ARCHITECTURE" in value:
            continue
        assert (entry.parent / unquote(value.split("#", 1)[0])).exists(), value
    for package in (ROOT / "packages").glob("ai4e-*"):
        if not package.is_dir():
            continue
        context = ROOT / ".context/modules" / f"{package.name}.md"
        assert context.is_file() and package.name in text
    assert (ROOT / "docs/AI4E_Dojo_ARCHITECTURE (1).md").is_file()


def test_unimplemented_products_remain_explicit():
    """整理现状不以其它模块能力或目录存在替代缺失产品功能。"""
    for name in ("automation", "MCP", "visConvertor", "reportManage"):
        text = (ROOT / f"packages/ai4e-viz/docs/PRD/{name}.md").read_text()
        assert "未实现" in text or "未开放" in text
    architecture = (ROOT / "docs/AI4E_Dojo_ARCHITECTURE (1).md").read_text()
    assert "不是全仓准入协议" in architecture
    assert "未作为现行 API 实现" in architecture


def test_inventory_includes_runtime_declarations_and_ui_sources():
    """源码盘点必须覆盖实际入口配置和界面样式，不限于 Python。"""
    from tools.verification.architecture_inventory import inventory

    files = {item["path"]: item for item in inventory()["files"]}
    for path in (
        "AGENTS.md",
        ".context/index.md",
        "pyproject.toml",
        "recipes/wdno/config.yaml",
        "recipes/wdno/pipeline.py",
        "packages/ai4e-web/package.json",
        "packages/ai4e-web/src/modules/inference/inference.css",
    ):
        assert path in files
        assert len(files[path]["sha256"]) == 64
