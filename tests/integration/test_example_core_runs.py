"""direct-core 入口契约；真实数据 smoke 通过显式环境变量运行。"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "case_id",
    [
        "aero_cfd.shapenet_car_transolver3_surface",
        "parametric_pde.neumann_diffusion",
        "gencp.turek_hron_cno",
        "safediffcon.burgers",
        "wdno.burgers_base",
    ],
)
def test_five_research_workflows_expose_direct_core_entry(case_id):
    """五类纵向教程都落到一个完整案例及公开 core 启动入口。"""
    import json

    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text())
    case = next(item for item in manifest["cases"] if item["id"] == case_id)
    root = ROOT / "examples" / case["path"]
    assert case["type"] == "standalone"
    assert "run.launch" in (root / case["entry"]).read_text()
    for stage in case["stages"]:
        assert (root / stage).is_file()
        if stage != "generate.py":
            assert "run.launch" in (root / stage).read_text(), (case_id, stage)


def test_neumann_stage_scripts_use_public_launch():
    case = ROOT / "examples/parametric_pde/neumann_diffusion"
    for name in ("pipeline.py", "rawprep.py", "trainprep.py", "train.py", "infer.py", "post.py"):
        assert "run.launch" in (case / name).read_text()


@pytest.mark.skipif(not os.environ.get("DOJO_EXAMPLE_SMOKE"), reason="显式开启仓库外 Neumann smoke")
def test_neumann_direct_core_smoke(tmp_path):
    source = ROOT / "examples/parametric_pde/neumann_diffusion"
    case = tmp_path / "neumann"
    shutil.copytree(source, case)
    config = yaml.safe_load((case / "config.yaml").read_text())
    config["train"]["max_epochs"] = 1
    config["train"]["device"] = "cpu"
    (case / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    generated = subprocess.run(
        [sys.executable, str(case / "generate.py"), "--config", str(case / "generate.yaml")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert generated.returncode == 0, generated.stdout + generated.stderr
    run = subprocess.run(
        [
            sys.executable,
            str(case / "pipeline.py"),
            "--set",
            "train.max_epochs=1",
            "--set",
            "train.device=cpu",
        ],
        cwd=tmp_path.parent,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert list((tmp_path / "runs").rglob("summary.json"))
