"""真实样本通过 HTTP 配置与 task 运行，现有数据准备读回原产物。"""

import json
import shutil
from pathlib import Path
import numpy as np
import pytest
import torch
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import ai4e_task as task
from tests.integration.test_web_project_task import platform

SAMPLE = "param1/1dc58be25e1b6e5675cad724c63e222e"
REAL = Path("/Users/zonghui/work/datasets/shapenet_car_cfd/mlcfd_data/training_data")


def copy_real(root):
    """复制真实 CFD 输入，不生成假结果。"""
    if not (REAL / SAMPLE).is_dir():
        pytest.skip("真实 ShapeNet-Car 样本不可用")
    target = root / SAMPLE
    target.mkdir(parents=True)
    for name in ["quadpress_smpl.vtk", "hexvelo_smpl.vtk"]:
        shutil.copy2(REAL / SAMPLE / name, target / name)
    return [SAMPLE + "/" + name for name in ["quadpress_smpl.vtk", "hexvelo_smpl.vtk"]]


def test_real_rawprep_to_existing_trainprep(platform):
    c, p, t, root, _ = platform
    files = copy_real(root)
    url = f"/api/v1/projects/{p}/tasks/{t['id']}/rawprep"
    bind = f"/api/v1/projects/{p}/tasks/{t['id']}/dataset"
    current = c.get(bind).json()
    bound = c.put(
        bind,
        json={
            "expected_revision": current["revision"],
            "sources": {"root": {"root": "data0", "path": ""}},
        },
    )
    assert bound.status_code == 200, bound.text
    cfg = c.get(url).json()
    cfg["rawprep"]["vtkhdf"] = True
    saved = c.put(url, json=cfg)
    assert saved.status_code == 200, saved.text
    body = {
        "revision": saved.json()["revision"],
        "root": "data0",
        "files": files,
        "all_selected": True,
        "idempotency_key": "actual-1",
    }
    missing = c.post(url + "/preflight", json={**body, "files": files[:1]})
    assert missing.status_code == 400 and "配套文件" in missing.text
    checked = c.post(url + "/preflight", json=body)
    assert checked.status_code == 200, checked.text
    started = c.post(url + "/execute", json=body)
    assert started.status_code == 200, started.text
    project = c.app.state.services.project(p)
    result = task.wait_run(project, started.json()["id"], timeout=60)
    assert result["status"] == "succeeded", result.get("error") or task.read_log(
        project, result["id"]
    )
    published = c.get("/api/v1/datasets").json()
    assert any(item["name"] == "shapenet_car" and item["status"] == "available" for item in published)
    repeated = c.post(url + "/execute", json=body)
    assert repeated.json()["id"] == result["id"], repeated.text
    assert len(task.get_lineage(project)) == 1
    data = Path(result["data_dir"])
    manifest = data / "manifest.json"
    assert manifest.is_file()
    from ai4e_core.applications.aero_cfd.trainprep.dataset import (
        open_manifest_sample,
        prepare_physical_sample,
    )

    prepared = prepare_physical_sample(
        open_manifest_sample(manifest, partition="train"),
        rules={"zero_fields": {"surface_sdf": "surface_position"}},
    )
    assert set(prepared) >= {
        "surface_pressure",
        "surface_position",
        "surface_sdf",
        "volume_velocity",
    }
    assert prepared["surface_position"].shape[0] > 1000
    assert torch.isfinite(prepared["surface_pressure"]).all()
    record = json.loads(manifest.read_text())["samples"][0]
    tensor = torch.load(
        Path(record["path"]) / record["filemap"]["surface_pressure"], weights_only=True
    )
    torch.testing.assert_close(prepared["surface_pressure"].flatten(), tensor.flatten())
    assert prepared["surface_sdf"].count_nonzero() == 0
    input_reader = vtk.vtkDataSetReader()
    input_reader.SetFileName(str(root / files[0]))
    input_reader.Update()
    input_values = vtk_to_numpy(input_reader.GetOutput().GetPointData().GetArray("point_scalars"))
    mapping = json.loads((Path(record["path"]) / "entity_mapping.json").read_text())
    np.testing.assert_allclose(
        tensor.flatten().numpy(), input_values[mapping["surface_pressure"]["entity_ids"]].flatten()
    )
    q = {
        "root": "task",
        "path": str(
            (Path(record["path"]) / record["filemap"]["surface_pressure"]).relative_to(
                project / "tasks" / t["id"]
            )
        ),
        "task_id": t["id"],
        "operation": "preview",
    }
    preview = c.get(f"/api/v1/projects/{p}/preview", params=q)
    assert preview.status_code == 200, preview.text
    assert preview.json()["kind"] == "tensor"
    assert "rawprep" in task.read_log(project, result["id"])
    config = Path(result["run_dir"]) / "inputs/config.yaml"
    assert "trainprep" not in __import__("yaml").safe_load(config.read_text())["pipeline"]["stages"]
