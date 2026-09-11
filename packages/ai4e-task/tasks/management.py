"""编辑任务研究信息；版本记录和运行快照保持不变。"""

from datetime import UTC, datetime
from pathlib import Path

from ..storage.database import transaction
from ..storage.files import write_json
from ..storage.layout import task_dir
from ..storage.records import get, put


def update_task(
    project: str | Path,
    task_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    archived: bool | None = None,
) -> dict:
    """更新任务的管理记录；归档可恢复，不删除资产。"""
    if name is not None and not name.strip():
        raise ValueError("task_name_required")
    with transaction(project) as db:
        value = get(db, "task", task_id)
        for key, item in {"name": name, "description": description, "archived": archived}.items():
            if item is not None:
                value[key] = item
        value["updated_at"] = datetime.now(UTC).isoformat()
        put(db, "task", value, replace=True)
        write_json(task_dir(project, task_id) / "task.json", value)
    return value
