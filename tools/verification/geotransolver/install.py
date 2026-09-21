"""在独立环境安装真实四包 wheel，复用机器第三方依赖而不重装正式环境。"""

import os
import subprocess
import sys
import sysconfig
from pathlib import Path


def install(root):
    """构建并安装隔离副本，返回解释器和干净环境变量。"""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    repo = Path(__file__).resolve().parents[3]
    wheels = root / "wheels"
    venv = root / "venv"
    for name in ("ai4e-spec", "ai4e-core", "ai4e-contrib", "ai4e-task"):
        subprocess.run(
            ["uv", "build", "--package", name, "--wheel", "--out-dir", str(wheels)],
            cwd=repo,
            check=True,
        )
    if not (venv / "bin/python").exists():
        subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--python",
                sys.executable,
                "python",
                "-m",
                "venv",
                "--system-site-packages",
                str(venv),
            ],
            check=True,
        )
    site = (
        venv / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    )
    (site / "third_party.pth").write_text(sysconfig.get_path("purelib") + "\n")
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "VIRTUAL_ENV"}}
    python = venv / "bin/python"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            "--reinstall",
            *[
                str(next(wheels.glob(name + "-*.whl")))
                for name in ("ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task")
            ],
        ],
        cwd=root,
        env=env,
        check=True,
    )
    probe = """import json,sys,ai4e_spec,ai4e_core,ai4e_contrib,ai4e_task
from pathlib import Path
from ai4e_contrib.ability.model.geotransolver import GeoTransolver
root=Path(sys.prefix).resolve()
modules=[ai4e_spec,ai4e_core,ai4e_contrib,ai4e_task]
assert all(Path(m.__file__).resolve().is_relative_to(root) for m in modules)
assert not any(x.startswith("physicsnemo") for x in sys.modules)
assert (Path(ai4e_core.__file__).parent/"Notice/physicsnemo/LICENSE").is_file()
assert (Path(ai4e_contrib.__file__).parent/"ability/model/geotransolver/LICENSE").is_file()
print(json.dumps({m.__name__:m.__file__ for m in modules}))"""
    result = subprocess.run(
        ["uv", "run", "--no-project", "--python", str(python), "python", "-c", probe],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    (root / "installed-paths.json").write_text(result.stdout)
    return python, env


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    a = p.parse_args()
    install(a.root)
