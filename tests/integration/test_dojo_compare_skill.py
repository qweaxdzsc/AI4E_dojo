"""主控对照技能可独立携带，且不随实验组研究资源导出。"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml
from ai4e_task.templates import resources

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/dojo-compare"


def test_controller_skill_is_portable_with_local_references(tmp_path):
    """复制整个技能后说明及按需引用仍在包内，不依赖本机仓库。"""
    target = tmp_path / "dojo-compare"
    shutil.copytree(SKILL, target)
    entry = target / "SKILL.md"
    metadata = yaml.safe_load(entry.read_text().split("---", 2)[1])
    assert metadata["name"] == target.name
    assert metadata["description"]
    visited = set()
    pending = [entry]
    while pending:
        page = pending.pop()
        if page in visited:
            continue
        visited.add(page)
        text = page.read_text()
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            assert "://" not in link, "必读材料应在技能包内可离线取得"
            child = (page.parent / link.split("#", 1)[0]).resolve()
            assert child.is_relative_to(target)
            assert child.is_file()
            pending.append(child)
    assert set(target.rglob("*.md")) == visited
    ui = yaml.safe_load((target / "agents/openai.yaml").read_text())
    assert "$" + metadata["name"] in ui["interface"]["default_prompt"]


def test_participant_guide_export_does_not_include_controller_skill(tmp_path, monkeypatch):
    """源资源含主控技能时，实际研究材料导出仍只交付研究技能。"""
    monkeypatch.setattr(resources, "resource_root", lambda: ROOT)
    target = tmp_path / "participant"
    result = resources.export_guide(target)
    assert Path(result["guide"]).is_file()
    assert (
        Path(result["skill"]).read_bytes()
        == (ROOT / ".agents/skills/dojo-research/SKILL.md").read_bytes()
    )
    exported = sorted(p.parent.name for p in (target / ".agents/skills").glob("*/SKILL.md"))
    assert exported == ["dojo-research"]
    assert not (target / ".agents/skills/dojo-compare").exists()
    assert not (target / "AGENTS.md").exists()
