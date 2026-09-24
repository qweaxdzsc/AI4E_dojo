"""框架连接与案例说明在配套wheel中独立读回，保留命令和内容摘要。"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_installed_state_hooks_and_portable_discovery(tmp_path):
    root = Path(__file__).resolve().parents[2]
    wheels, installed = tmp_path / "wheels", tmp_path / "installed"
    records = []

    def command(args, cwd, env=None):
        result = subprocess.run(
            args, cwd=cwd, env=env, text=True, capture_output=True, timeout=240, check=False
        )
        records.append(
            {
                "args": args,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        (tmp_path / "commands.json").write_text(json.dumps(records, indent=2))
        assert result.returncode == 0, result.stdout + result.stderr

    for package in ("ai4e-spec", "ai4e-core", "ai4e-task"):
        command(["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)], root)
    command(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        tmp_path,
    )
    pairs = {
        "packages/ai4e-core/abilities/training/checkpoint.py": "ai4e_core/abilities/training/checkpoint.py",
        "packages/ai4e-core/abilities/training/iterations.py": "ai4e_core/abilities/training/iterations.py",
        "packages/ai4e-core/applications/base/iteration_training.py": "ai4e_core/applications/base/iteration_training.py",
        "packages/ai4e-task/templates/example_docs.py": "ai4e_task/templates/example_docs.py",
        "DOJO_AGENT_GUIDE.md": "ai4e_task/resources/DOJO_AGENT_GUIDE.md",
        ".agents/skills/dojo-research/SKILL.md": "ai4e_task/resources/.agents/skills/dojo-research/SKILL.md",
    }
    digests = {}
    for source, target in pairs.items():
        assert (root / source).read_bytes() == (installed / target).read_bytes()
        digests[source] = hashlib.sha256((installed / target).read_bytes()).hexdigest()
    (tmp_path / "source-hashes.json").write_text(json.dumps(digests, indent=2))
    env = {**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"}
    probe = tmp_path / "probe.py"
    probe.write_text(PROBE)
    prefix = ["uv", "run", "--no-project", "--python", sys.executable, "python"]
    command([*prefix, str(probe), str(installed)], tmp_path, env)
    shutil.copy2(
        root / "tests/integration/test_training_state_bindings.py", tmp_path / "test_state.py"
    )
    command(
        [
            *prefix,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "test_state.py",
            "--basetemp",
            str(tmp_path / "state-runs"),
        ],
        tmp_path,
        env,
    )


PROBE = r"""
import hashlib,json,sys
from pathlib import Path
import ai4e_core,ai4e_spec,ai4e_task as task
from ai4e_task.templates import resources
installed=Path(sys.argv[1])
for module in (ai4e_core,ai4e_spec,task):
    assert Path(module.__file__).is_relative_to(installed)
filtered=task.list_examples(data_form="regular_grid",training_pattern="iteration")
assert any(c["id"]=="recipe_extensions.research_state" for c in filtered)
task.export_guide("offline")
assert (Path("offline")/".agents/skills/dojo-research/SKILL.md").is_file()
for name in ("tail_batch","research_state"):
    case_id="recipe_extensions."+name
    destination=Path("copies")/name
    receipt=task.copy_example(case_id,destination)
    assert set(receipt["documentation"]["sources"])=={"base","extension"}
    assert (destination/receipt["documentation"]["entry"]).is_file()
    cases={c["id"]:c for c in task.list_examples()}
    for role,info in receipt["documentation"]["sources"].items():
        assert hashlib.sha256((destination/info["path"]).read_bytes()).hexdigest()==info["sha256"]
        source=cases[receipt["base_case"] if role=="base" else case_id]
        original=resources.resource_root()/"examples"/source["path"]/"README.md"
        assert hashlib.sha256(original.read_bytes()).hexdigest()==info["source_sha256"]
    page=task.read_help_topic("case:"+case_id)
    assert "案例详细说明" in page["content"] and "基案例完整说明" in page["content"]
    exported=Path("offline/docs/agent-help/examples/cases/recipe_extensions")/(name+".md")
    assert exported.read_text()==page["content"]
print(json.dumps({"installed":str(installed),"cases":len(task.list_examples()),"passed":True}))
"""
