"""任务配置公开操作：以内容摘要作为修订，原子保存且不创建版本。"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from omegaconf import OmegaConf

from ..storage.database import transaction
from ..storage.files import write_json
from ..storage.layout import inside, task_dir
from ..storage.records import get, put
from ..templates.materialize import read_entry


def _path(project, task_id):
    folder = task_dir(project, task_id) / "recipe"
    entry = read_entry(folder)
    if not entry:
        raise ValueError("entry_required")
    return inside(folder, entry["config"])


def read_configuration(project: str | Path, task_id: str) -> dict:
    """读取配置和文件摘要；未知插值保持原样。"""
    with transaction(project) as db:
        get(db, "task", task_id)
        data = _path(project, task_id).read_bytes()
    config = OmegaConf.to_container(OmegaConf.create(data.decode()), resolve=False)
    return {"revision": hashlib.sha256(data).hexdigest(), "config": config}


def save_configuration(project: str | Path, task_id: str, patch: dict, *, revision: str) -> dict:
    """在项目锁内核对修订并保存配置；未编辑的配置段保持。"""
    with transaction(project) as db:
        task = get(db, "task", task_id)
        if task.get("archived", False):
            raise ValueError("task_archived")
        path = _path(project, task_id)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != revision:
            raise ValueError("configuration_revision_conflict")
        original = OmegaConf.create(data.decode())
        if "sampling" in patch.get("model", {}):
            if "sampling" in patch.get("trainprep", {}):
                raise ValueError("model.sampling: 新旧采样声明不能同时存在")
            if "sampling" in original.get("trainprep", {}):
                del original.trainprep["sampling"]
        cfg = OmegaConf.merge(original, OmegaConf.create(patch))
        payload = OmegaConf.to_yaml(cfg, resolve=False).encode()
        temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            temp.write_bytes(payload)
            temp.replace(path)
            task["updated_at"] = datetime.now(UTC).isoformat()
            put(db, "task", task, replace=True)
            write_json(task_dir(project, task_id) / "task.json", task)
        finally:
            temp.unlink(missing_ok=True)
    return {
        "revision": hashlib.sha256(payload).hexdigest(),
        "config": OmegaConf.to_container(cfg, resolve=False),
    }
