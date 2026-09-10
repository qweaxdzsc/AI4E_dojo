"""ai4e 命令分派，Python API 是唯一业务实现。"""

import argparse
import sys

from . import project, task, template, version
from .output import render


def main(argv: list[str] | None = None) -> int:
    """返回 0 成功、1 运行失败、2 输入或业务错误。"""
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    argv = [arg for arg in argv if arg != "--json"]
    parser = argparse.ArgumentParser(prog="ai4e")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON，可放在任意子命令后")
    commands = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--project", default=".")

    for module in (project, task, version, template):
        module.register(commands, common)
    args = parser.parse_args(argv)
    try:
        value = args.action(args)
    except Exception as exc:  # noqa: BLE001 - 外部执行边界保存可查询失败
        print(
            render({"error": type(exc).__name__, "message": str(exc)}, as_json=as_json),
            file=sys.stderr,
        )
        return 2
    print(render(value, as_json=as_json))
    return 1 if isinstance(value, dict) and value.get("status") in {"failed", "stopped"} else 0
