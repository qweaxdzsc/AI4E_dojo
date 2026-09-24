"""standalone/extension 清单和路径契约。"""

import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_case_manifest_has_only_two_case_types_and_complete_standalones():
    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text())
    assert manifest["example_contract_version"] == 1
    assert manifest["recipe_contract_version"] == 1
    assert {case["type"] for case in manifest["cases"]} == {"standalone", "extension"}
    assert not any("available" in case for case in manifest["cases"])
    for case in manifest["cases"]:
        path = ROOT / "examples" / case["path"]
        if case["type"] == "standalone":
            for name in case["required_files"]:
                assert (path / name).is_file(), (case["id"], name)
        else:
            assert case["base_case"] in {item["id"] for item in manifest["cases"]}
            assert all((path / name).is_file() for name in case["override_files"])


def test_examples_do_not_contain_development_paths_or_internal_navigation():
    forbidden = ("/Users/", "/private/tmp/", ".context", "recipes/")
    for path in (ROOT / "examples").rglob("*"):
        if path.is_file() and path.suffix not in {".pyc"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert not any(value in text for value in forbidden), path


def test_declared_recipe_stage_files_are_byte_identical():
    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text())
    for case in manifest["cases"]:
        if case["type"] != "standalone":
            continue
        recipe = ROOT / "recipes" / case["recipe_source"]
        example = ROOT / "examples" / case["path"]
        for name in case["shared_stage_files"]:
            assert (recipe / name).read_bytes() == (example / name).read_bytes(), (case["id"], name)


@pytest.mark.parametrize("name", ["DOJO_AGENT_GUIDE.md", ".agents/skills/dojo-research/SKILL.md"])
def test_agent_resources_are_public_and_portable(name):
    text = (ROOT / name).read_text()
    assert ".context" not in text and "/Users/" not in text and "recipes/" not in text
    assert "standalone" in text and "extension" in text


def test_agent_resources_define_one_primary_entry_per_agent_capability():
    guide_path = ROOT / "DOJO_AGENT_GUIDE.md"
    skill_path = ROOT / ".agents/skills/dojo-research/SKILL.md"
    guide = guide_path.read_text()
    skill = skill_path.read_text()
    help_index = (ROOT / "docs/agent-help/index.md").read_text()

    guide_first_screen = "\n".join(guide.splitlines()[:45])
    skill_first_screen = "\n".join(skill.splitlines()[:45])
    assert "docs/agent-help/index.md" in guide_first_screen
    assert "../../../docs/agent-help/index.md" in skill_first_screen
    assert ".agents/skills/dojo-research/SKILL.md" in guide
    assert "../../../DOJO_AGENT_GUIDE.md" in skill
    assert "完整新训练任务先选择并复制最接近的 standalone example" in skill_first_screen
    assert "用户组件与公开扩展点" in skill_first_screen
    assert "不要求采用某个固定算法工具" in skill_first_screen
    assert "唯一帮助正文" in help_index

    help_entry = (ROOT / "docs/agent-help/index.md").resolve()
    assert (guide_path.parent / "docs/agent-help/index.md").resolve() == help_entry
    assert (skill_path.parent / "../../../docs/agent-help/index.md").resolve() == help_entry

    help_types = (
        "getting-started",
        "concepts",
        "workflows",
        "api",
        "user-components",
        "examples",
        "recipe",
        "troubleshooting",
        "reference",
    )
    for help_type in help_types:
        assert help_type in guide, help_type
        assert help_type in skill, help_type
    for api_name in ("search_help", "read_help_topic", "describe_help_symbol"):
        assert api_name in guide, api_name
        assert api_name in skill, api_name


def test_agent_resources_contain_executable_python_api_contract():
    guide = (ROOT / "DOJO_AGENT_GUIDE.md").read_text()
    skill = (ROOT / ".agents/skills/dojo-research/SKILL.md").read_text()
    for name in (
        "guide_info",
        "export_help",
        "search_help",
        "read_help_topic",
        "describe_help_symbol",
        "copy_example",
        "ai4e_core.run.launch",
        "ai4e_task",
    ):
        assert name in guide, name
    for name in (
        "search_help",
        "describe_help_symbol",
        "ai4e_core.run.launch",
        "TrainingRun",
        "ai4e_task.create_project",
        "ai4e_task.wait_run",
    ):
        assert name in skill, name

    topics = json.loads((ROOT / "docs/agent-help/indexes/topics.json").read_text())
    topic_ids = {topic["topic_id"] for topic in topics}
    for topic_id in (
        "api:ai4e_core.run.launch",
        "api:ai4e_core.run.TrainingRun",
        "api:ai4e_task.new_task",
        "api:ai4e_task.submit_run",
        "api:ai4e_task.resume_run",
        "user-component:loss",
    ):
        assert topic_id in topic_ids

    snippets = re.findall(r"```python\n(.*?)```", guide, flags=re.DOTALL)
    assert snippets
    for snippet in snippets:
        ast.parse(snippet)
