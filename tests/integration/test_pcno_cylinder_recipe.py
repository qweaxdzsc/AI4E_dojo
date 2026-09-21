"""可复制案例的真实阶段交接与公开参数失败边界。"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from ai4e_task import copy_example

from ai4e_contrib.application.spatiotemporal_pde.pcno.configuration import validate
from tests.integration.test_pcno_cylinder_training import tiny  # noqa: F401


def test_copied_recipe_real_training_and_fixed_post(tiny, tmp_path):  # noqa: F811
    cfg, prep, _ = tiny
    case = tmp_path / "case"
    copy_example("pcno.double_cylinder", case)
    cfg["pipeline"]["stages"] = ["train", "infer", "post"]
    cfg["inputs"]["train"]["preparation"] = prep
    cfg["inputs"]["infer"]["preparation"] = prep
    (case / "config.yaml").write_text(yaml.safe_dump(cfg))
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(case / "pipeline.py"),
            "--config",
            str(case / "config.yaml"),
        ],
        cwd=tmp_path,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(next(Path(cfg["run_root"]).glob("*/summary.json")).read_text())
    report = json.loads(Path(summary["reports"]["post"]["comparison"]).read_text())
    assert report["windows"] == 1 and set(report["aggregate"]) == {
        "initial",
        "persistence",
        "supervised",
        "physics",
    }


@pytest.mark.parametrize(
    "change",
    [
        lambda c: c["train"].update(updates=0),
        lambda c: c["train"].update(batch_size=2),
        lambda c: c["loss"].update(warmup_fraction=0.9, ramp_fraction=0.2),
        lambda c: c["inputs"]["infer"].update(unknown="x"),
    ],
)
def test_invalid_public_configuration(tiny, change):  # noqa: F811
    cfg, _, _ = tiny
    change(cfg)
    with pytest.raises(ValueError):
        validate(cfg)
