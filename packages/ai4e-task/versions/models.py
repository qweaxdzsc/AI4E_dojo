"""正式版本、来源与差异的轻量类型。"""

from typing import TypedDict


class Version(TypedDict):
    """完整创建快照加单父血缘，基线与父版本独立。"""

    id: str
    task_id: str
    parent_version_id: str | None
    baseline_version_id: str | None
    snapshot: dict
    source_snapshot: dict
