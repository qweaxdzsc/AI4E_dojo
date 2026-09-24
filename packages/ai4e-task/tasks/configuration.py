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
    project: str | Path, task_id: str, config: dict, *, revision: str,
    script_replacements: dict | None = None,
) -> dict:
    """按修订原子保存完整配置，不合并旧值或解释业务参数；返回配置和新修订。"""
    if not isinstance(config, dict):
        raise TypeError("configuration must be a mapping")
    return _save_configuration(project, task_id, config, revision, (), complete=True,
                               script_replacements=script_replacements)


def _save_configuration(project, task_id, patch, revision, replace_sections, *, complete,
                        script_replacements=None):
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
            if not isinstance(section, str) or not section.isidentifier() or section not in patch:
                raise ValueError("unsupported_configuration_replacement")
            # 被替换的旧树不得参与递归合并，连类型不兼容的旧节点也应移除。
            original.pop(section, None)
        cfg = (
            OmegaConf.create(patch)
            if complete
            else OmegaConf.merge(original, OmegaConf.create(patch))
        )
        payload = OmegaConf.to_yaml(cfg, resolve=False).encode()
        temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        originals, replacements = {}, {}
        replaced = []
        backup = None
        task_file = task_dir(project, task_id) / "task.json"
        old_task_bytes = task_file.read_bytes()
        if script_replacements:
            import shutil

            for name, item in script_replacements.items():
                target = inside(path.parent, name)
                if target.suffix != ".py":
                    raise ValueError("replacement_python_file_required")
                original_bytes = target.read_bytes()
                if hashlib.sha256(original_bytes).hexdigest() != item["revision"]:
                    raise ValueError("migration_source_changed: " + name)
                originals[name] = original_bytes
                replacements[name] = Path(item["source"]).read_bytes()
            backup = path.parent.parent / ".dojo/script-migrations" / uuid4().hex
            shutil.copytree(path.parent, backup / "original")
            write_json(backup / "receipt.json", {"status": "preparing", "files": script_replacements})
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
            if replacements:
                from ..storage.script_replacement import _replace_bytes

                for name, payload_bytes in replacements.items():
                    if (path.parent / name).read_bytes() != originals[name]:
                        raise ValueError("migration_source_changed: " + name)
                    _replace_bytes(path.parent / name, payload_bytes)
                    replaced.append(name)
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
            if backup:
                write_json(backup / "receipt.json", {"status": "applied", "files": script_replacements})
        except BaseException:
            if backup:
                from ..storage.script_replacement import _replace_bytes

                for name in reversed(replaced):
                    _replace_bytes(path.parent / name, originals[name])
                _replace_bytes(path, data)
                _replace_bytes(task_file, old_task_bytes)
                write_json(backup / "receipt.json", {"status": "rolled_back", "files": script_replacements})
            raise
        finally:
            temp.unlink(missing_ok=True)
    return {
        "revision": hashlib.sha256(payload).hexdigest(),
        "config": OmegaConf.to_container(cfg, resolve=False),
    }
