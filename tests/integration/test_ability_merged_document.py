"""合并能力讨论稿的逐项追溯、引用与导航检查，不验证算法执行。"""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = ROOT / "docs/abilities-merged.md"
INVENTORY = ROOT / "docs/abilities-inventory.md"


def _rows(text: str, prefix: str) -> dict[str, list[str]]:
    """读取按编号声明的表格行，拒绝重复编号。"""
    result = {}
    for line in text.splitlines():
        if not re.match(rf"\| {prefix}\d+ \|", line):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        assert cells[0] not in result, f"重复编号：{cells[0]}"
        result[cells[0]] = cells
    return result


def test_ability_merged_complete_mapping():
    """每个原始条目都保留名称和源码，并指向实际声明的主能力或策略。"""
    text = DOCUMENT.read_text(encoding="utf-8")
    original = _rows(INVENTORY.read_text(encoding="utf-8"), "A")
    mapping = _rows(text, "A")
    owners = _rows(text, "O") | _rows(text, "P")
    assert original and owners
    assert mapping.keys() == original.keys(), "存在遗漏或凭空添加的原始条目"
    referenced = set()
    for key, cells in mapping.items():
        assert len(cells) == 5
        assert cells[1] == original[key][1], f"原条目身份不一致：{key}"
        assert cells[-1] == original[key][-1], f"原条目源码不一致：{key}"
        targets = cells[2].split("、")
        assert targets and all(target in owners for target in targets), key
        assert cells[3], f"缺少归并说明：{key}"
        referenced.update(targets)
    assert referenced == owners.keys(), "存在没有实现依据的合并能力"


def test_ability_merged_links_and_navigation():
    """讨论稿与原表均可从模块索引找到，文档及索引链接指向实际文件。"""
    text = DOCUMENT.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith("#"):
            assert f'id="{target[1:]}"' in text, f"失效的阶段锚点：{target}"
            continue
        path = (DOCUMENT.parent / unquote(target.split("#", 1)[0])).resolve()
        assert path.is_relative_to(ROOT), target
        assert path.is_file(), target
    for relative in (
        ".context/index.md",
        ".context/modules/ai4e-core.md",
        ".context/modules/ai4e-contrib.md",
    ):
        index = ROOT / relative
        content = index.read_text(encoding="utf-8")
        for document in (DOCUMENT, INVENTORY):
            targets = [
                target
                for target in re.findall(r"\]\(([^)]+)\)", content)
                if target.endswith(document.name)
            ]
            assert targets, f"缺少导航：{relative} -> {document.name}"
            assert all((index.parent / target).resolve() == document for target in targets)
    assert "不是代码合并、公开 API 变更或拖拽节点已实现的声明" in text
    assert "没有重新执行算法、训练或数值对照" in text


def test_ability_merged_five_stage_visibility():
    """五阶段均在主表展开，模型/训练/后处理不再只有一个父流程条目。"""
    text = DOCUMENT.read_text(encoding="utf-8")
    original = _rows(INVENTORY.read_text(encoding="utf-8"), "A")
    owners = _rows(text, "O") | _rows(text, "P")
    stages = {
        "rawprep": ("R", {"提取具名字段", "表面法向计算"}),
        "trainprep": ("D", {"绑定模型输入与监督字段", "模型专用拼批"}),
        "model": ("M", {"加载初始权重", "冻结指定参数", "域注意力交互", "连续坐标嵌入"}),
        "train": ("T", {"监督目标与损失聚合", "单次有效训练更新", "训练状态捕获与兼容恢复"}),
        "post": ("H", {"重建推理模型", "预测逆变换", "物理指标评价", "结果文件导出"}),
    }
    for stage, (prefix, required) in stages.items():
        match = re.search(
            rf"### 2\.\d {stage}：.*?\n(.*?)(?=\n### |\n## |\Z)", text, re.DOTALL
        )
        assert match, f"缺少主表阶段：{stage}"
        rows = _rows(match[1], prefix)
        assert required <= {cells[1] for cells in rows.values()}, stage
        for key, cells in rows.items():
            assert len(cells) == 8, key
            assert all(owner in owners for owner in cells[6].split("、")), key
            sources = cells[7].split("、")
            assert sources and all(source in original for source in sources), key
    assert "不相加计数" in text


def test_ability_summary_stage_order_and_references():
    """简表按用户指定五类排列，能追溯详细清单且可从模块入口发现。"""
    document = ROOT / "docs/abilities-summary.md"
    text = document.read_text(encoding="utf-8")
    categories = []
    for line in text.splitlines():
        if not re.match(r"\| (rawprep|trainprep|train|model|post) ", line):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        assert len(cells) == 3 and all(cells)
        stage = cells[0].split()[0]
        if not categories or categories[-1] != stage:
            categories.append(stage)
    assert categories == ["rawprep", "trainprep", "train", "model", "post"]
    targets = re.findall(r"\]\(([^)]+)\)", text)
    assert {"abilities-merged.md", "abilities-inventory.md"} <= set(targets)
    assert all((document.parent / target).is_file() for target in targets)
    for relative in (
        ".context/index.md",
        ".context/modules/ai4e-core.md",
        ".context/modules/ai4e-contrib.md",
    ):
        index = ROOT / relative
        targets = re.findall(r"\]\(([^)]+)\)", index.read_text(encoding="utf-8"))
        assert any((index.parent / target).resolve() == document for target in targets)
