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


def save_configuration(
    project: str | Path,
    task_id: str,
    patch: dict,
    *,
    revision: str,
    replace_sections: tuple[str, ...] = (),
) -> dict:
    """在项目锁内核对修订；普通编辑合并，受控 replace_sections 先移除旧段再保存。"""
    return _save_configuration(project, task_id, patch, revision, replace_sections, complete=False)


def replace_configuration(
    project: str | Path, task_id: str, config: dict, *, revision: str
) -> dict:
    """按修订原子保存完整配置，不合并旧值或解释业务参数；返回配置和新修订。"""
    if not isinstance(config, dict):
        raise TypeError("configuration must be a mapping")
    return _save_configuration(project, task_id, config, revision, (), complete=True)


def _save_configuration(project, task_id, patch, revision, replace_sections, *, complete):
    """两种保存方式共用事务、受控文件及共享资产维护。"""
    with transaction(project) as db:
        task = get(db, "task", task_id)
        if task.get("archived", False):
            raise ValueError("task_archived")
        path = _path(project, task_id)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != revision:
            raise ValueError("configuration_revision_conflict")
        original = OmegaConf.create(data.decode())
        for section in replace_sections:
            if section not in {"rawprep", "model", "train", "trainprep"} or section not in patch:
                raise ValueError("unsupported_configuration_replacement")
            # 被替换的旧树不得参与递归合并，连类型不兼容的旧节点也应移除。
            original.pop(section, None)
        if not complete and "sampling" in patch.get("model", {}):
            if "sampling" in patch.get("trainprep", {}):
                raise ValueError("model.sampling: 新旧采样声明不能同时存在")
            if "sampling" in original.get("trainprep", {}):
                del original.trainprep["sampling"]
        cfg = (
            OmegaConf.create(patch)
            if complete
            else OmegaConf.merge(original, OmegaConf.create(patch))
        )
        payload = OmegaConf.to_yaml(cfg, resolve=False).encode()
        temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            temp.write_bytes(payload)
            # 显式共享绑定同时更新当前资产；创建快照与历史运行不回写。
            from ..storage.records import all_records
            from .assets import asset_path

            incoming_cfg = OmegaConf.to_container(cfg, resolve=False)
            for item in all_records(db, "asset"):
                if not item.get("shared_dataset"):
                    continue
                key = item["consumer_binding"]
                incoming = OmegaConf.select(cfg, key)
                if incoming and Path(incoming).resolve() == asset_path(project, item).resolve():
                    if item["status"] != "available":
                        raise ValueError("shared_dataset_unavailable")
                    task.setdefault("assets", {})[key] = item
            from ai4e_core.base.config.conventions import input_bindings
            from ..storage.shared_datasets import resolve_reference

            live_keys = set(input_bindings(incoming_cfg))
            for key in live_keys:
                incoming = OmegaConf.select(cfg, key)
                if isinstance(incoming, str) and Path(incoming).is_absolute():
                    current = resolve_reference(project, Path(incoming))
                    if current is not None:
                        if current["status"] != "available":
                            raise ValueError("shared_dataset_unavailable")
                        task.setdefault("assets", {})[key] = current
            if task.get("assets"):
                task["assets"] = {
                    key: item for key, item in task["assets"].items() if key in live_keys
                }
            temp.replace(path)
            live = read_entry(path.parent)
            kept = {
                key: task.get("entry", {}).get(key)
                for key in ("platform_case",)
                if task.get("entry", {}).get(key)
            }
            task["entry"] = {**live, **kept}
            task["updated_at"] = datetime.now(UTC).isoformat()
            put(db, "task", task, replace=True)
            write_json(task_dir(project, task_id) / "task.json", task)
        finally:
            temp.unlink(missing_ok=True)
    return {
        "revision": hashlib.sha256(payload).hexdigest(),
        "config": OmegaConf.to_container(cfg, resolve=False),
    }
