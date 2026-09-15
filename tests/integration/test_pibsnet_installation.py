"""实际 wheel、仓外复制模板和已安装用户函数的真实短训验收。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("case", ["neumann_diffusion", "advection", "diffusion_trapezoid"])
def test_installed_wheels_and_copied_recipe(tmp_path, case):
    wheels, target = tmp_path / "wheels", tmp_path / "installed"
    for package in ("ai4e-spec", "ai4e-core", "ai4e-contrib"):
        subprocess.run(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )
    # 用户组件作为可安装包，不依赖工作目录碰巧可导入。
    user = tmp_path / "components"
    user.mkdir()
    (user / "pyproject.toml").write_text("""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "pibsnet-user-example"
version = "0.0.1"
[tool.hatch.build.targets.wheel]
packages = ["my_pde"]
""")
    (user / "my_pde").mkdir()
    (user / "my_pde/__init__.py").write_text("")
    (user / "my_pde/training.py").write_text("""import torch
def training_step(model, batch):
    parameters = next(model.parameters())
    inputs = torch.tensor([[batch["sample"]["parameters"]["nu"]]], device=parameters.device, dtype=parameters.dtype)
    values = model(inputs)
    loss = values.square().mean()
    return {"loss": loss, "losses": {"user_coefficient_penalty": loss}}
""")
    subprocess.run(
        ["uv", "pip", "install", "--no-deps", "--target", str(target), str(user)],
        check=True,
        capture_output=True,
    )
    recipe = tmp_path / "copied_recipe"
    shutil.copytree(
        ROOT / "recipes/parametric_pde", recipe, ignore=shutil.ignore_patterns("__pycache__")
    )
    env = {**os.environ, "PYTHONPATH": str(target), "OMP_NUM_THREADS": "1"}

    def invoke(*args):
        return subprocess.run(
            ["uv", "run", "--no-project", "--python", sys.executable, "python", *args],
            cwd=tmp_path,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    probe = invoke(
        "-c",
        "import ai4e_core, ai4e_contrib, ai4e_spec, my_pde.training; import json; print(json.dumps([m.__file__ for m in [ai4e_core,ai4e_contrib,ai4e_spec,my_pde.training]]))",
    )
    assert all(str(target) in path for path in json.loads(probe.stdout))
    invoke(
        "-c",
        "import torch; from ai4e_contrib.ability.constraint.equations import burgers; z=torch.zeros(3); assert torch.equal(burgers(u=z,u_t=z,u_x=z,u_xx=z,convection_coefficient=1.,viscosity=.1),z)",
    )
    generation = {
        "case": case,
        "output": str(tmp_path / "dataset"),
        "train": 2,
        "test": 1,
        "nx": 9,
        "nt": 101 if case == "diffusion_trapezoid" else 7,
        **({"ny": 5, "nx": 7} if case == "diffusion_trapezoid" else {}),
    }
    (recipe / "generate.yaml").write_text(yaml.safe_dump(generation))
    invoke(str(recipe / "generate.py"), "--config", str(recipe / "generate.yaml"))
    config = {
        "case": case,
        "dataset": {"manifest": str(tmp_path / "dataset/manifest.json")},
        "run_root": str(tmp_path / "runs"),
        "trainprep": {"output": str(tmp_path / "prepared")},
        "model": {
            "control_points": [5, 5, 5] if case == "diffusion_trapezoid" else [5, 5],
            "degree": 3,
            "hidden_dim": 8,
            "sampling": {"supervised": {"method": "random_without_replacement", "num_points": 12}},
        },
        "train": {
            "max_epochs": 2,
            "device": "cpu",
            "snapshot": False,
            "step": "my_pde.training.training_step" if case == "neumann_diffusion" else None,
        },
        "post": {"output": str(tmp_path / "predictions")},
    }
    (recipe / "config.yaml").write_text(yaml.safe_dump(config))
    invoke(str(recipe / "pipeline.py"), "--config", str(recipe / "config.yaml"))
    result = json.loads((tmp_path / "predictions/predictions.json").read_text())
    assert result["status"] == "complete" and len(result["samples"]) == 1
    protocol = next((tmp_path / "runs").glob("*/artifacts/training-protocol.json"), None)
    if protocol is None:
        protocol = next((tmp_path / "runs").rglob("training-protocol.json"))
    assert bool(json.loads(protocol.read_text())["contract"]["user_step"]) == (
        case == "neumann_diffusion"
    )
