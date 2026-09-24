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


@pytest.mark.parametrize("name", ["shapenet_car_abupt", "nasa_crm_abupt"])
def test_full_abupt_fields_match_frozen_reference(tmp_path, name):
    """全点链单独对照，不能拿锚点评价指标代替完整实体集合。"""
    import shutil

    folder, cfg = case(tmp_path, name)
    fixtures = Path(__file__).resolve().parents[1]
    shutil.copyfile(fixtures / "reference_preparation_adapter.py", folder / "reference_preparation_adapter.py")
    shutil.copyfile(fixtures / "fixtures/recipe_before_explicit/physical_post.py", folder / "reference_prediction.py")
    cfg["pipeline"]["stages"] = ["trainprep", "train", "post"]
    cfg["run_root"] = str(tmp_path / "full-runs")
    cfg["data_root"] = str(tmp_path / "full-data")
    (folder / "post.py").write_text('''from configuration import application_parameters, load_components
from ai4e_core import run
import reference_prediction
from reference_preparation_adapter import compare_full_fields
def post(cfg, trained=None):
    components = load_components(cfg)
    config = application_parameters(cfg)
    config['post'].update(config['infer'])
    config['post']['checkpoint'] = trained['checkpoints']['last']
    return compare_full_fields(reference_prediction, config, components.dataset, components.model, run.TrainingRun())
''')
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder)
    assert result.returncode == 0, result.stdout + result.stderr


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
    shutil.copyfile(Path(__file__).resolve().parents[1] / "reference_preparation_adapter.py", folder / "reference_preparation_adapter.py")
    original_post = (folder / "post.py").read_text()
    (
        folder / "post.py"
    ).write_text("""from configuration import application_parameters, load_components
from ai4e_core import run
import reference_prediction
from reference_preparation_adapter import execute_reference

def post(cfg, trained=None):
    component = load_components(cfg)
    config = application_parameters(cfg)
    config['post'].update(config['infer'])
    if trained:
        config['post']['checkpoint'] = trained['checkpoints']['last']
    return execute_reference(reference_prediction, config, component.dataset, component.model, run.TrainingRun(), anchors="abupt" in component.model.__name__)
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
        **{k: v for k, v in cfg["infer"].items() if k in set(DEFAULTS) | OPTIONAL},
        "device": "cpu",
    }
    cfg["inputs"]["infer"].update(checkpoint=str(checkpoint), preparation=str(preparation))
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
        expected_domains = a["metadata"]["domains"]
        actual_domains = b["metadata"]["domains"]
        if "abupt" in name:
            # 旧记录显式 null，新锚点记录省略坐标系；实体与字段仍严格相等。
            for domain in actual_domains.values():
                domain.setdefault("coordinate_space", None)
        assert expected_domains == actual_domains
        for key in a["fields"]:
            torch.testing.assert_close(a["fields"][key], b["fields"][key], rtol=0, atol=0)
    assert open_results(directory / "artifacts/physical-predictions.json") == actual
    summary = json.loads((directory / "summary.json").read_text())
    assert summary["reports"]["post"]["results"] == actual["results"]
    # Independent post succeeds with unavailable checkpoint: it must not attempt inference.
    cfg["inputs"]["post"]["results"] = str(directory / "artifacts/physical-predictions.json")
    cfg["inputs"]["infer"]["checkpoint"] = str(tmp_path / "missing.pt")
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
    cfg.inputs.infer.checkpoint = str(trained / "checkpoints/last.pt")
    cfg.inputs.infer.preparation = str(trained / "artifacts/preparation.json")
    cfg.infer = {
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
    progress = json.loads((directory / "artifacts/inference-progress.json").read_text())
    for operation in ("evaluation", "predictions"):
        assert progress["operations"][operation]["status"] == "succeeded"
        assert progress["operations"][operation]["completed"] == 1
    assert progress["operations"]["predictions"]["samples"][0]["artifacts"]
    managed = json.loads((directory / "artifacts/task-progress.json").read_text())
    assert managed["completed"] == managed["total"] == 1
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

    from tests.wheel_environment import install_wheels

    installed, env = install_wheels(tmp_path)
    monkeypatch.setenv("PYTHONPATH", env["PYTHONPATH"])

    def snapshot():
        return {
            str(p.relative_to(installed)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in installed.rglob("*")
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
    cfg["inputs"]["infer"].update(checkpoint=str(trained / "checkpoints/last.pt"), preparation=str(trained / "artifacts/preparation.json"))
    cfg["infer"] = {
        "samples": ["Sample001", "Sample002"],
        "device": "cpu",
        "export_vtk": False,
    }
    cfg["pipeline"]["stages"] = ["infer", "post"]
    cfg["inputs"]["post"]["results"] = None
    cfg["run_root"] = str(tmp_path / "infer-runs")
    cfg["data_root"] = str(tmp_path / "predictions-data")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder)
    assert done.returncode == 0, done.stdout + done.stderr
    inferred = next(Path(cfg["run_root"]).iterdir())
    result = json.loads((inferred / "artifacts/physical-predictions.json").read_text())
    assert len(result["results"]) == 2 and result["status"] == "succeeded"
    cfg["inputs"]["post"]["results"] = str(inferred / "artifacts/physical-predictions.json")
    cfg["inputs"]["infer"]["checkpoint"] = str(tmp_path / "missing.pt")
    cfg["run_root"] = str(tmp_path / "post-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder, "post.py")
    assert done.returncode == 0, done.stdout + done.stderr
    assert before == snapshot()
    assert not list(Path(cfg["run_root"]).glob("*/artifacts/inference-progress.json"))
