"""实际 wheel、仓库外复制、参数修改和真实条件/输出扩展验收。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = Path("/Users/zonghui/work/project_simulation/dojo_train/gencp/raw")


def test_installed_copy_pipeline_and_condition_extension(tmp_path):
    if not (DATA / "NTcouple/decouple_train/neu.npy").is_file():
        pytest.skip("需要实际核热数据；缺环境不算验收")
    wheels = tmp_path / "wheels"
    for package in ("ai4e-spec", "ai4e-core", "ai4e-contrib"):
        subprocess.run(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)],
            cwd=ROOT,
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
    shutil.copytree(ROOT / "recipes/gencp", copied, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("custom.py", "extension.py", "retrain.py"):
        shutil.copy2(ROOT / "examples/recipe_extensions/gencp" / name, copied / name)
    cfg = yaml.safe_load((ROOT / "examples/gencp/ntcouple_sit_fno/config.yaml").read_text())
    cfg["run_root"] = str(tmp_path / "runs")
    cfg["data"].update(
        train_count=4, val_count=1
    )
    cfg["inputs"]["rawprep"]["source"] = str(DATA)
    cfg["data_root"] = str(tmp_path / "data")
    cfg["train"].update(updates=2, evaluate_every=1, single_points=3, device="cpu")
    cfg["infer"].update(flow_steps=3, device="cpu")
    cfg["fields"]["fluid"]["lr"] = 0.0002
    config = copied / "config.yaml"
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    env = {
        **os.environ,
        "PYTHONPATH": str(installed),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
    }
    probe = subprocess.run(
        [sys.executable, "-c", "import ai4e_contrib; print(ai4e_contrib.__file__)"],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert Path(probe.stdout.strip()).is_relative_to(installed)

    def execute(script):
        result = subprocess.run(
            [sys.executable, "-B", str(copied / script), "--config", str(config)],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    execute("pipeline.py")
    first = next((tmp_path / "data").glob("*/infer/results/results.json"))
    cfg["inputs"]["train"]["preparation"] = str(next((tmp_path / "data").glob("*/trainprep/preparation.json")))
    cfg["inputs"]["infer"]["preparation"] = cfg["inputs"]["train"]["preparation"]
    cfg["inputs"]["infer"]["checkpoint"] = str(next((tmp_path / "data").glob("*/train/weights.json")))
    cfg["data_root"] = str(tmp_path / "variant")
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    execute("extension.py")
    second = next((tmp_path / "variant").glob("*/infer/results/results.json"))
    assert not np.array_equal(
        np.load(first.parent / "fluid_prediction.npy"),
        np.load(second.parent / "fluid_prediction.npy"),
    )
    derived = next((tmp_path / "variant").glob("*/extension/speed/results.json"))
    record = json.loads(derived.read_text())
    assert record["metadata"]["unit"] == "m/s"
    assert np.load(derived.parent / "speed_prediction.npy").shape == (1, 16, 64, 12, 1)
    assert (derived.parent / "analysis/metrics.json").is_file()
    group = json.loads(Path(cfg["inputs"]["infer"]["checkpoint"]).read_text())
    assert group["fields"]["fluid"]["contract"]["training"]["lr"] == 0.0002
    # 从真实旧组只重训一个场，组内场的更新次数不必相同。
    original_group_bytes = Path(cfg["inputs"]["infer"]["checkpoint"]).read_bytes()
    cfg["data_root"] = str(tmp_path / "retrained")
    cfg["fields"]["fluid"]["updates"] = 1
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    execute("retrain.py")
    replacement = json.loads(next((tmp_path / "retrained").glob("*/retrain/weights.json")).read_text())
    assert Path(cfg["inputs"]["infer"]["checkpoint"]).read_bytes() == original_group_bytes
    for field in ("neutron", "solid"):
        assert replacement["fields"][field] == group["fields"][field]
    assert replacement["fields"]["fluid"]["updates"] == 1
    assert replacement["fields"]["fluid"]["sha256"] != group["fields"]["fluid"]["sha256"]
    regenerated = next((tmp_path / "retrained").glob("*/infer/results/results.json"))
    assert not np.array_equal(
        np.load(first.parent / "fluid_prediction.npy"),
        np.load(regenerated.parent / "fluid_prediction.npy"),
    )
    assert next((tmp_path / "retrained").glob("*/post/analysis/metrics.json")).is_file()
    # 独立 post 只给固定结果；取消准备和检查点仍可运行。
    cfg["inputs"]["post"]["results"] = str(first)
    cfg["inputs"]["train"]["preparation"] = None
    cfg["inputs"]["infer"]["checkpoint"] = None
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    execute("post.py")
