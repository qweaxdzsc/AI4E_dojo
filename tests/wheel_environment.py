"""同一源码批次构建安装，逐包核对导入来源；不重装正式工作环境。"""

import os
import subprocess
import sys
from pathlib import Path


def install_wheels(directory, products=("spec", "core", "contrib", "task")):
    """返回隔离安装目录与环境；每个第一方包均从本批 wheel 导入。"""
    directory = Path(directory)
    repository = Path(__file__).resolve().parents[1]
    configured = os.environ.get("DOJO_TASK_WHEELS")
    wheels = Path(configured) if configured else directory / "wheels"
    installed = directory / "installed"
    if not configured:
        for name in products:
            result = subprocess.run(
                ["uv", "build", "--package", "ai4e-" + name, "--wheel", "--out-dir", str(wheels)],
                cwd=repository,
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            assert result.returncode == 0, result.stdout + result.stderr
    selected = []
    for name in products:
        matches = list(wheels.glob("ai4e_" + name + "-*.whl"))
        assert len(matches) == 1, (name, matches)
        selected.extend(matches)
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
            "--no-deps",
            "--target",
            str(installed),
            *map(str, selected),
        ],
        check=True,
        capture_output=True,
        timeout=180,
    )
    env = {**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"}
    code = (
        "import importlib, pathlib, sys\n"
        "root=pathlib.Path(sys.argv[1])\n"
        "for name in sys.argv[2:]:\n"
        "    module=importlib.import_module('ai4e_'+name)\n"
        "    assert pathlib.Path(module.__file__).is_relative_to(root), module.__file__\n"
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(installed), *products],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return installed, env
