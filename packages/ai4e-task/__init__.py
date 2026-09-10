"""AI4E 项目、版本和本地执行的公开 Python API；管理操作不加载训练栈。"""

from .projects.project import create_project, open_project, recover_project
from .projects.shared import get_shared, list_shared, register_shared, share_run_asset
from .tasks.create import fork_task, new_task
from .tasks.execution import resume_run, stop_run, submit_run, wait_run
from .tasks.query import get_run, get_task, import_run, list_runs, list_tasks, read_log
from .templates.catalog import list_templates, register_template
from .versions.compare import compare_runs, compare_versions, compare_worktree
from .versions.tree import get_lineage

__all__ = [
    "compare_runs",
    "compare_versions",
    "compare_worktree",
    "create_project",
    "fork_task",
    "get_lineage",
    "get_run",
    "get_shared",
    "get_task",
    "import_run",
    "list_runs",
    "list_shared",
    "list_tasks",
    "list_templates",
    "new_task",
    "open_project",
    "read_log",
    "recover_project",
    "register_shared",
    "register_template",
    "resume_run",
    "share_run_asset",
    "stop_run",
    "submit_run",
    "wait_run",
]
