"""多维云图维度和颜色字段业务规则。"""


def validate_dimensions(dimensions: list[str], color_field: str | None = None) -> tuple[str, ...]:
    """去重并校验多维云图维度；至少需要三个维度。"""

    normalized = tuple(dict.fromkeys(item.strip() for item in dimensions if item.strip()))
    if len(normalized) < 3:
        raise ValueError("多维云图至少需要三个维度")
    if color_field and not color_field.strip():
        raise ValueError("颜色字段不能为空字符串")
    return normalized
