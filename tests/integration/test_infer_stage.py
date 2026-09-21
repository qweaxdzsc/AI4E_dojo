"""五个真实模型小规模 CPU 推理对照、独立脚本、权重检查和结果读回。"""

import json
from pathlib import Path

import pytest
import torch
import yaml

from ai4e_core.applications.aero_cfd.infer.configuration import DEFAULTS, OPTIONAL
from tests.integration.test_cross_model_recipe import NAMES
from tests.integration.test_recipe_explicit_equivalence import case
from tests.integration.test_recipe_extensions import script


@pytest.mark.parametrize("name", NAMES)
def test_native_infer_matches_old_post_and_consumes_results(tmp_path, name):
    folder, cfg = case(tmp_path, name)
    cfg["pipeline"]["stages"] = ["trainprep", "train", "post"]
    cfg["run_root"] = str(tmp_path / "legacy-runs")
    cfg["data_root"] = str(tmp_path / "legacy-data")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    import shutil

    reference = (
        Path(__file__).resolve().parents[1] / "fixtures/recipe_before_explicit/physical_post.py"
    )
    shutil.copyfile(reference, folder / "reference_prediction.py")
    original_post = (folder / "post.py").read_text()
    (
        folder / "post.py"
    ).write_text("""from configuration import application_parameters, load_components
from ai4e_core import run
from reference_prediction import execute

def post(cfg, trained=None):
    component = load_components(cfg)
    config = application_parameters(cfg)
    if trained:
        config['post']['checkpoint'] = trained['checkpoints']['last']
    return execute(config, component.dataset, component.model, run.TrainingRun())
""")
    completed = script(folder)
    (folder / "post.py").write_text(original_post)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    original = next(Path(cfg["run_root"]).iterdir())
    checkpoint = original / "checkpoints/last.pt"
    preparation = original / "artifacts/preparation.json"
    expected = json.loads((original / "artifacts/physical-predictions.json").read_text())
    from ai4e_core.applications.aero_cfd.infer import inspect_checkpoint, inspect_inputs

    info = inspect_checkpoint(checkpoint)
    assert info["epoch"] == 2 and info["updates"] > 0 and "model" not in info
    json.dumps(info)
    prepared = inspect_inputs(checkpoint, preparation, info["effective_config"], folder)
    assert prepared["compatibility"]["status"] == "compatible", prepared
    assert prepared["partitions"]["test"]
    raw_prepared = inspect_inputs(checkpoint, preparation, cfg, folder)
    assert raw_prepared["compatibility"]["status"] == "compatible", raw_prepared
    cfg["infer"] = {
        **{k: v for k, v in cfg["post"].items() if k in set(DEFAULTS) | OPTIONAL},
        "checkpoint": str(checkpoint),
        "preparation": str(preparation),
        "device": "cpu",
    }
    cfg["pipeline"]["stages"] = ["infer", "post"]
    cfg["run_root"] = str(tmp_path / "native-runs")
    cfg["data_root"] = str(tmp_path / "native-data")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    completed = script(folder)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    directory = next(Path(cfg["run_root"]).iterdir())
    actual = json.loads((directory / "artifacts/physical-predictions.json").read_text())
    progress = json.loads((directory / "artifacts/inference-progress.json").read_text())
    assert progress["status"] == "succeeded" and progress["completed"] == len(
        cfg["infer"]["samples"]
    )
    assert actual["metrics"] == expected["metrics"]
    from ai4e_core.applications.aero_cfd.infer import open_results, read_sample

    for left, right in zip(expected["results"], actual["results"], strict=True):
        a, b = read_sample(left["manifest"]), read_sample(right["manifest"])
        assert a["metadata"]["domains"] == b["metadata"]["domains"]
        for key in a["fields"]:
            torch.testing.assert_close(a["fields"][key], b["fields"][key], rtol=0, atol=0)
    assert open_results(directory / "artifacts/physical-predictions.json") == actual
    summary = json.loads((directory / "summary.json").read_text())
    assert summary["reports"]["post"]["results"] == actual["results"]
    # Independent post succeeds with unavailable checkpoint: it must not attempt inference.
    cfg["post"] = {"results": str(directory / "artifacts/physical-predictions.json")}
    cfg["infer"]["checkpoint"] = str(tmp_path / "missing.pt")
    cfg["run_root"] = str(tmp_path / "read-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    completed = script(folder, "post.py")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert not list(Path(cfg["run_root"]).glob("*/artifacts/inference-progress.json"))


@pytest.mark.parametrize("mesh", [False, True])
def test_anchor_template_has_independent_infer_and_fixed_post(tmp_path, mesh):
    from ai4e_core.applications.aero_cfd.infer import inspect_inputs, open_results
    from tests.integration.test_train_recipe import _fit_config, _run_script, prepared_case

    folder, cfg = prepared_case(tmp_path)
    _fit_config(cfg)
    cfg.train.device = "cpu"
    done, trained, _ = _run_script(folder, cfg)
    assert done.returncode == 0, done.stderr
    cfg.infer = {
        "checkpoint": str(trained / "checkpoints/last.pt"),
        "preparation": str(trained / "artifacts/preparation.json"),
        "samples": ["b"],
        "device": "cpu",
        "fields": ["surface:pressure:scalar"],
        "query": mesh,
        "query_chunk_size": 1,
        "export_vtk": mesh,
    }
    import shutil

    shutil.copyfile(
        Path(__file__).resolve().parents[2]
        / "examples/recipe_extensions/inference_metrics/metrics.py",
        folder / "user_metrics.py",
    )
    cfg.infer.sample_metric = {"target": "user_metrics.physical_metrics"}
    done, directory, _ = _run_script(folder, cfg, entry="infer.py")
    assert done.returncode == 0, done.stderr
    result = open_results(directory / "artifacts/physical-predictions.json")
    assert result["status"] == "succeeded" and result["kind"] == "anchor-predictions"
    assert result["results"][0]["sample_id"] == "b"
    assert (directory / "artifacts/inference-progress.json").is_file()
    modern = json.loads((directory / "artifacts/inference-results.json").read_text())
    assert modern["results"][0]["metric_records"][0]["algorithm"] == "user-physical-metrics-v1"
    manifest = Path(result["results"][0]["manifest"])
    metadata = json.loads(manifest.read_text())
    assert set(metadata["domains"]) == {"surface"}
    if mesh:
        assert "surface" in metadata["meshes"]
        assert (manifest.parent / metadata["meshes"]["surface"]["path"]).is_file()
        assert not (manifest.parent / "full_volume.vtu").exists()
        records = [metadata["meshes"]["surface"], metadata["meshes"].get("surface_anchors") or {}]
        fields = [name for record in records for name in (record.get("fields") or [])]
        assert any(name.endswith(".prediction") or name in {"pred_pressure"} for name in fields)
        assert any(name.endswith(".truth") or name in {"gt_pressure"} for name in fields)
        assert metadata.get("vtk", {}).get("exported") is True
    else:
        assert metadata.get("vtk", {}).get("exported") is False
        assert metadata.get("vtk", {}).get("reason")
    effective = yaml.safe_load((trained / "inputs/config.yaml").read_text())
    inputs = inspect_inputs(
        trained / "checkpoints/last.pt", trained / "artifacts/preparation.json", effective, folder
    )
    assert inputs["compatibility"]["status"] == "compatible", inputs


def test_wheel_installed_external_recipe_infer_and_post(tmp_path, monkeypatch):
    """真实构建安装到隔离目标，外部复制案例不依赖仓库源码导入。"""
    import hashlib
    import os
    import subprocess
    import sys

    from tests.integration.test_recipe_extensions import ROOT

    wheels = tmp_path / "wheels"
    done = subprocess.run(
        ["uv", "build", "--package", "ai4e-core", "--wheel", "--out-dir", str(wheels)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    installed = tmp_path / "installed"
    done = subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            sys.executable,
            "--no-deps",
            "--target",
            str(installed),
            str(next(wheels.glob("*.whl"))),
        ],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    monkeypatch.setenv("PYTHONPATH", str(installed))
    done = subprocess.run(
        [
            sys.executable,
            "-c",
            "import ai4e_core; from pathlib import Path; import os; assert Path(ai4e_core.__file__).is_relative_to(Path(os.environ['PYTHONPATH']))",
        ],
        env=dict(os.environ),
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert done.returncode == 0, done.stderr

    def snapshot():
        return {
            str(p.relative_to(installed)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (installed / "ai4e_core").rglob("*")
            if p.is_file() and "__pycache__" not in p.parts
        }

    before = snapshot()
    (tmp_path / "outside").mkdir()
    folder, cfg = case(tmp_path / "outside", "nasa_crm_transolver3")
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    cfg["run_root"] = str(tmp_path / "train-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder)
    assert done.returncode == 0, done.stdout + done.stderr
    trained = next(Path(cfg["run_root"]).iterdir())
    cfg["infer"] = {
        "checkpoint": str(trained / "checkpoints/last.pt"),
        "preparation": str(trained / "artifacts/preparation.json"),
        "samples": ["Sample001", "Sample002"],
        "device": "cpu",
        "export_vtk": False,
    }
    cfg["pipeline"]["stages"] = ["infer", "post"]
    cfg["post"] = {"results": None}
    cfg["run_root"] = str(tmp_path / "infer-runs")
    cfg["data_root"] = str(tmp_path / "predictions-data")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder)
    assert done.returncode == 0, done.stdout + done.stderr
    inferred = next(Path(cfg["run_root"]).iterdir())
    result = json.loads((inferred / "artifacts/physical-predictions.json").read_text())
    assert len(result["results"]) == 2 and result["status"] == "succeeded"
    cfg["post"]["results"] = str(inferred / "artifacts/physical-predictions.json")
    cfg["infer"]["checkpoint"] = str(tmp_path / "missing.pt")
    cfg["run_root"] = str(tmp_path / "post-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder, "post.py")
    assert done.returncode == 0, done.stdout + done.stderr
    assert before == snapshot()
    assert not list(Path(cfg["run_root"]).glob("*/artifacts/inference-progress.json"))
