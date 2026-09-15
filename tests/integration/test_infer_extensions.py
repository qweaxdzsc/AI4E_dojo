"""仓库外用户派生字段：执行、保存、读回、真实网格与失败边界。"""

import json
import shutil
from pathlib import Path

import pytest
import torch
import yaml

from tests.integration.test_recipe_explicit_equivalence import case
from tests.integration.test_recipe_extensions import ROOT, script


@pytest.mark.parametrize("invalid", [False, True])
def test_copied_recipe_derived_field_reaches_real_vtk(tmp_path, invalid):
    folder, cfg = case(tmp_path, "shapenet_car_abupt")
    cfg["pipeline"]["stages"] = ["rawprep", "trainprep", "train"]
    # 夹具只有一个六面体；保留边界点才能验证完整单元的真实网格输出。
    cfg["rawprep"]["filters"]["volume"] = []
    cfg["run_root"] = str(tmp_path / "train-runs")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder, "pipeline.py", "--overwrite")
    assert done.returncode == 0, done.stdout + done.stderr
    run = next(Path(cfg["run_root"]).iterdir())
    shutil.copyfile(
        ROOT / "examples/recipe_extensions/inference_fields/fields.py", folder / "fields.py"
    )
    shutil.copyfile(
        ROOT / "examples/recipe_extensions/inference_metrics/metrics.py", folder / "user_metrics.py"
    )
    if invalid:
        path = folder / "fields.py"
        path.write_text(
            path.read_text().replace("dim=-1, keepdim=True)", "dim=-1, keepdim=True)[:-1]")
        )
    infer = folder / "infer.py"
    infer.write_text(
        infer.read_text().replace(
            "    job = infer_stage.configure_physical_output(job)",
            """    job = infer_stage.configure_physical_output(job)
    job = infer_stage.configure_derived_fields(
        job, name="pressure_error", domain="surface", unit=None,
        inputs={"prediction": "surface.pressure.prediction", "truth": "surface.pressure.truth"},
        settings={"target": "fields.absolute_error"},
    )""",
        )
    )
    cfg["infer"] = {
        "checkpoint": str(run / "checkpoints/last.pt"),
        "preparation": str(run / "artifacts/preparation.json"),
        "samples": ["b"],
        "device": "cpu",
        "fields": ["surface:pressure:scalar", "surface:pressure_error:scalar"],
        "sample_metric": {"target": "user_metrics.physical_metrics"},
        "export_vtk": True,
    }
    cfg["pipeline"]["stages"] = ["infer"]
    cfg["run_root"] = str(tmp_path / "infer-runs")
    cfg["paths"]["datasets"]["predictions"] = str(tmp_path / "predictions")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    done = script(folder, "infer.py")
    run = next(Path(cfg["run_root"]).iterdir())
    progress = json.loads((run / "artifacts/inference-progress.json").read_text())
    if invalid:
        assert done.returncode != 0 and "派生字段输出形状" in done.stderr
        assert progress["status"] == "failed"
        assert not (tmp_path / "predictions/b/manifest.json").exists()
        assert not (run / "artifacts/physical-predictions.json").exists()
        return
    assert done.returncode == 0, done.stdout + done.stderr
    from ai4e_core.applications.aero_cfd.infer import read_sample

    saved = read_sample(tmp_path / "predictions/b/manifest.json")
    fields = saved["fields"]
    torch.testing.assert_close(
        fields["surface.pressure_error"],
        (fields["surface.pressure.prediction"] - fields["surface.pressure.truth"]).abs(),
    )
    assert (
        saved["metadata"]["domains"]["surface"]["derived_fields"]["pressure_error"]["ids"]
        == "surface.ids"
    )
    import vtk

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(str(tmp_path / "predictions/b/surface.vtp"))
    reader.Update()
    array = reader.GetOutput().GetPointData().GetArray("surface.pressure_error")
    assert array is not None and array.GetNumberOfTuples() == len(fields["surface.ids"])
    report = json.loads((run / "artifacts/inference-results.json").read_text())
    rows = report["results"][0]["metric_records"]
    assert all(row["algorithm"] == "user-physical-metrics-v1" for row in rows)
    derived = next(row for row in rows if row["field_id"] == "surface:pressure_error:scalar")
    assert all(value is None for value in derived["values"].values())
    assert "独立真值" in derived["undefined"]["relative_l2"]
    assert progress["status"] == "succeeded"
    assert progress["operations"]["derived:surface.pressure_error"]["completed"] == 1
