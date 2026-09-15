"""可视化资产表示与导出状态的领域规则。"""

SUPPORTED_EXPORT_FORMATS = frozenset({"csv", "png", "mp4", "vtk"})


def normalize_export_format(value: str) -> str:
    """规范化导出格式并拒绝未声明的扩展名。"""

    normalized = value.strip().lower()
    if normalized not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError("unsupported_export_format")
    return normalized
