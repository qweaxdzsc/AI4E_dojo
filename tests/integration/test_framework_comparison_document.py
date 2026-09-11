"""框架比较参考文档的发现入口与仓内证据链接检查。"""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / "docs/ai4s-framework-comparison.md"


def test_framework_comparison_navigation():
    """参考文档可从治理入口及案例模块索引发现。"""
    assert DOCUMENT.is_file()
    for relative in ("AGENTS.md", ".context/index.md", ".context/modules/recipes.md"):
        assert DOCUMENT.name in (ROOT / relative).read_text(encoding="utf-8")


def test_framework_comparison_local_evidence_links():
    """仓内证据必须可定位；相邻参考仓库不作为单独克隆的依赖。"""
    content = DOCUMENT.read_text(encoding="utf-8")
    targets = re.findall(r"\]\((<[^>]+>|[^)]+)\)", content)
    checked = []
    for target in targets:
        relative = unquote(target.strip("<>").split("#", 1)[0])
        if not relative or "://" in relative:
            continue
        path = (DOCUMENT.parent / relative).resolve()
        if not path.is_relative_to(ROOT):
            continue
        assert path.is_file(), f"失效的仓内证据链接：{relative}"
        checked.append(path)
    assert checked, "比较文档应提供仓内依据"
