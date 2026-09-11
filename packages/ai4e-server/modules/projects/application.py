"""项目位置登记和 task 项目管理。"""

from uuid import uuid4

import ai4e_task as task


def create(service, name):
    """创建真实项目并登记位置。"""
    if not name.strip():
        raise ValueError("project_name_required")
    path = service.settings.root / "projects" / uuid4().hex
    value = task.create_project(path, name=name)
    service.store.put("project", value["id"], {"id": value["id"], "path": str(path)})
    return value


def listing(service):
    """读取项目当前事实。"""
    return [task.open_project(service.project(v["id"])) for v in service.store.list("project")]
