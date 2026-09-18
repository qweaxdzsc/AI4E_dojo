"""离线迁移命令；先生成可审阅包，再显式应用或回滚。"""

import argparse
import json
from pathlib import Path

from tools.migration.recipe_conventions import transaction


def main(argv=None):
    """候选目录由研究者准备，不猜测应替换哪一套模型脚本。"""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--source", type=Path, required=True)
    prepare.add_argument("--candidate", type=Path, required=True)
    prepare.add_argument("--bundle", type=Path, required=True)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("--bundle", type=Path, required=True)
    for action in ("apply", "rollback"):
        command = commands.add_parser(action)
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--offline", action="store_true", required=True,
                             help="确认该目录的执行器已停止；此工具不停止任何服务")
    args = parser.parse_args(argv)
    if args.operation == "prepare":
        before = transaction.inventory(args.source)
        after = transaction.inventory(args.candidate)
        changes = {
            name: (args.candidate / name).read_bytes() if name in after else None
            for name in before.keys() | after.keys()
            if before.get(name) != after.get(name)
        }
        value = transaction.prepare(args.source, args.bundle, changes)
    elif args.operation == "inspect":
        value = json.loads((args.bundle / "journal.json").read_text())
        for directory, key in (("original", "before"), ("candidate", "after")):
            if transaction.inventory(args.bundle / directory) != value[key]:
                raise ValueError(f"migration_{directory}_changed")
    else:
        value = getattr(transaction, args.operation)(args.bundle)
    print(json.dumps(value, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
