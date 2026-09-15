"""真实 wheel 在源码之外安装，并核对 Python/CLI 管理操作。"""

import json
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest


def test_wheel_install_outside_checkout(tmp_path):
    configured = os.environ.get("DOJO_TASK_WHEELS")
    wheels = Path(configured) if configured else tmp_path / "wheels"
    if not configured:
        subprocess.run(
            ["uv", "build", "--all-packages", "--wheel", "--out-dir", str(wheels)],
            cwd=Path(__file__).resolve().parents[2],
            check=True,
            capture_output=True,
            text=True,
        )
    names = ["ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"]
    files = [next(wheels.glob(name + "-*.whl"), None) for name in names]
    if any(file is None for file in files):
        pytest.fail("先构建四个 workspace wheel，并用 DOJO_TASK_WHEELS 指定目录")
    envdir = tmp_path / "venv"
    # 只复用机器已有第三方训练依赖；四个产品包必须安装到新环境。
    subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", str(envdir)],
        check=True,
        capture_output=True,
    )
    python = envdir / "bin/python"
    # venv 的 system-site-packages 指向基础 Python，并不包含父 venv。
    # 显式复用已安装第三方依赖；下方断言仍要求所有产品包来自新 wheel。
    target_site = (
        envdir
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    (target_site / "third_party.pth").write_text(sysconfig.get_path("purelib") + "\n")
    clean = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
    subprocess.run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--force-reinstall",
            *[str(f) for f in files],
        ],
        cwd=tmp_path,
        env=clean,
        check=True,
        capture_output=True,
        text=True,
    )
    probe = subprocess.run(
        [
            str(python),
            "-c",
            'import sys, ai4e_task, ai4e_core, ai4e_spec; import json; print(json.dumps({"path":ai4e_task.__file__,"core":ai4e_core.__file__,"spec":ai4e_spec.__file__,"torch":"torch" in sys.modules} ))',
        ],
        cwd=tmp_path,
        env=clean,
        check=True,
        capture_output=True,
        text=True,
    )
    info = json.loads(probe.stdout)
    assert all(str(envdir) in info[key] for key in ("path", "core", "spec"))
    assert info["torch"] is False
    cli = envdir / "bin/ai4e"
    project = tmp_path / "installed-study"

    def invoke(*args):
        return json.loads(
            subprocess.run(
                [str(cli), *map(str, args), "--json"],
                cwd=tmp_path,
                env=clean,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )

    invoke("project", "new", project)
    first = invoke("new", "root", "--project", project)
    second = invoke("fork", first["id"], "--project", project)
    assert second["parent_version_id"] == first["version_id"]
    assert len(invoke("tree", "--project", project)) == 2
    from tests.integration.test_task_management import recipe

    source = recipe(tmp_path)
    runnable = invoke("new", "runnable", "--project", project, "--from", source)
    completed = invoke("run", runnable["id"], "--project", project, "--wait", "--timeout", "30")
    assert completed["status"] == "succeeded", completed
    assert completed["lineage"]["version_id"] == runnable["version_id"]

    # 同一真实 wheel 环境执行仓库外完整用户字段扩展，覆盖安装包与模板交接。
    from tests.integration.test_recipe_extensions import extension_case

    folder, _ = extension_case(tmp_path / "extension", "field_mapping")
    result = subprocess.run(
        [str(python), "-B", str(folder / "pipeline.py")],
        cwd=tmp_path,
        env={**clean, "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "extension/data/train/a/volume_speed.pt").is_file()
    assert list((tmp_path / "extension/records").glob("*/checkpoints/last.pt"))

    subprocess.run(
        [str(python), "-m", "ai4e_task", "--help"],
        cwd=tmp_path,
        env=clean,
        check=True,
        capture_output=True,
    )
