"""真实受控数据绑定到原始处理和产物预览；不使用模拟 HDF5 或算法替身。"""

import json
import os
import time
from pathlib import Path
from uuid import uuid4

import numpy as np
import pytest
import torch
import yaml
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient

RECIPE = Path(__file__).resolve().parents[2] / "recipes/aero_cfd"
SAMPLE = "param1/1dc58be25e1b6e5675cad724c63e222e"


def checked(response):
    """保留服务原始响应，失败可定位到实际业务值。"""
    assert response.status_code == 200, (
        f"{response.request.url}: {response.status_code} {response.text}"
    )
    return response.json()


@pytest.fixture
def real_binding_platform():
    """仅引用已有真实输入；本次运行和缓存归用户指定实验目录。"""
    raw = Path(os.environ.get("DOJO_BINDING_SHAPENET", "/private/tmp/dojo-web-acceptance/raw"))
    nasa = Path(os.environ.get("DOJO_BINDING_NASA", "/Users/zonghui/work/datasets/NASA"))
    training = sorted(nasa.glob("*/trainingData_NASA-CRM.h5"))
    assert len(training) == 1, f"请明确真实 NASA training 来源，当前发现：{training}"
    testing = nasa / "Case 4 - NASA CRM/testData_NASA-CRM.h5"
    connectivity = nasa / "Case 4 - NASA CRM/connectivity_NASA-CRM.h5"
    for path in (
        raw / SAMPLE / "quadpress_smpl.vtk",
        raw / SAMPLE / "hexvelo_smpl.vtk",
        testing,
        connectivity,
    ):
        assert path.is_file(), f"真实输入缺失，不能声明链路验收：{path}"
    output_root = os.environ.get("DOJO_BINDING_REAL_ROOT")
    assert output_root, "请显式设置 DOJO_BINDING_REAL_ROOT，真实产物根不得隐式回退临时或生产目录"
    parent = Path(output_root).expanduser().resolve()
    root = parent / uuid4().hex
    root.mkdir(parents=True)
    # 特意登记两个不同 NASA 数据根，验证来源可以跨根且始终保持受控引用。
    settings = Settings(root, RECIPE, [raw, training[0].parent, testing.parent])
    with TestClient(create_app(settings)) as client:
        project = checked(client.post("/api/v1/projects", json={"name": "真实绑定链验收"}))["id"]
        yield client, f"/api/v1/projects/{project}", root


def test_real_public_catalog_identifies_complete_copies(real_binding_platform):
    """真实数据根按 contrib 声明识别 ShapeNet 目录与 NASA 三文件，一次保存为 valid。"""
    client, base, _ = real_binding_platform
    task = checked(client.post(base + "/tasks", json={"name": "catalog", "case_id": "shapenet_car_abupt"}))
    url = base + "/tasks/" + task["id"]
    catalog = checked(client.get(url + "/datasets"))
    names = {item["dataset_id"]: item for item in catalog["datasets"]}
    assert set(names) == {"shapenet_car", "nasa_crm"}
    assert names["shapenet_car"]["instances"] and names["nasa_crm"]["instances"]
    shapenet = names["shapenet_car"]["instances"][0]
    nasa = names["nasa_crm"]["instances"][0]
    before = checked(client.get(url + "/dataset"))
    bound = checked(
        client.put(
            url + "/dataset",
            json={
                "expected_revision": before["revision"],
                "dataset_id": "nasa_crm",
                "instance_id": nasa["id"],
            },
        )
    )
    assert bound["status"] == "valid" and bound["dataset_id"] == "nasa_crm", bound
    assert set(bound["sources"]) == {"train_h5", "test_h5", "connectivity_h5"}
    restored = checked(
        client.put(
            url + "/dataset",
            json={
                "expected_revision": bound["revision"],
                "dataset_id": "shapenet_car",
                "instance_id": shapenet["id"],
            },
        )
    )
    assert restored["status"] == "valid" and restored["dataset_id"] == "shapenet_car", restored
    assert set(restored["sources"]) == {"root"}
    assert checked(client.get(url))["version_id"] == task["version_id"]


