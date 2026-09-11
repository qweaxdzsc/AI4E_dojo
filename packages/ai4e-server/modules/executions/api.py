"""真实执行和日志；事件连接断开不改变任务状态。"""

import asyncio
import json

import ai4e_task as task
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from ...bootstrap.dependencies import services
from ...infrastructure.transport import finite_values

router = APIRouter(prefix="/projects/{project}/runs")


@router.get("")
def listing(project: str, request: Request, task_id: str | None = None):
    """查询当前范围内的真实管理记录。"""
    return task.list_runs(services(request).project(project), task_id)


@router.post("/{identity}/stop")
def stop(project: str, identity: str, request: Request):
    """请求停止既有运行并返回核对状态。"""
    return task.stop_run(services(request).project(project), identity)


@router.get("/{identity}")
def detail(project: str, identity: str, request: Request):
    """读取已有对象详情，不创建新运行。"""
    return task.get_run(services(request).project(project), identity)


@router.get("/{identity}/log")
def log(project: str, identity: str, request: Request):
    """读取既有运行日志。"""
    return {"text": task.read_log(services(request).project(project), identity)}


@router.get("/{identity}/events")
async def events(project: str, identity: str, request: Request):
    """订阅运行快照及日志，断开不改变运行。"""
    base = services(request).project(project)

    async def stream():
        """协调此范围内的公开用例。"""
        seq = 0
        while not await request.is_disconnected():
            state = await run_in_threadpool(task.get_run, base, identity)
            text = await run_in_threadpool(task.read_log, base, identity)
            seq += 1
            yield (
                "id: "
                + str(seq)
                + "\ndata: "
                + json.dumps(
                    finite_values({"status": state["status"], "text": text}),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n\n"
            )
            if state["status"] in {"succeeded", "failed", "stopped"}:
                break
            await asyncio.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/{identity}/resume")
def resume(project: str, identity: str, request: Request):
    """从固定检查点恢复既有配置，不增加版本。"""
    return task.resume_run(services(request).project(project), identity)


@router.get("/{identity}/metrics")
def metrics(project: str, identity: str, request: Request):
    """只展示运行已有记录和可读取的本机进程资源。"""
    return task.read_run_metrics(services(request).project(project), identity)
