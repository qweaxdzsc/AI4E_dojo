"""后处理用例：授权任务结果，并通过task公开接口调度评价。"""

from pathlib import Path

import ai4e_task as task

from ..visualization import register


def _file(service, project, identity, file):
    base = Path(service.project(project)).resolve()
    path = Path(file["path"]).resolve()
    if not path.is_relative_to(base):
        raise ValueError("结果不在当前项目范围内")
    relative = str(path.relative_to(base))
    ref = register(service, project, "project", relative, identity)
    if file.get("revision") and file["revision"] != ref["revision"]:
        raise ValueError("post_file_revision_conflict")
    return {**file, "path": relative, "root": "project", "task_id": identity, "ref": ref}


def _public_file(service, project, identity, file):
    """列举只回相对路径，不登记、不读内容。"""
    if file.get("directory"):
        return {
            **{k: v for k, v in file.items() if k != "path" or v},
            "path": file.get("tree_path", file.get("path", "")),
            "root": "project",
            "task_id": identity,
            "directory": True,
        }
    base = Path(service.project(project)).resolve()
    path = Path(file["path"]).resolve()
    if not path.is_relative_to(base):
        raise ValueError("结果不在当前项目范围内")
    relative = str(path.relative_to(base))
    return {
        **file,
        "path": relative,
        "source_path": relative,
        "root": "project",
        "task_id": identity,
        "directory": False,
    }


def results(
    service,
    project,
    identity,
    *,
    offset=0,
    limit=500,
    batch=None,
    query="",
    directory=None,
    view="catalog",
    run_id=None,
    sample=None,
    split=None,
    status=None,
):
    """指标目录与按层文件树分开；打开树不登记资产。"""
    if view == "catalog":
        value = task.post_results(service.project(project), identity)
        return {
            "items": [
                {k: v for k, v in i.items() if k not in {"manifest", "files"}}
                for i in value["items"]
            ],
            "batches": value["batches"],
            "errors": value["errors"],
            "total": 0,
            "files": [],
        }
    if view != "files":
        raise ValueError("unsupported_result_view")
    listed = task.list_post_result_files(
        service.project(project),
        identity,
        directory=directory or "",
        query=query,
        batch=batch,
        run_id=run_id,
        sample=sample,
        split=split,
        status=status,
    )
    files, errors = [], list(listed["errors"])
    for file in listed["files"][offset : offset + limit]:
        try:
            files.append(_public_file(service, project, identity, file))
        except (OSError, ValueError, KeyError) as exc:
            errors.append({"file_id": file.get("id"), "error": str(exc)})
    return {
        "items": [],
        "batches": [],
        "errors": errors,
        "total": listed["total"],
        "files": files,
    }


def public_job(value, offset=0, limit=100):
    """隐藏进程和路径，返回固定评价范围及分页行。"""
    return {
        k: v for k, v in value.items() if k not in {"inputs", "run_dir", "data_dir", "pid", "rows"}
    } | {
        "rows": value.get("rows", [])[offset : offset + limit],
        "row_count": len(value.get("rows", [])),
    }


def catalog(service, project, identity):
    """在当前任务授权下读取评价能力目录。"""
    task.get_task(service.project(project), identity)
    return {"metrics": task.metric_catalog()}


def submit(service, project, identity, body):
    """提交固定结果评价。"""
    return public_job(task.submit_post_metrics(service.project(project), identity, body))


def jobs(service, project, identity):
    """列出评价历史，无原数组或模型。"""
    return {
        "items": [
            public_job(j, limit=0)
            for j in task.list_post_metrics(service.project(project), identity)
        ]
    }


def read(service, project, identity, job, offset=0, limit=100):
    """查询指定评价和分页行。"""
    return public_job(
        task.read_post_metrics(service.project(project), identity, job), offset, limit
    )


def cancel(service, project, identity, job):
    """请求取消当前任务所属评价。"""
    return public_job(task.cancel_post_metrics(service.project(project), identity, job))


def export(service, project, identity, job, body):
    """提交导出并登记可下载的固定资产。"""
    return _file(
        service,
        project,
        identity,
        task.export_post_metrics(service.project(project), identity, job, body),
    )
