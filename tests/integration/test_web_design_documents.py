"""检查 Web 设计交付的导航与 PRD 结构，不将文档检查视为平台功能验收。"""

import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / "docs/PRD/ai4e-web/src/PRD.md"
ARCHITECTURE = ROOT / "docs/AI4E_Dojo_ARCHITECTURE (1).md"
LINK = re.compile(r"\[[^\]\n]+\]\((?:<([^>]+)>|([^\s)]+))\)")


def _anchors(text: str) -> set[str]:
    """提取本次文档使用的普通标题锚点，保留中文与重复空格形成的连字符。"""
    headings = re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.MULTILINE)
    return {re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-") for heading in headings}


@pytest.mark.parametrize(
    "path",
    [PRODUCT, ROOT / "docs/architecture/README.md"],
)
def test_design_links_resolve(path: Path):
    """产品和架构入口的本地文件及章节链接必须可定位。"""
    for match in LINK.finditer(path.read_text()):
        target = match.group(1) or match.group(2)
        url = urlsplit(target)
        if url.scheme:
            continue
        destination = (path.parent / unquote(url.path)).resolve() if url.path else path
        assert destination.is_file(), (path, target)
        if url.fragment:
            assert unquote(url.fragment) in _anchors(destination.read_text()), (path, target)


def test_product_chapters_follow_prd_contract():
    """各章均遵守六节约定，功能清单与详解编号一一对应。"""
    text = PRODUCT.read_text()
    for number, chapter in enumerate(re.split(r"^## [一二三]、.*$", text, flags=re.MULTILINE)[1:], 1):
        sections = re.findall(r"^### (\d\.\d) ", chapter, flags=re.MULTILINE)
        assert sections == [f"{number}.{index}" for index in range(1, 7)]
        inventory = chapter.split(f"### {number}.5 ", 1)[1].split(f"### {number}.6 ", 1)[0]
        entries = re.findall(r"^(\d+)\. ", inventory, flags=re.MULTILINE)
        details = re.findall(r"^#### (\d+)\. ", chapter, flags=re.MULTILINE)
        assert entries and entries == details
    assert len(re.findall(r"^## [一二三]、", text, flags=re.MULTILINE)) == 3


def test_v2_is_in_single_authoritative_document():
    """架构 v2 在既有权威文档中，产品稿继续单独维护功能正文。"""
    text = ARCHITECTURE.read_text()
    assert text.count("## 19. Web / Server 当前架构\n") == 1
    assert "PRD/ai4e-web/src/PRD.md" in text
    assert "平台配置编辑在 Server 阶段模块合成" in text
    assert "状态：圈定真实链路" in PRODUCT.read_text()
    assert "不承诺所有状态逐像素一致或生产训练精度" in PRODUCT.read_text()


@pytest.mark.parametrize(
    "filename",
    [
        "dojo-web-wireframe.html",
        "dojo-web-integrated.html",
        "dojo-rawprep-detail.html",
        "dojo-trainprep-detail.html",
        "dojo-model-detail.html",
        "dojo-training-detail.html",
        "dojo-run-detail.html",
        "dojo-post-detail.html",
    ],
)
def test_wireframe_is_offline_and_scripts_parse(filename):
    """线框不加载外部资源；脚本和初始事件属性具备有效语法。"""

    class Markup(HTMLParser):
        """收集资源和事件，不通过字符串猜测 HTML 属性边界。"""

        def __init__(self):
            super().__init__()
            self.handlers = []

        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key in {"src", "href"}:
                    assert not (value or "").startswith(("http:", "https:", "//"))
                if key.startswith("on"):
                    self.handlers.append(value)

    html = (ROOT / "docs/prototypes" / filename).read_text()
    parser = Markup()
    parser.feed(html)
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    assert scripts and parser.handlers
    node = shutil.which("node")
    assert node, "线框脚本语法检查需要 Node.js"
    subprocess.run(
        [
            node,
            "-e",
            "JSON.parse(require('fs').readFileSync(0,'utf8')).forEach(s=>new Function(s))",
        ],
        input=json.dumps(scripts + parser.handlers),
        text=True,
        check=True,
        capture_output=True,
    )
