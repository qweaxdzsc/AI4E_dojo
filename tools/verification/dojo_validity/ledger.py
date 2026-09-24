"""按活动区间与供应商请求计费；允许训练和编码重叠，不编造缺失统计。"""

import math

PHASES = (
    "coding",
    "training",
    "evaluation",
    "environment_setup",
    "data_preparation",
    "idle_or_wait",
    "unclassified",
)
TOKEN_PHASES = ("coding", "training_observation", "evaluation", "environment_setup", "mixed")


def union_seconds(intervals):
    """计算半开时间区间并集，拒绝倒序或非有限时间。"""
    result, end = 0.0, None
    for start, stop in sorted(intervals):
        if not all(math.isfinite(v) for v in (start, stop)) or stop < start:
            raise ValueError("非法活动时间区间")
        result += max(0.0, stop - (start if end is None else max(start, end)))
        end = stop if end is None else max(stop, end)
    return result


def summarize_time(events, start, stop):
    """按同一单调时钟汇总活动并集、进程累计、重叠及未记账区间。"""
    wall = union_seconds([(start, stop)])
    by_phase = {phase: [] for phase in PHASES}
    ids = set()
    for event in events:
        if event["event_id"] in ids:
            raise ValueError("重复时间事件")
        ids.add(event["event_id"])
        a, b, phase = event["start"], event["end"], event["phase"]
        if phase not in by_phase or a < start or b > stop:
            raise ValueError("活动阶段或计时边界不合法")
        union_seconds([(a, b)])
        by_phase[phase].append((a, b))
    result = {f"{k}_seconds": union_seconds(v) for k, v in by_phase.items()}
    active = [
        i
        for phase, values in by_phase.items()
        if phase not in {"idle_or_wait", "unclassified"}
        for i in values
    ]
    unknown = by_phase["unclassified"]
    all_intervals = active + unknown + by_phase["idle_or_wait"]
    covered = union_seconds(all_intervals)
    # 等待区间与活动重叠的部分不能再次计费。
    result["idle_or_wait_seconds"] = covered - union_seconds(active + unknown)
    # 有阶段收据覆盖时采用具体活动；余下未知不能改称等待或编码。
    result["unclassified_seconds"] = union_seconds(active + unknown) - union_seconds(active)
    result.update(
        end_to_end_seconds=wall,
        accounted_wall_seconds=covered,
        unaccounted_seconds=wall - covered,
        overlapping_activity_seconds=sum(
            union_seconds(by_phase[p]) for p in PHASES if p not in {"idle_or_wait", "unclassified"}
        )
        - union_seconds(active),
        training_process_seconds=sum(b - a for a, b in by_phase["training"]),
        intervals=events,
    )
    return result


def summarize_usage(records):
    """对规范化供应商 usage 去重；input 包含 cache、output 包含 reasoning。"""
    requests = {}
    for item in records:
        key = item["request_id"]
        if key in requests and requests[key] != item:
            raise ValueError("同一请求的 usage 不一致")
        if item["phase"] not in TOKEN_PHASES:
            raise ValueError("未知 token 阶段")
        if item.get("input_includes_cache") is not True:
            raise ValueError("供应商 adapter 必须显式规范化缓存计数")
        if item.get("output_includes_reasoning") is not True:
            raise ValueError("供应商 adapter 必须显式规范化推理计数")
        for name in (
            "input_tokens",
            "output_tokens",
            "cache_read_tokens",
            "cache_write_tokens",
            "tool_calls",
            "retry_count",
        ):
            value = item.get(name)
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f"非法 usage: {name}")
        requests[key] = item
    rows = list(requests.values())

    def total(subset):
        if not subset or any(
            r.get("input_tokens") is None or r.get("output_tokens") is None for r in subset
        ):
            return None
        return sum(r["input_tokens"] + r["output_tokens"] for r in subset)

    result = {f"{p}_tokens": total([r for r in rows if r["phase"] == p]) for p in TOKEN_PHASES}
    for field in (
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "tool_calls",
        "retry_count",
    ):
        result[field] = (
            sum(r[field] for r in rows)
            if rows and all(r.get(field) is not None for r in rows)
            else None
        )
    result.update(
        total_accounted_tokens=total(rows),
        request_count=len(rows),
        raw_requests=rows,
        missing_usage_requests=[
            r["request_id"]
            for r in rows
            if r.get("input_tokens") is None or r.get("output_tokens") is None
        ],
    )
    return result
