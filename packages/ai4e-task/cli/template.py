"""模板登记及列表命令。"""

from ..templates.catalog import list_templates, register_template


def register(commands, common) -> None:
    """注册模板子命令。"""
    group = commands.add_parser("template").add_subparsers(dest="template_action", required=True)
    p = group.add_parser("register")
    common(p)
    p.add_argument("name")
    p.add_argument("--source", required=True)
    p.set_defaults(action=lambda a: register_template(a.project, a.name, a.source))
    p = group.add_parser("list")
    common(p)
    p.set_defaults(action=lambda a: list_templates(a.project))
