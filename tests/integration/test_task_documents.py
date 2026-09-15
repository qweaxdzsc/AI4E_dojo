"""Task 文档入口、六节 PRD 与声明文件完整性。"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_task_documents_and_entry_links():
    """六类功能说明齐全；源码与文档链接真实存在。"""
    for module in ("cli", "projects", "tasks", "versions", "templates", "storage"):
        assert (ROOT / "packages/ai4e-task" / module).is_dir()
        text = (ROOT / f"docs/PRD/ai4e-task/{module}/PRD.md").read_text()
        chapters = [
            chapter
            for chapter in re.split(r"^## ", text, flags=re.MULTILINE)
            if re.search(r"^### \d+\.1 ", chapter, re.MULTILINE)
        ]
        for number, chapter in enumerate(chapters, 1):
            assert re.findall(r"^### (\d+\.[1-6]) ", chapter, re.MULTILINE) == [
                f"{number}.{i}" for i in range(1, 7)
            ]
            inventory = chapter.split(f"### {number}.5 ", 1)[1].split(f"### {number}.6 ", 1)[0]
            assert re.findall(r"^(\d+)\. ", inventory, re.MULTILINE) == re.findall(
                r"^#### (\d+)\. ", chapter, re.MULTILINE
            )
    entry = json.loads((ROOT / "recipes/aero_cfd/task-entry.json").read_text())
    assert (ROOT / "recipes/aero_cfd" / entry["script"]).is_file()
    assert (ROOT / "recipes/aero_cfd" / entry["config"]).is_file()
    assert (ROOT / "docs/adr/0003-task-local-package.md").is_file()
    assert (ROOT / "examples/task_lifecycle.py").is_file()
