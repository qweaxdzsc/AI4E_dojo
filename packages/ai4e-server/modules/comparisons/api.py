"""比较委托 task，保留真实差异及固定身份。"""

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel

from ...bootstrap.dependencies import services

router = APIRouter()


class Compare(BaseModel):
    """显式比较对象请求。"""

    mode: str
    left: str
    right: str | None = None
    parameter: str | None = None


@router.post("/projects/{project}/compare")
def compare(project: str, body: Compare, request: Request):
    """比较明确版本、工作目录或运行对象。"""
    base = services(request).project(project)
    if body.mode == "worktree":
        return task.compare_worktree(base, body.left)
    if body.mode == "versions":
        result = task.compare_versions(base, body.left, body.right)
        if body.parameter:

            def selected(version):
                details = task.read_version_details(base, version)
                path = body.parameter.split(".")
                stage = next((v for v in details["stages"] if v["stage"] == path[0]), None)
                value = stage["configuration"] if stage else None
                for key in path[1:]:
                    if not isinstance(value, dict) or key not in value:
                        return {"available": False, "revision": details["revision"]}
                    value = value[key]
                return {
                    "available": stage is not None,
                    "value": value,
                    "revision": details["revision"],
                }

            result["parameter_comparison"] = {
                "path": body.parameter,
                "source": "creation_snapshot",
                "left": selected(body.left),
                "right": selected(body.right),
            }
        return result
    if body.mode == "runs":
        return task.compare_runs(base, body.left, body.right)
    raise ValueError("invalid_comparison_mode")


@router.post("/projects/{project}/comparisons")
def save_comparison(project: str, body: Compare, request: Request):
    """固化当次比较结果，后续运行不替换比较事实。"""
    from datetime import UTC, datetime
    from uuid import uuid4

    value = compare(project, body, request)
    identity = uuid4().hex
    return services(request).store.put(
        "comparison",
        identity,
        {
            "project_id": project,
            "comparison_id": identity,
            "created_at": datetime.now(UTC).isoformat(),
            "selection": body.model_dump(),
            "result": value,
        },
    )


@router.get("/projects/{project}/comparisons")
def comparisons(project: str, request: Request):
    """列出固定比较记录。"""
    services(request).project(project)
    return [v for v in services(request).store.list("comparison") if v["project_id"] == project]


@router.get("/projects/{project}/comparisons/{identity}")
def comparison(project: str, identity: str, request: Request):
    """读取固定比较，不重新绑定最新运行。"""
    value = services(request).store.get("comparison", identity)
    if value["project_id"] != project:
        raise KeyError(identity)
    return value


class DifferenceRequest(BaseModel):
    """差值输入分别固定值包和身份描述，禁止浏览器传本机路径。"""

    task_id: str
    expected_revision: str
    inputs: list[dict]
    idempotency_key: str | None = None


@router.post("/projects/{project}/comparisons/{identity}/differences")
def differences(project: str, identity: str, body: DifferenceRequest, request: Request):
    """通过任务公开算法门面执行严格差值，不配准或插值。"""
    from pathlib import Path

    from ..visualization.application import asset, submit_model_inspection

    service = services(request)
    saved = comparison(project, identity, request)
    if saved["selection"]["mode"] != "runs" or len(body.inputs) != 2:
        raise ValueError("difference_requires_two_fixed_runs")
    references = []
    resolved = []
    for selected, run_id in zip(
        body.inputs, [saved["selection"]["left"], saved["selection"]["right"]], strict=True
    ):
        run = task.get_run(service.project(project), run_id)
        record = {}
        for key, target in [("asset_ref", "path"), ("metadata_ref", "metadata_path")]:
            ref = selected[key]
            path = asset(service, project, ref)
            if not any(
                path.is_relative_to(Path(run[root]).resolve()) for root in ["run_dir", "data_dir"]
            ):
                raise ValueError("difference_input_run_mismatch")
            references.append(ref)
            record[target] = str(path)
        resolved.append(record)
    return submit_model_inspection(
        service,
        project,
        body.task_id,
        body.expected_revision,
        {"comparison_inputs": resolved},
        references,
        body.idempotency_key,
        operation="compare_fields",
    )
