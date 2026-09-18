"""实际 wheel、外部复制扩展、字段与图片读回验收。"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from tests.integration.test_post_analysis_recipe import saved_sample


def test_wheel_external_custom_visualization(tmp_path):
    root = Path(__file__).resolve().parents[2]
    wheels = tmp_path / "wheels"
    for package in ("ai4e-spec", "ai4e-core", "ai4e-contrib"):
        subprocess.run(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)],
            cwd=root,
            check=True,
            capture_output=True,
        )
    installed = tmp_path / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )
    copied = tmp_path / "research"
    shutil.copytree(root / "examples/recipe_extensions/physical_visualization", copied)
    manifest, report = saved_sample(tmp_path / "input")
    result = subprocess.run(
        [sys.executable, "-B", str(copied / "post.py"), str(manifest), str(tmp_path / "output")],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(installed)},
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert list((tmp_path / "output").glob("*/*/figures/custom_speed.png"))
    assert not list(installed.glob("**/*.png"))
    # 相同实际 wheel 同时运行完整官方 post 模板，配置从仓库外目录解析。
    official = tmp_path / "official"
    shutil.copytree(root / "examples/aero_cfd/shapenet_car_abupt", official)
    cfg = yaml.safe_load((official / "config.yaml").read_text())
    cfg["pipeline"]["stages"] = ["post"]
    cfg["data_root"] = str(tmp_path / "data")
    cfg["run_root"] = str(tmp_path / "runs")
    cfg["post"].update(
        analysis_enabled=True,
        results=str(report),
        samples=[],
        fields=["volume:velocity:magnitude"],
        figures=["slice"],
        slice_origin=[0.5] * 3,
        image_size=[320, 240],
    )
    (official / "config.yaml").write_text(yaml.safe_dump(cfg))
    result = subprocess.run(
        [sys.executable, "-B", str(official / "post.py"), "--set", "post.cmap=magma"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(installed)},
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert list((tmp_path / "data/post").glob("*/*/figures/velocity_slice.png"))
    import json

    manifest = next((tmp_path / "data/post").glob("*/*/manifest.json"))
    files = json.loads(manifest.read_text())["files"]
    assert next(item for item in files if item["kind"] == "image")["parameters"]["cmap"] == "magma"


def test_missing_optional_dependency_only_fails_when_called(tmp_path):
    """隔离进程模拟未安装 PyVista；导入与数值评价成功，三维调用明确报错。"""
    code = """import builtins
original = builtins.__import__
def blocked(name, *args, **kwargs):
    if name == "pyvista" or name.startswith("pyvista."):
        raise ImportError("not installed")
    return original(name, *args, **kwargs)
builtins.__import__ = blocked
from ai4e_core.applications.aero_cfd import post
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays
assert evaluate_arrays([[1.]], [[1.]])["values"]["mae"] == 0
from ai4e_core.abilities.postproc.visualization import slice_mesh
try:
    slice_mesh(None, origin=[0,0,0], normal=[1,0,0])
except ImportError as error:
    assert "ai4e-core[post]" in str(error)
else:
    raise AssertionError("expected missing optional dependency")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
