"""正式版本登记与单父引用校验。"""

from ..storage.records import get, put


def record_version(db, value: dict) -> None:
    """仅由任务创建流程调用，父与基线必须是项目中已有版本。"""
    for key in ("parent_version_id", "baseline_version_id"):
        if value.get(key):
            get(db, "version", value[key])
    put(db, "version", value)
