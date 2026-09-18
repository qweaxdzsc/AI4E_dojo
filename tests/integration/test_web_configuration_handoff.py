"""平台生成配置经过真实保存、加载与任务捕获后保持编辑语义。"""

from copy import deepcopy

import ai4e_task as task
from ai4e_server.modules.stages import compose_configuration
from omegaconf import OmegaConf

from tests.integration.test_task_management import recipe
from tests.integration.test_web_project_task import platform as platform  # noqa: PLC0414


def test_http_edit_preserves_unedited_values_and_removes_old_keys(platform):
    client, project, record, _, _ = platform
    base = client.app.state.services.project(project)
    original = task.read_configuration(base, record["id"])
    cfg = deepcopy(original["config"])
    cfg["train"]["research_note"] = "keep"
    cfg["model"]["parameters"]["research_stats"] = {"mean": 2}
    cfg["model"]["parameters"]["obsolete"] = 7
    seeded = task.replace_configuration(base, record["id"], cfg, revision=original["revision"])
    url = f"/api/v1/projects/{project}/tasks/{record['id']}/configuration"
    response = client.put(
        url,
        json={
            "stage": "model",
            "expected_revision": seeded["revision"],
            "values": {"parameters": {"dim": 192, "research_stats": {"mean": 2}}},
            "edited_paths": [["parameters", "dim"]],
            "removed_paths": [["parameters", "obsolete"]],
        },
    )
    assert response.status_code == 200, response.text
    saved = response.json()
    assert "obsolete" not in saved["config"]["model"]["parameters"]
    assert saved["config"]["train"]["research_note"] == "keep"
    assert task.read_configuration(base, record["id"])["config"] == saved["config"]
    denied = client.put(
        url,
        json={
            "stage": "train",
            "expected_revision": saved["revision"],
            "values": {"manifest": "/untrusted"},
            "edited_paths": [["manifest"]],
        },
    )
    assert denied.status_code == 400
    assert task.read_configuration(base, record["id"])["revision"] == saved["revision"]


def test_trainprep_save_accepts_empty_edit_paths(platform):
    client, project, record, _, _ = platform
    url = f"/api/v1/projects/{project}/tasks/{record['id']}/configuration"
    cfg = client.get(url, params={"stage": "trainprep"}).json()
    response = client.put(
        url,
        json={
            "stage": "trainprep",
            "expected_revision": cfg["revision"],
            "values": cfg["values"],
            "edited_paths": [],
            "removed_paths": [],
        },
    )
    assert response.status_code == 200, response.text


