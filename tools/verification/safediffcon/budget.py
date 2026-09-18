"""SafeDiffCon 持续账本的阶段限时：给最终响应评价保留余额。"""

import argparse
import json
import math
from pathlib import Path

from tools.verification.gencp.budget import run_budgeted


def phase_limits(ledger: Path, *, seconds: float, reserve: float) -> tuple[float, float]:
    """从已有账本取余额；单阶段不能侵占预留或重建历史账本。"""
    if not ledger.is_file():
        raise ValueError("继续执行必须提供已有累计账本")
    state = json.loads(ledger.read_text())
    used = state["seconds"]
    if (
        not all(math.isfinite(x) for x in (used, seconds, reserve))
        or min(used, reserve) < 0
        or seconds <= 5
    ):
        raise ValueError("阶段预算非法")
    if any(r["status"] == "running" for r in state["runs"]):
        raise RuntimeError("存在未收尾计算")
    hard = min(10800 - reserve, used + seconds)
    soft = min(10500, hard - 5)
    if soft <= used:
        raise TimeoutError("余额不足以保留最终评价")
    return soft, hard


def main():
    """监督整个子进程组；失败和中断仍记入原账本。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--reserve", type=float, default=0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("缺少计算命令")
    soft, hard = phase_limits(args.ledger, seconds=args.seconds, reserve=args.reserve)
    return run_budgeted(args.ledger, command, soft=soft, hard=hard)


def training_forecast(
    *, start: int, total: int, seconds_per_update: float, post_seconds: float, training_limit: float
) -> dict:
    """双侧剩余更新加后训练开销乘1.25，拒绝把总目标误作增量。"""
    if type(start) is not int or type(total) is not int or not 0 <= start < total <= 20000:
        raise ValueError("总更新目标与恢复位置非法")
    if not all(
        math.isfinite(x) and x > 0 for x in (seconds_per_update, post_seconds, training_limit)
    ):
        raise ValueError("耗时测量必须是正有限值")
    expected = 2 * (total - start) * seconds_per_update + post_seconds
    guarded = 1.25 * expected
    if guarded > training_limit:
        raise TimeoutError("双侧训练预估超出阶段分配")
    return {
        "start": start,
        "total": total,
        "additional_per_side": total - start,
        "seconds_per_update": seconds_per_update,
        "post_seconds_both_sides": post_seconds,
        "expected_seconds": expected,
        "guarded_seconds": guarded,
        "training_limit_seconds": training_limit,
    }


if __name__ == "__main__":
    raise SystemExit(main())
