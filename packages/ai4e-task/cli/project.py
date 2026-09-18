"""项目和共享资产命令，仅调用公开 API。"""

from ..projects.project import create_project, open_project
from ..projects.shared import list_shared, register_shared


def register(commands, common) -> None:
    """注册项目及资产子命令。"""
    group = commands.add_parser("project").add_subparsers(dest="project_action", required=True)
    p = group.add_parser("new")
    p.add_argument("directory")
    p.add_argument("--name")
    p.set_defaults(action=lambda a: create_project(a.directory, name=a.name))
    p = group.add_parser("show")
    common(p)
    p.set_defaults(action=lambda a: open_project(a.project))
    datasets = group.add_parser("datasets").add_subparsers(dest="dataset_action", required=True)
    from ..projects.dataset_migration import migrate_shared_datasets
    from ..projects.datasets import bind_shared_dataset, list_shared_datasets

    p = datasets.add_parser("list")
    common(p)
    p.set_defaults(action=lambda a: list_shared_datasets(a.project))
    p = datasets.add_parser("bind")
    common(p)
    p.add_argument("task_id")
    p.add_argument("name")
    p.add_argument("--revision", required=True)
    p.set_defaults(
        action=lambda a: bind_shared_dataset(a.project, a.task_id, a.name, revision=a.revision)
    )
    p = datasets.add_parser("migrate")
    common(p)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(
        action=lambda a: migrate_shared_datasets(
            a.project, dry_run=not a.execute, overwrite=a.overwrite
        )
    )
    group = commands.add_parser("asset").add_subparsers(dest="asset_action", required=True)
    p = group.add_parser("register")
    common(p)
    p.add_argument("name")
    p.add_argument("--source", required=True)
    p.add_argument(
        "--kind", default="other", choices=["other", "dataset", "preparation", "checkpoint"]
    )
    p.add_argument("--copy", action="store_true")
    p.set_defaults(
        action=lambda a: register_shared(a.project, a.name, a.source, kind=a.kind, copy=a.copy)
    )
    p = group.add_parser("list")
    common(p)
    p.set_defaults(action=lambda a: list_shared(a.project))
