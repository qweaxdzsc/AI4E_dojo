"""推理导出管理；算法与文件写出在core隔离进程执行。"""

from pathlib import Path
from uuid import uuid4

from ..projects.project import open_project
from ..storage.files import write_json
from ..storage.layout import task_dir
from .checkpoints import file_digest, inspect_inference
from .inference_results import inference_results
from .records import get_task


def export_inference(project, task_id, batch_id, request):
    """固定批次导出，不接受客户端路径，不改变原运行和任务版本。"""
    if get_task(project, task_id).get("archived") or open_project(project).get("archived"):
        raise ValueError("archived")
    if set(request) - {"format", "selection"} or request.get("format") not in {"csv", "xlsx"}:
        raise ValueError("invalid_inference_export")
    value = inference_results(project, task_id, batch_id)
    if not value["records"]:
        raise ValueError("inference_metrics_not_available")
    name = uuid4().hex + "." + request["format"]
    path = task_dir(project, task_id) / "data/inference_exports" / batch_id / name
    from .operation_sources import operation_context

    result = inspect_inference(
        "export",
        context=operation_context(project, task_id, batch_id=batch_id),
        arguments={"value": value, "path": str(path), **request},
    )
    receipt = {
        **result,
        "name": name,
        "path": str(Path(path).resolve()),
        "revision": file_digest(path),
        "batch_id": batch_id,
        "task_id": task_id,
        "selection": request.get("selection"),
        "sources": [
            {
                k: row.get(k)
                for k in ("run_id", "checkpoint_revision", "protocol", "split", "sample")
            }
            for row in value["records"]
        ],
    }
    write_json(task_dir(project, task_id) / ".dojo/inference_exports" / (name + ".json"), receipt)
    return receipt
