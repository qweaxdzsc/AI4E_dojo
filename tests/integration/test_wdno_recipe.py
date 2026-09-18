"""真实 wheel、仓库外复制、完整阶段、续训和自由变体。"""

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def installed(tmp_path_factory):
    target = tmp_path_factory.mktemp("wdno-wheel")
    wheels = target / "wheels"
    for package in ("ai4e-spec", "ai4e-core", "ai4e-contrib", "ai4e-task"):
        subprocess.run(
            ["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    dest = target / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(dest),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )
    return dest


def run_script(case, stage, cfg, installed):
    path = case / "config.yaml"
    path.write_text(yaml.safe_dump(cfg))
    proc = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            str(case / f"{stage}.py"),
            "--config",
            str(path),
        ],
        cwd=case.parent,
        env={**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(
        max(
            Path(cfg["run_root"]).glob("*/summary.json"), key=lambda p: p.stat().st_mtime_ns
        ).read_text()
    )


def fixture(case, *, source="recipes/wdno"):
    case.mkdir()
    for path in (ROOT / source).glob("*"):
        if path.is_file():
            shutil.copy2(path, case / path.name)
    raw = case.parent / "raw"
    raw.mkdir()
    torch.manual_seed(7)
    sources = {}
    for split in ("train", "test"):
        path = raw / f"{split}.pt"
        torch.save({"u": torch.randn(4, 81, 120), "f": torch.randn(4, 80, 120)}, path)
        sources[split] = {
            "file": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    (raw / "protocol.json").write_text(json.dumps({"sources": sources}))
    (raw / "indices.json").write_text(json.dumps({"train": [0, 1], "validation": [2], "test": [0]}))
    cfg = yaml.safe_load((case / "config.yaml").read_text())
    cfg["run_root"] = str(case.parent / "runs")
    cfg["data_root"] = str(case.parent / "data")
    cfg["inputs"]["rawprep"].update(
        source=str(raw / "protocol.json"),
        indices=str(raw / "indices.json"),
    )
    cfg["model"].update(dim=8, dim_mults=[1, 2], ddim_steps=2)
    cfg["train"].update(updates=2, batch_size=2, device="cpu")
    cfg["infer"].update(device="cpu", batch_size=1)
    return cfg


@pytest.mark.parametrize("source", ["recipes/wdno", "examples/wdno/burgers_base"])
def test_installed_copied_pipeline_resume_post_and_variant(tmp_path, installed, source):
    case = tmp_path / "case"
    cfg = fixture(case, source=source)
    summary = run_script(case, "pipeline", cfg, installed)
    assert not summary["failed"]
    reports = summary["reports"]
    checkpoint = reports["train"]["checkpoint"]
    assert reports["train"]["updates"] == 2
    sources = list(Path(summary["run_dir"]).rglob("wdno-recipe.json"))
    assert len(sources) == 1
    saved = json.loads(sources[0].read_text())
    assert saved["pipeline.py"]["text"] == (case / "pipeline.py").read_text()
    assert reports["post"]["test"]["samples"] == 1
    original_pred = np.load(Path(reports["infer"]["test"]).parent / "prediction.npy")
    cfg["inputs"]["post"] = reports["infer"]
    post = run_script(case, "post", cfg, installed)
    assert post["reports"]["post"] == reports["post"]
    assert np.array_equal(
        original_pred, np.load(Path(reports["infer"]["test"]).parent / "prediction.npy")
    )
    for stage in ("train", "infer"):
        cfg["inputs"][stage].update(
            preparation=reports["trainprep"]["train"],
            validation=reports["trainprep"]["validation"],
            test=reports["trainprep"]["test"],
        )
    cfg["inputs"]["train"]["resume"] = checkpoint
    cfg["train"].update(updates=3)
    resumed = run_script(case, "train", cfg, installed)
    assert resumed["reports"]["train"]["updates"] == 3
    state = torch.load(
        resumed["reports"]["train"]["checkpoint"], weights_only=False, map_location="cpu"
    )
    assert len(state["history"]) == 3 and int(state["ema"]["step"]) == 3
    # 实际研究目录定义网络、目标与派生输出，不修改框架或注册表。
    shutil.copy2(ROOT / "examples/recipe_extensions/wdno/variants.py", case / "variants.py")
    variant = copy.deepcopy(cfg)
    variant["inputs"]["train"]["resume"] = None
    variant["train"].update(updates=2, lr=0.0002)
    variant["data_root"] = str(tmp_path / "variant-data")
    variant["components"].update(
        network="variants.custom_network",
        objective="variants.custom_loss",
        derived="variants.energy",
    )
    trained = run_script(case, "train", variant, installed)
    variant["inputs"]["infer"]["checkpoint"] = trained["reports"]["train"]["checkpoint"]
    inferred = run_script(case, "infer", variant, installed)
    path = Path(inferred["reports"]["infer"]["test"])
    info = json.loads(path.read_text())
    assert info["metadata"]["derived_fields"]["energy"] == {
        "units": "u^2",
        "axes": ["sample", "time"],
    }
    energy = np.load(path.parent / "energy.npy")
    prediction = np.load(path.parent / "prediction.npy")
    np.testing.assert_array_equal(energy, np.mean(prediction**2, axis=-1))
    assert info["metadata"]["provenance"]["derived"]["callable"] == "variants.energy"
    variant["inputs"]["post"] = inferred["reports"]["infer"]
    assert run_script(case, "post", variant, installed)["reports"]["post"]["test"]["samples"] == 1


def test_raw_selection_leakage_and_mutation(tmp_path):
    from ai4e_contrib.application.spatiotemporal_pde.wdno.data import read
    from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays

    case = tmp_path / "case"
    cfg = fixture(case)
    path = Path(cfg["inputs"]["rawprep"]["indices"])
    path.write_text(json.dumps({"train": [0, 1], "validation": [1], "test": [0]}))
    with pytest.raises(ValueError, match="泄漏"):
        read(
            {
                "protocol": cfg["inputs"]["rawprep"]["source"],
                "indices": cfg["inputs"]["rawprep"]["indices"],
            }
        )
    manifest = save_arrays(tmp_path / "arrays", {"a": np.ones((2, 3))}, kind="test", metadata={})
    np.save(Path(manifest).parent / "a.npy", np.zeros((2, 3)))
    with pytest.raises(ValueError, match="改变"):
        read_arrays(manifest, kind="test")
