"""资源 CLI；仅调用 templates.resources 的无模型门面。"""

from ..templates.resources import (
    check_example,
    copy_example,
    create_smoke_data,
    describe_help_symbol,
    export_guide,
    guide_info,
    list_examples,
    read_help_topic,
    search_help,
    source_location,
)


def register(commands, common) -> None:
    """注册 guide/source/example 便利命令。"""
    guide = commands.add_parser("guide")
    guide.set_defaults(action=lambda _: guide_info())
    export = guide.add_subparsers(dest="guide_action")
    p = export.add_parser("export")
    p.add_argument("--to", required=True)
    p.set_defaults(action=lambda a: export_guide(a.to))
    p = export.add_parser("search")
    p.add_argument("query")
    p.add_argument("--kind")
    p.add_argument("--layer")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(
        action=lambda a: search_help(
            a.query,
            kind=a.kind,
            layer=a.layer,
            limit=a.limit,
        )
    )
    p = export.add_parser("topic")
    p.add_argument("topic_id")
    p.set_defaults(action=lambda a: read_help_topic(a.topic_id))
    p = export.add_parser("symbol")
    p.add_argument("symbol")
    p.set_defaults(action=lambda a: describe_help_symbol(a.symbol))

    p = commands.add_parser("source")
    p.add_argument("module")
    p.set_defaults(action=lambda a: source_location(a.module))

    group = commands.add_parser("example").add_subparsers(dest="example_action", required=True)
    p = group.add_parser("list")
    p.set_defaults(action=lambda _: list_examples())
    p = group.add_parser("check")
    p.add_argument("case_id")
    p.set_defaults(action=lambda a: check_example(a.case_id))
    p = group.add_parser("copy")
    p.add_argument("case_id")
    p.add_argument("--to", required=True)
    p.set_defaults(action=lambda a: copy_example(a.case_id, a.to))
    smoke = group.add_parser("smoke-data").add_subparsers(dest="smoke_action", required=True)
    p = smoke.add_parser("create")
    p.add_argument("--to", required=True)
    p.set_defaults(action=lambda a: create_smoke_data(a.to))
