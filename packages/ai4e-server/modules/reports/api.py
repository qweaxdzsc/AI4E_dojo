"""报告为服务自有事实，运行证据固定为保存时快照。"""

from datetime import UTC, datetime

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from ...bootstrap.dependencies import services
from .domain import validate

router = APIRouter()


class Report(BaseModel):
    """文字与固定运行证据请求。"""

    title: str
    text: str = ""
    run_ids: list[str] = Field(default_factory=list)


@router.get("/projects/{project}/report")
def read(project: str, request: Request):
    """读取持久化的当前内容。"""
    s = services(request)
    s.project(project)
    try:
        return s.store.get("report", project)
    except KeyError:
        return {"title": "项目报告", "text": "", "run_ids": [], "evidence": []}


@router.put("/projects/{project}/report")
def save(project: str, body: Report, request: Request):
    """校验并保存当前编辑内容。"""
    s = services(request)
    base = s.project(project)
    value = validate(body.model_dump())
    try:
        previous = {e["id"]: e for e in s.store.get("report", project)["evidence"]}
    except KeyError:
        previous = {}
    evidence = []
    for identity in body.run_ids:
        record = task.get_run(base, identity)
        if record["status"] not in {"succeeded", "failed", "stopped"}:
            raise ValueError("evidence_requires_finished_run")
        evidence.append(previous.get(identity) or {"id": identity, "record": record})
    value["evidence"] = evidence
    value["updated_at"] = datetime.now(UTC).isoformat()
    return s.store.put("report", project, value)
