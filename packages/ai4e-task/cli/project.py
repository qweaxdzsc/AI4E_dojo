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
    p.add_argument("--task-id", required=True, help="提供明确应用声明的任务")
    p.add_argument("--sources", help="共享名称到运行 ID 的 JSON 映射；多个候选须明确选择")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--overwrite", action="store_true")

    def migrate(args):
        import json

        from ..tasks.operation_sources import operation_context

        return migrate_shared_datasets(
            args.project,
            context=operation_context(args.project, args.task_id, name="inspect"),
            sources=json.loads(args.sources) if args.sources is not None else None,
            dry_run=not args.execute,
            overwrite=args.overwrite,
        )

    p.set_defaults(action=migrate)
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
