"""资源门面不加载案例，且复制/物化行为明确。"""

import json
from pathlib import Path

import pytest
from ai4e_task.templates.resources import (
    check_example,
    copy_example,
    describe_help_symbol,
    export_guide,
    export_help,
    guide_info,
    help_info,
    list_examples,
    list_help_topics,
    read_help_topic,
    search_help,
    source_location,
)


def test_resource_manifest_and_checks():
    manifest = json.loads((Path(__file__).resolve().parents[2] / 'examples/case-manifest.json').read_text())
    for kind in ['standalone', 'extension']:
        assert {c['id'] for c in list_examples(case_type=kind)} == {
            c['id'] for c in manifest['cases'] if c['type'] == kind
        }
    assert check_example("parametric_pde.neumann_diffusion")["ok"]


def test_copy_standalone_rejects_non_empty_target(tmp_path):
    target = tmp_path / "case"
    result = copy_example("parametric_pde.neumann_diffusion", target)
    assert (target / "pipeline.py").is_file()
    assert result["type"] == "standalone"
    (target / "sentinel").write_text("x")
    with pytest.raises(FileExistsError, match="为空"):
        copy_example("parametric_pde.neumann_diffusion", target)


def test_copy_extension_materializes_base_and_provenance(tmp_path):
    target = tmp_path / "variant"
    result = copy_example("recipe_extensions.wdno", target)
    assert result["base_case"] == "wdno.burgers_base"
    assert (target / "train.py").is_file()
    assert (target / ".dojo-provenance.json").is_file()


def test_guide_export_and_source_location_do_not_create_agents(tmp_path):
    info = guide_info()
    assert Path(info["guide"]).is_file()
    assert Path(info["skill"]).is_file()
    assert Path(info["manifest"]).is_file()
    assert Path(info["help_root"]).is_dir()
    assert Path(info["help_manifest"]).is_file()
    assert Path(info["help_entry"]).is_file()
    assert info["python"] and info["dojo_version"] and info["source"]
    result = export_guide(tmp_path / "guide")
    assert Path(result["guide"]).is_file()
    assert Path(result["skill"]).is_file()
    guide = Path(result["guide"]).read_text()
    skill = Path(result["skill"]).read_text()
    for name in ("search_help", "ai4e_core.run.launch", "ai4e_task"):
        assert name in guide
    for name in ("search_help", "ai4e_core.run.launch", "ai4e_task.create_project", "wait_run"):
        assert name in skill
    assert Path(result["help_root"]).is_dir()
    assert Path(result["entry"]).is_file()
    assert not (tmp_path / "guide" / "AGENTS.md").exists()
    assert source_location("ai4e_task")["path"]


def test_help_search_topic_symbol_and_export(tmp_path):
    info = help_info()
    assert info["help_contract_version"] == 1
    assert info["coverage"]["symbols"] > 1_000
    assert list_help_topics(kind="workflow")
    exact = search_help("ai4e_core.run.launch", limit=1)[0]
    assert exact["topic_id"] == "api:ai4e_core.run.launch"
    symbol = describe_help_symbol("ai4e_core.run.launch")
    assert symbol["signature"].startswith("launch(")
    assert Path(symbol["source_path"]).as_posix().endswith("run/session.py")
    topic = read_help_topic("user-component:loss")
    assert "损失" in topic["content"]
    exported = export_help(tmp_path / "offline")
    assert Path(exported["entry"]).is_file()
    assert not (tmp_path / "offline" / "AGENTS.md").exists()


def test_resource_commands_do_not_import_training_stack():
    script = """import json,sys
from ai4e_task.templates.resources import list_examples, check_example, source_location, search_help
list_examples(); check_example('parametric_pde.neumann_diffusion'); source_location('ai4e_task'); search_help('launch')
print(json.dumps({'torch': 'torch' in sys.modules, 'contrib': 'ai4e_contrib' in sys.modules}))
"""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c", script], check=True, capture_output=True, text=True
    )
    assert json.loads(result.stdout) == {"torch": False, "contrib": False}


def test_help_cli_wraps_python_api(tmp_path):
    import subprocess
    import sys

    def invoke(*args):
        result = subprocess.run(
            [sys.executable, "-m", "ai4e_task", "guide", *args, "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    hits = invoke("search", "ai4e_core.run.launch", "--limit", "1")
    assert hits[0]["topic_id"] == "api:ai4e_core.run.launch"
    topic = invoke("topic", "workflow:parametric-pde")
    assert topic["title"] == "参数化 PDE 研究流程"
    symbol = invoke("symbol", "ai4e_task.search_help")
    assert symbol["signature"].startswith("search_help(")
    exported = invoke("export", "--to", str(tmp_path / "exported"))
    assert Path(exported["entry"]).is_file()
    assert not (tmp_path / "exported/AGENTS.md").exists()


def test_documented_agent_python_apis_are_public():
    import ai4e_task as task

    from ai4e_core import run
    from ai4e_core.run import TrainingRun

    for name in (
        "list_examples",
        "check_example",
        "copy_example",
        "read_case_manifest",
        "help_info",
        "list_help_topics",
        "search_help",
        "read_help_topic",
        "describe_help_symbol",
        "export_help",
        "create_project",
        "new_task",
        "fork_task",
        "submit_run",
        "wait_run",
        "stop_run",
        "resume_run",
        "read_configuration",
        "save_configuration",
        "replace_configuration",
        "compare_runs",
    ):
        assert callable(getattr(task, name)), name
    for name in ("launch", "stage", "managed_run", "execute_operation"):
        assert callable(getattr(run, name)), name
    for name in (
        "output_dir",
        "report",
        "artifact",
        "record_asset",
        "record_metric",
        "checkpoint",
        "execute_samples",
    ):
        assert callable(getattr(TrainingRun, name)), name
