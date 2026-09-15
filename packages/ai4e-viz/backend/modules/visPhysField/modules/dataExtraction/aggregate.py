"""聚合提取方法和空值策略业务规则。"""


def validate_aggregate_method(method: str) -> str:
    """校验聚合方法并返回统一小写名称。"""

    normalized = method.strip().lower()
    if normalized not in {"min", "max", "mean", "sum", "count"}:
        raise ValueError("不支持的聚合方法")
    return normalized