def test_complete_save_capture_and_recipe_consumption(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    record = task.new_task(project, "configuration", source=recipe(tmp_path))
    original = task.read_configuration(project, record["id"])
    config = compose_configuration(
        original["config"], "train", {"max_epochs": 0}, edited_paths=[["max_epochs"]]
    )
    config["score"] = 7
    saved = task.replace_configuration(project, record["id"], config, revision=original["revision"])
    run = task.submit_run(project, record["id"], expected_revision=saved["revision"])
    config["score"] = 99
    task.replace_configuration(project, record["id"], config, revision=saved["revision"])
    completed = task.wait_run(project, run["id"])
    assert completed["status"] == "succeeded", completed
    assert completed["summary"]["reports"]["train"]["score"] == 7
    snapshot = OmegaConf.load(completed["run_dir"] + "/inputs/config.yaml")
    assert snapshot.score == 7
    assert snapshot.train.max_epochs == 0


def test_real_five_case_configuration_consumption(tmp_path):
    """显式启用的真实CFD五案例：平台合成和直接配置逐值等价，完成完整预测。"""
    import json
    import os
    import shutil
    from pathlib import Path

    import pytest
    import torch
    import yaml

    from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset
    from tests.integration.test_cross_model_recipe import NAMES
    from tests.integration.test_recipe_extensions import ROOT, script
    from tests.support import SHAPENET_SAMPLES, shapenet_raw_root

    if os.environ.get("DOJO_CONFIGURATION_REAL") != "1":
        pytest.skip("真实五案例需显式 DOJO_CONFIGURATION_REAL=1，跳过不算验收")
    nasa = Path("/Users/zonghui/work/datasets/NASA")
    training = sorted(nasa.glob("*/trainingData_NASA-CRM.h5"))
    assert len(training) == 1
    nasa_source = {
        "root": str(training[0].parent),
        "train_h5": str(training[0]),
        "test_h5": str(nasa / "Case 4 - NASA CRM/testData_NASA-CRM.h5"),
        "connectivity_h5": str(nasa / "Case 4 - NASA CRM/connectivity_NASA-CRM.h5"),
    }
    names = RawDataset(nasa_source).partitions
    nasa_source["samples"] = {split: samples[:1] for split, samples in names.items()}
    nasa_source["samples"]["train"] = [
        names["train"][index * (len(names["train"]) - 1) // 4] for index in range(5)
    ]
    evidence = []
    for name in NAMES:
        folder = tmp_path / name / "recipe"
        shutil.copytree(ROOT / "examples/aero_cfd" / name, folder)
        original = yaml.safe_load((folder / "config.yaml").read_text())
        shape = name.startswith("shapenet")
        sample = str(SHAPENET_SAMPLES[1]) if shape else names["test"][0]
        original["dataset"].update(
            {
                "root": str(shapenet_raw_root()),
                "partition": {"train": [str(SHAPENET_SAMPLES[0])], "test": [sample]},
                "samples": "all",
            }
            if shape
            else nasa_source
        )
        original["data_root"] = str(folder.parent / "data")
        original["run_root"] = str(folder.parent / "raw-runs")
        original["pipeline"]["stages"] = ["rawprep"]
        original["post"].update(samples=[sample], export_vtk=False, snapshot_every=0)
        original["infer"].update(
            samples=[sample], device="cpu", export_vtk=False, query_chunk_size=4096
        )
        train = {"device": "cpu", "max_epochs": 1, "snapshot": False, "evaluation_enabled": False}
        model = deepcopy(original["model"])
        if "abupt" in name:
            model["parameters"].update(
                dim=24,
                geometry_depth=1,
                num_heads=3,
                blocks="psc" if shape else "ps",
                num_domain_decoder_blocks={key: 1 for key in original["trainprep"]["domains"]},
            )
            model["sampling"]["geometry"]["max_points"] = 32
            model["sampling"]["supernodes"]["num_points"] = 8
            for domain in model["sampling"]["domains"].values():
                domain["anchor"]["num_points"] = 16
        else:
            model["parameters"].update(n_hidden=16, n_layers=2, n_head=4, slice_num=4)
            model["sampling"].update(chunk_count=20, stride=4)
        config = compose_configuration(
            original, "train", train, edited_paths=[[key] for key in train]
        )
        config = compose_configuration(
            config, "model", model, edited_paths=[["parameters"], ["sampling"]]
        )
        config = compose_configuration(
            config,
            "rawprep",
            {"formats": ["pt", "zarr"], "vtkhdf": False},
            edited_paths=[["formats"], ["vtkhdf"]],
        )
        config = compose_configuration(
            config,
            "trainprep",
            {"normalization": {"materialize": True}},
            edited_paths=[["normalization", "materialize"]],
        )
        direct = deepcopy(original)
        direct["train"].update(train)
        direct["model"] = model
        direct["rawprep"].pop("format", None)
        direct["rawprep"].update(formats=["pt", "zarr"], vtkhdf=False)
        direct["trainprep"]["normalization"]["materialize"] = True
        assert config == direct
        (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
        result = script(folder, "rawprep.py")
        (folder / "raw.log").write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stdout + result.stderr
        config["pipeline"]["stages"] = ["trainprep", "train", "infer", "post"]
        config["run_root"] = str(folder.parent / "pipeline-runs")
        (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
        result = script(folder)
        (folder / "pipeline.log").write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stdout + result.stderr
        checkpoint = next(Path(config["run_root"]).glob("*/checkpoints/last.pt"))
        weights = torch.load(checkpoint, weights_only=False)
        assert weights["epoch"] == 1
        prediction = next(Path(config["run_root"]).glob("*/artifacts/physical-predictions.json"))
        result_manifest = json.loads(prediction.read_text())
        assert result_manifest["results"]
        from ai4e_core.abilities.data.save.zarr import read_zarr

        physical = json.loads((folder.parent / "data/manifest.json").read_text())
        for row in physical["samples"]:
            for field, filename in row["format_filemaps"]["pt"].items():
                tensor = torch.load(Path(row["path"]) / filename, weights_only=True)
                alternate = read_zarr(Path(row["path"]) / row["format_filemaps"]["zarr"][field])
                torch.testing.assert_close(tensor, alternate, rtol=0, atol=0)

        evidence.append(
            {
                "case": name,
                "checkpoint": str(checkpoint),
                "predictions": str(prediction),
                "epochs": 1,
                "device": "cpu",
            }
        )
        (tmp_path / "real-evidence.json").write_text(json.dumps(evidence, indent=2))
