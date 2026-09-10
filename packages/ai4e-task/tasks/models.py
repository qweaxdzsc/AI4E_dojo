"""任务与运行的管理记录类型。"""

from typing import TypedDict


class Task(TypedDict):
    """只有 new/fork 创建正式版本，工作目录可持续编辑。"""

    id: str
    project_id: str
    version_id: str
    name: str
    created_at: str


class Run(TypedDict):
    """同一任务的一次执行，不是新的正式版本。"""

    id: str
    task_id: str
    version_id: str | None
    status: str
