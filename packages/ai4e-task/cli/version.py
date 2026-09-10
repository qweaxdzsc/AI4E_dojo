"""血缘树及三类比较命令。"""

from ..versions.compare import compare_runs, compare_versions, compare_worktree
from ..versions.tree import get_lineage


def register(commands, common) -> None:
    """注册固定引用比较，工作目录查询不保存浮动定义。"""
    p = commands.add_parser("tree")
    common(p)
    p.add_argument("--version-id")
    p.set_defaults(action=lambda a: get_lineage(a.project, a.version_id))
    group = commands.add_parser("compare").add_subparsers(dest="compare_kind", required=True)
    for name, function in [("versions", compare_versions), ("runs", compare_runs)]:
        p = group.add_parser(name)
        common(p)
        p.add_argument("left")
        p.add_argument("right")
        p.add_argument("--save", action="store_true")
        p.set_defaults(action=lambda a, fn=function: fn(a.project, a.left, a.right, save=a.save))
    p = group.add_parser("worktree")
    common(p)
    p.add_argument("task_id")
    p.set_defaults(action=lambda a: compare_worktree(a.project, a.task_id))
