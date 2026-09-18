"""执行公开文档中的配置例子，并核对真实扩展产物。"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import ai4e_task as task
import yaml

from ai4e_contrib.application.spatiotemporal_pde.wdno.configuration import load_configuration
from tests.integration.test_wdno_recipe import ROOT, fixture
from tools.verification.wdno.task_replay import direct, managed


def test_documented_configuration_and_extension_execute(tmp_path):
    code = tmp_path / "research"
    seed = fixture(code)
    extension = ROOT / "examples/recipe_extensions/wdno"
    for name in ("config.yaml", "pipeline.py", "audit.py", "variants.py"):
        shutil.copy2(extension / name, code / name)
    text = (extension / "README.md").read_text().split("<!-- wdno-configure-example -->", 1)[1]
    script = re.search(r"```python\n(.*?)```", text, re.DOTALL).group(1)
    setup = code / "configure_variant.py"
    setup.write_text(script)
    subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(setup),
            seed["inputs"]["rawprep"]["source"],
            seed["inputs"]["rawprep"]["indices"],
        ],
        cwd=tmp_path.parent,
        check=True,
        capture_output=True,
    )
    cfg = load_configuration(code / "config.yaml")
    assert cfg["model"]["dim"] == 8 and cfg["train"]["device"] == "cpu"
    assert cfg["components"]["objective"] == "variants.custom_loss"
    first = direct(code, cfg)
    project = tmp_path / "project"
    task.create_project(project)
    current = task.new_task(project, "documented-variant", source=code, configuration=cfg)
    second, _ = managed(project, current, cfg)
    for summary in (first, second):
        assert [x["stage"] for x in summary["stage_events"]] == [
            "rawprep",
            "trainprep",
            "train",
            "infer",
            "audit",
            "post",
        ]
        assert all(x["energy_readback_passed"] for x in summary["reports"]["audit"].values())
        prediction = summary["reports"]["infer"]["test"]
        assert "energy" in json.loads(Path(prediction).read_text())["fields"]
    assert yaml.safe_load((code / "config.yaml").read_text())["train"]["updates"] == 2
