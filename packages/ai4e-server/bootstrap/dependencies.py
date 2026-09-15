"""只通过任务包公开 API 定位研究对象。"""

from pathlib import Path

import ai4e_task as task

from ..infrastructure.persistence import Store


class Services:
    """请求共享的装配对象；不拥有 task 领域记录。"""

    def __init__(self, settings):
        self.settings = settings
        from ..infrastructure.vis_client import VisClient
        self.vis = VisClient(settings)
        self.vis_sessions = {}
        self.vis_contexts = {}
        self.store = Store(settings.root)
        from ..modules.visualization.application import recover_operations

        recover_operations(self)

    def project(self, identity):
        """按服务位置索引打开 task 项目。"""
        path = Path(self.store.get("project", identity)["path"])
        if task.open_project(path)["id"] != identity:
            raise ValueError("project_identity_changed")
        return path


def services(request):
    """取得已装配的服务对象。"""
    return request.app.state.services
