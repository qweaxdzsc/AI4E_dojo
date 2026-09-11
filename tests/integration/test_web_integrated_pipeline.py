"""主 Agent 独立验收：真实服务、工作进程及二进制数组的跨包交接。"""

import hashlib
import importlib.util
import time
from pathlib import Path

import numpy as np

from tests.integration.test_web_project_task import platform  # noqa: F401


def wait_operation(client, base, operation):
    """等待辅助操作完成，保留失败快照作为断言上下文。"""
    deadline = time.monotonic() + 40
    while operation["status"] in {"queued", "running"}:
        assert time.monotonic() < deadline, operation
        time.sleep(0.05)
        response = client.get(base + "/operations/" + operation["operation_id"])
        assert response.status_code == 200, response.text
        operation = response.json()
    assert operation["status"] == "succeeded", operation
    return operation


def test_api_vtk_worker_binary_roundtrip(platform):  # noqa: F811 - 复用 pytest 夹具
    """真实文件经 HTTP 登记和独立 VTK 进程，二进制坐标与场保持原值。"""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk

    client, project, _, data, _ = platform
    points = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 3.0, 0.0]], dtype=np.float64)
    field = np.array([7.0, 11.0, 19.0], dtype=np.float64)
    mesh = vtk.vtkPolyData()
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(points, deep=True))
    mesh.SetPoints(vtk_points)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(3, [0, 1, 2])
    mesh.SetPolys(cells)
    array = numpy_to_vtk(field, deep=True)
    array.SetName("pressure")
    mesh.GetPointData().AddArray(array)
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(str(data / "surface.vtp"))
    writer.SetInputData(mesh)
    assert writer.Write() == 1
    base = f"/api/v1/projects/{project}"
    response = client.post(base + "/assets", json={"root": "data0", "path": "surface.vtp"})
    assert response.status_code == 200, response.text
    source = response.json()
    response = client.post(
        base + "/visualization/operations",
        json={"source": source, "operation": "transform", "options": {"pipeline": []}},
    )
    assert response.status_code == 200, response.text
    operation = wait_operation(client, base, response.json())
    manifest = operation["result"]
    ref = operation["result_refs"][0]

    def read(buffer):
        result = client.get(
            base + f"/assets/{ref['asset_id']}/content",
            params={"member": buffer["path"], "revision": ref["revision"]},
        )
        assert result.status_code == 200, result.text
        assert len(result.content) == buffer["byte_length"]
        assert hashlib.sha256(result.content).hexdigest() == buffer["sha256"]
        return np.frombuffer(result.content, dtype=buffer["dtype"]).reshape(buffer["shape"])

    np.testing.assert_array_equal(read(manifest["geometry_buffers"][0]), points)
    pressure = next(f for f in manifest["fields"] if f["field_id"] == "point:pressure")
    np.testing.assert_array_equal(read(pressure["buffer"]), field)
    assert (
        client.get(
            base + f"/assets/{ref['asset_id']}/content", params={"member": "../outside"}
        ).status_code
        == 400
    )


