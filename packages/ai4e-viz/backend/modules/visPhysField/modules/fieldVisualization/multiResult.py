"""多结果导入、多窗口、统一视角和显隐业务规则。"""


def unique_result_ids(result_ids: list[str]) -> tuple[str, ...]:
    """保留导入顺序并去除重复结果，供多窗口布局和统一视角使用。"""

    normalized = tuple(dict.fromkeys(item.strip() for item in result_ids if item.strip()))
    if not normalized:
        raise ValueError("至少需要一个结果")
    return normalized
