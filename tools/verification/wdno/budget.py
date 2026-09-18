"""复用累计监督工具；限制单原版切片，TERM/KILL 留足宽限。"""

import argparse
import json
from pathlib import Path

from tools.verification.gencp.budget import run_budgeted


def limits(used):
    """将三小时中的最后一分钟保留给终止和报告收尾。"""
    if not 0 <= used < 10740:
        raise TimeoutError("原切片累计预算已耗尽")
    return 10740, 10790


def continue_budget(ledger, command):
    """只续用已存在的累计账本；拼错路径不能隐式获得新三小时。"""
    ledger = Path(ledger)
    state = json.loads(ledger.read_text())
    soft, hard = limits(state["seconds"])
    return run_budgeted(ledger, command, soft=soft, hard=hard)


def main():
    """所有尝试共享账本；历史短测速也明确计入初始成本。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--credit-seconds", type=float, default=None)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("缺少受监督命令")
    if args.ledger.exists():
        return continue_budget(args.ledger, command)
    if args.credit_seconds is None:
        parser.error("续接必须指定已有账本；首次建账须显式给出 --credit-seconds")
    used = args.credit_seconds
    soft, hard = limits(used)
    return run_budgeted(args.ledger, command, credit_seconds=used, soft=soft, hard=hard)


if __name__ == "__main__":
    raise SystemExit(main())