def test_browser_contracts_are_generated_from_shared_source():
    """跨语言字段变更必须同时出现在浏览器契约，防止手写类型漂移。"""
    root = Path(__file__).resolve().parents[2]
    source = root / "packages/ai4e-web/scripts/generate-platform-contracts.py"
    spec = importlib.util.spec_from_file_location("contract_generator", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.TARGET.read_text() == module.generate()


def run_real_http_case(api_url: str, identities: Path, name: str, reference: Path, evidence: Path):
    """显式验收真实四阶段 HTTP 流程；保持案例模型尺寸，仅采用已声明短程预算。"""
    import json
    from uuid import uuid4

    import httpx
    import yaml

    request_namespace = uuid4().hex
    ids = json.loads(identities.read_text())
    project, task_id = ids["project"], ids["tasks"][name]
    config = yaml.safe_load(reference.read_text())
    client = httpx.Client(base_url=api_url.rstrip("/") + "/api/v1", timeout=180)
    base = f"/projects/{project}"
    task_url = base + f"/tasks/{task_id}"
    records = {
        "case": name,
        "project": project,
        "task": task_id,
        "request_namespace": request_namespace,
        "stages": {},
    }
    evidence.mkdir(parents=True, exist_ok=True)

    def request(method, path, **kwargs):
        response = client.request(method, path, **kwargs)
        assert response.is_success, (method, path, response.status_code, response.text)
        return response.json()

    def save(stage, values):
        current = request("GET", task_url + "/configuration")
        return request(
            "PUT",
            task_url + "/configuration",
            json={
                "stage": stage,
                "expected_revision": current["revision"],
                "values": values,
            },
        )

    samples = config["dataset"]["samples"]
    if samples == "all":
        samples = [v for group in config["dataset"]["partition"].values() for v in group]
    if name.startswith("nasa"):
        current = request("GET", task_url + "/configuration")
        sources = {
            key: {
                "root": "data3",
                "path": str(
                    Path(config["dataset"][key]).relative_to("/Users/zonghui/work/datasets/NASA")
                ),
            }
            for key in ("train_h5", "test_h5", "connectivity_h5")
        }
        request(
            "PUT",
            task_url + "/dataset",
            json={"expected_revision": current["revision"], "sources": sources},
        )
    save("rawprep", config["rawprep"])
    save("train", {"max_epochs": 1, "device": "mps", "snapshot": False})
    save("post", {"samples": config["post"]["samples"]})
    bindings = {}
    for stage in ("rawprep", "trainprep", "train", "post"):
        current = request("GET", task_url + "/configuration")
        selection = {"samples": samples, "bindings": bindings}
        payload = {
            "mode": "execute",
            "expected_revision": current["revision"],
            "selection": selection,
            "inputs": list(bindings.values()),
            "idempotency_key": f"integrated-{request_namespace}-{name}-{stage}-{current['revision']}",
        }
        started = request("POST", task_url + f"/stages/{stage}/operations", json=payload)
        run_id = started["id"]
        deadline = time.monotonic() + 600
        while True:
            run = request("GET", base + f"/runs/{run_id}")
            if run["status"] in {"succeeded", "failed", "stopped", "interrupted"}:
                break
            assert time.monotonic() < deadline, run
            time.sleep(1)
        log = request("GET", base + f"/runs/{run_id}/log")["text"]
        (evidence / f"{name}-{stage}.log").write_text(log)
        records["stages"][stage] = run
        (evidence / f"{name}.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))
        assert run["status"] == "succeeded", (name, stage, run.get("error"), log[-8000:])
        repeated = request("POST", task_url + f"/stages/{stage}/operations", json=payload)
        assert repeated["id"] == run_id
        inputs = request("GET", task_url + "/stage-inputs")
        for item in inputs:
            if item["run_id"] == run_id:
                bindings[item["binding"]] = item["ref"]
        if stage == "rawprep":
            assert "train.manifest" in bindings, inputs
        elif stage == "trainprep":
            assert "train.preparation" in bindings, inputs
        elif stage == "train":
            assert "post.checkpoint" in bindings, inputs
        print(f"{name}: {stage} succeeded ({run_id})", flush=True)
    assert len(request("GET", base + "/lineage")) == len(ids["tasks"])
    client.close()
    return records


def verify_real_delivery(api_url: str, record_path: Path) -> dict:
    """独立读盘对照 HTTP 张量切片与实际预测网格，不能用状态成功代替内容。"""
    import json

    import httpx
    import torch
    import vtk

    records = json.loads(record_path.read_text())
    post = records["stages"]["post"]
    base = f"/api/v1/projects/{records['project']}"
    project_root = Path(post["run_dir"]).parents[3]
    report_path = Path(post["run_dir"]) / "artifacts/physical-predictions.json"
    report = json.loads(report_path.read_text())
    assert report["status"] == "succeeded"
    manifest_path = Path(report["results"][0]["manifest"])
    manifest = json.loads(manifest_path.read_text())
    prediction_key = next(key for key in manifest["filemap"] if key.endswith(".prediction"))
    prediction_path = manifest_path.parent / manifest["filemap"][prediction_key]
    expected = torch.load(prediction_path, weights_only=True).numpy()
    assert expected.shape[0] > 1000 and np.isfinite(expected).all()
    with httpx.Client(base_url=api_url, timeout=180) as client:

        def register(path):
            response = client.post(
                base + "/assets",
                json={
                    "root": "project",
                    "path": str(path.relative_to(project_root)),
                    "task_id": records["task"],
                },
            )
            assert response.is_success, response.text
            return response.json()

        source = register(prediction_path)
        response = client.post(
            base + "/previews/operations",
            json={
                "source": source,
                "operation": "read_slice",
                "options": {"limit": 3},
            },
        )
        assert response.is_success, response.text
        preview = wait_operation(client, base, response.json())["result"]
        assert preview["shape"] == list(expected.shape)
        np.testing.assert_array_equal(preview["rows"], expected[:3].reshape(3, -1))
        mesh_paths = sorted(manifest_path.parent.glob("*.vtp"))
        assert mesh_paths, manifest_path
        mesh_path = mesh_paths[0]
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(str(mesh_path))
        reader.Update()
        mesh = reader.GetOutput()
        mesh_source = register(mesh_path)
        response = client.post(
            base + "/visualization/operations",
            json={
                "source": mesh_source,
                "operation": "transform",
                "options": {"pipeline": []},
            },
        )
        assert response.is_success, response.text
        operation = wait_operation(client, base, response.json())
        display = operation["result"]
        assert display["geometry_buffers"][0]["shape"] == [mesh.GetNumberOfPoints(), 3]
        ref = operation["result_refs"][0]
        buffer = display["geometry_buffers"][0]
        response = client.get(
            base + f"/assets/{ref['asset_id']}/content",
            params={
                "revision": ref["revision"],
                "member": buffer["path"],
            },
        )
        assert response.is_success, response.text
        from vtk.util.numpy_support import vtk_to_numpy

        actual = np.frombuffer(response.content, dtype=buffer["dtype"]).reshape(buffer["shape"])
        np.testing.assert_array_equal(actual, vtk_to_numpy(mesh.GetPoints().GetData()))
        evidence = {
            "case": records["case"],
            "prediction": source,
            "prediction_shape": list(expected.shape),
            "mesh": mesh_source,
            "display": ref,
            "points": mesh.GetNumberOfPoints(),
            "tensor_values_equal": True,
            "mesh_coordinates_equal": True,
        }
    record_path.with_name(record_path.stem + "-preview.json").write_text(
        json.dumps(evidence, indent=2)
    )
    return evidence


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="通过真实 HTTP/task 执行指定完整模型案例")
    parser.add_argument("--api", default="http://127.0.0.1:8002")
    parser.add_argument("--identities", type=Path, required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    run_real_http_case(args.api, args.identities, args.case, args.reference, args.evidence)
