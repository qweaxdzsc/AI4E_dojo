"""二维表格分页、字段选择和抽样业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableWindow:
    """数据概览表格窗口，避免一次把完整场数据送入浏览器。"""

    offset: int = 0
    limit: int = 200


def validate_table_window(window: TableWindow) -> TableWindow:
    """校验分页范围并限制单次最多一万行。"""

    if window.offset < 0 or not 1 <= window.limit <= 10_000:
        raise ValueError("表格分页参数无效")
    return window
