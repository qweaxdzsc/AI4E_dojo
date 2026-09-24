"""构建真实 wheel，在仓库外独立环境复跑两项能力的行为与恢复测试。"""

import json
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path


def test_installed_foundational_capabilities(tmp_path):
    root = Path(__file__).resolve().parents[2]
    wheels, environment = tmp_path / "wheels", tmp_path / "environment"
    records = []

    def command(args, *, cwd=tmp_path, env=None):
        result = subprocess.run(
            args, cwd=cwd, env=env, capture_output=True, text=True, timeout=240, check=False
        )
        records.append(
            {
                "command": list(map(str, args)),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        (tmp_path / "installation-evidence.json").write_text(json.dumps(records, indent=2))
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    for package in ("ai4e-spec", "ai4e-core", "ai4e-task"):
        command(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)], cwd=root
        )
    command(["uv", "venv", "--python", sys.executable, "--system-site-packages", str(environment)])
    python = str(environment / "bin/python")
    # 复用已安装的第三方依赖，只读；本轮两个 Dojo wheel 安装在优先级更高的独立环境。
    site = (
        environment
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    (site / "audit-third-party-runtime.pth").write_text(sysconfig.get_path("purelib") + "\n")
    command(
        ["uv", "pip", "install", "--python", python, "--no-deps", *map(str, wheels.glob("*.whl"))]
    )
    research = tmp_path / "research"
    tests = research / "tests/integration"
    tests.mkdir(parents=True)
    (research / "tests/__init__.py").touch()
    (tests / "__init__.py").touch()
    for name in ("test_epoch_stream.py", "test_metric_selection.py"):
        shutil.copy2(root / "tests/integration" / name, tests / name)
    env = {
        **os.environ,
        "DOJO_CAPABILITY_INSTALLED": "1",
        "PYTHONPATH": str(research),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "1",
    }
    probe = command(
        [
            python,
            "-c",
            "import ai4e_core, ai4e_spec, ai4e_task; print(ai4e_core.__file__); print(ai4e_spec.__file__); print(ai4e_task.__file__)",
        ],
        cwd=research,
        env=env,
    )
    for path in probe.stdout.splitlines():
        assert Path(path).is_relative_to(environment)
    command(
        [
            python,
            "-c",
            """from pathlib import Path
import ai4e_task as task
task.export_guide("offline")
page = Path("offline/docs/agent-help/capabilities/training.md").read_text()
assert "EpochBatchStream" in page and "BestMetric" in page
for name in ("epoch_stream.EpochBatchStream", "selection.BestMetric"):
    symbol = "ai4e_core.abilities.training." + name
    assert task.search_help(symbol, limit=1)[0]["topic_id"] == "api:" + symbol
print("installed help export and both public symbols verified")
""",
        ],
        cwd=research,
        env=env,
    )
    command(
        [
            python,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            str(tests),
            "--basetemp",
            str(tmp_path / "installed-test-runs"),
        ],
        cwd=research,
        env=env,
    )
