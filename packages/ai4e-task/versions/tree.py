"""正式版本血缘查询，不把运行次数挂入版本树。"""

from pathlib import Path

from ..storage.records import listing


def get_lineage(project: str | Path, version_id: str | None = None) -> list[dict]:
    """返回有序版本记录；指定版本时返回其后代子树。"""
    records = listing(project, "version")
    if version_id is None:
        return records
    if version_id not in {v["id"] for v in records}:
        raise KeyError(version_id)
    selected = {version_id}
    while True:
        more = {v["id"] for v in records if v.get("parent_version_id") in selected}
        if more <= selected:
            break
        selected |= more
    return [v for v in records if v["id"] in selected]