@pytest.mark.parametrize("storage_format", ["pt", "zarr"])
@pytest.mark.parametrize("case", ["shapenet_car_abupt", "nasa_crm_transolver3"])
def test_real_binding_catalog_execute_and_preview(real_binding_platform, case, storage_format):
    """新建未绑定案例，经受控绑定、明确样本选择，真实处理一个样本并预览。"""
    client, base, evidence_root = real_binding_platform
    task = checked(client.post(base + "/tasks", json={"name": case, "case_id": case}))
    url = base + "/tasks/" + task["id"]
    initial = checked(client.get(url + "/dataset"))
    assert initial["status"] == "unbound" and initial["sources"] == {}, initial
    is_nasa = case.startswith("nasa")
    sources = (
        {
            "train_h5": {"root": "data1", "path": "trainingData_NASA-CRM.h5"},
            "test_h5": {"root": "data2", "path": "testData_NASA-CRM.h5"},
            "connectivity_h5": {"root": "data2", "path": "connectivity_NASA-CRM.h5"},
        }
        if is_nasa
        else {"root": {"root": "data0", "path": ""}}
    )
    bound = checked(
        client.put(
            url + "/dataset", json={"expected_revision": initial["revision"], "sources": sources}
        )
    )
    assert bound["status"] == "valid" and bound["sources"] == sources, bound
    assert bound["revision"] != initial["revision"]
    assert checked(client.get(url + "/dataset")) == bound
    config = checked(client.get(url + "/rawprep"))
    config["rawprep"]["format"] = storage_format
    saved = checked(client.put(url + "/rawprep", json=config))
    selected_files = (
        [ref["root"] + "::" + ref["path"] for ref in sources.values()]
        if is_nasa
        else [SAMPLE + "/quadpress_smpl.vtk", SAMPLE + "/hexvelo_smpl.vtk"]
    )
    selection = {
        "revision": saved["revision"],
        "root": "data0",
        "files": selected_files,
        "all_selected": True,
    }
    if not is_nasa:
        selection["samples"] = [SAMPLE]
    catalog = checked(client.post(url + "/rawprep/catalog", json=selection))
    assert catalog["dataset_id"] == bound["dataset_id"] and catalog["fields"], catalog
    assert catalog["samples"] and all("path" not in source for source in catalog["sources"])
    chosen = next(sample for sample in catalog["samples"] if sample["partition"] == "train")
    selection["samples"] = (
        [chosen["partition"] + "::" + chosen["sample_id"]] if is_nasa else [chosen["sample_id"]]
    )
    dependencies = {source["source_id"]: source for source in catalog["sources"]}
    required = {dependencies[key]["relative_path"] for key in chosen["dependencies"]}
    assert required <= set(selected_files), {"required": required, "selected": selected_files}
    missing = client.post(
        url + "/rawprep/preflight", json={**selection, "files": sorted(required)[1:]}
    )
    assert missing.status_code == 400 and "配套文件" in missing.text, missing.text
    preflight = checked(client.post(url + "/rawprep/preflight", json=selection))
    assert preflight["sample_count"] == 1 and preflight["samples"] == [chosen["sample_id"]], (
        preflight
    )
    assert set(preflight["files"]) == required
    selection["idempotency_key"] = "real-binding-single-sample"
    started = checked(client.post(url + "/rawprep/execute", json=selection))
    deadline = time.monotonic() + 300
    while True:
        run = checked(client.get(base + "/runs/" + started["id"]))
        if run["status"] not in {"queued", "running", "pending", "starting"}:
            break
        assert time.monotonic() < deadline, {
            "run": run,
            "log": checked(client.get(base + "/runs/" + started["id"] + "/log")),
        }
        time.sleep(0.25)
    log = checked(client.get(base + "/runs/" + run["id"] + "/log"))["text"]
    assert run["status"] == "succeeded", {"run": run, "log": log}
    assert "rawprep" in log
    assert len(checked(client.get(base + "/runs", params={"task_id": task["id"]}))) == 1
    assert len(checked(client.get(base + "/lineage"))) == 1
    assert checked(client.get(url))["version_id"] == task["version_id"]
    data = Path(run["data_dir"])
    assert data.is_relative_to(evidence_root), run
    manifest = json.loads((data / "manifest.json").read_text())
    assert len(manifest["samples"]) == 1, manifest
    frozen = yaml.safe_load((Path(run["run_dir"]) / "inputs/config.yaml").read_text())
    assert frozen["pipeline"]["stages"] == ["rawprep"], frozen["pipeline"]
    tensors = sorted(data.rglob(("surface_cp." if is_nasa else "surface_pressure.") + storage_format))
    assert len(tensors) == 1, list(data.rglob("*.pt"))
    from ai4e_core.abilities.data.save.store import load_named_tensor

    tensor = load_named_tensor(tensors[0])
    assert isinstance(tensor, torch.Tensor) and tensor.shape[0] > 1000
    from ai4e_core.applications.aero_cfd.trainprep.dataset import open_manifest_sample

    prepared = open_manifest_sample(data / "manifest.json", partition="train")
    field = "surface_cp" if is_nasa else "surface_pressure"
    torch.testing.assert_close(prepared[field].flatten(), tensor.flatten())
    task_root = Path(run["run_dir"]).parent.parent
    preview = checked(
        client.get(
            base + "/preview",
            params={
                "root": "task",
                "task_id": task["id"],
                "path": str(tensors[0].relative_to(task_root)),
                "operation": "preview",
            },
        )
    )
    assert preview["kind"] == "tensor" and preview["shape"] == list(tensor.shape), preview
    np.testing.assert_allclose(
        np.asarray(preview["rows"]),
        tensor[: len(preview["rows"])].reshape(len(preview["rows"]), -1).numpy(),
        rtol=1e-6,
    )
    (evidence_root / "binding-result.json").write_text(
        json.dumps(
            {
                "case": case,
                "storage_format": storage_format,
                "preparation_readback": field,
                "binding": bound,
                "selection": selection,
                "preflight": preflight,
                "run": run,
                "preview": preview,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
