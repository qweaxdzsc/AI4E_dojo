"""按显式文件清单替换任务源码；不解释算法参数，不创建研究版本。"""

from __future__ import annotations

import hashlib
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .database import transaction
from .files import write_json
from .layout import inside, task_dir
from .records import get, put


def replace_scripts(project: str | Path, task_id: str, files: dict[str, dict]) -> dict:
    """按明确文件清单与原件修订执行有备份的替换；失败恢复本次改动。"""
    if not files:
        raise ValueError("replacement_file_list_required")
    recipe = task_dir(project, task_id) / "recipe"
    backup = recipe.parent / ".dojo" / "script-migrations" / uuid4().hex
    replacements = {}
    originals = {}
    replaced: list[str] = []
    task_file = recipe.parent / "task.json"
    with transaction(project) as db:
        old_task = task_file.read_bytes()
        receipt = {"files": files, "replaced": replaced, "status": "preparing"}
        try:
            record = get(db, "task", task_id)
            if record.get("archived"):
                raise ValueError("task_archived")
            for name, item in files.items():
                target, source = inside(recipe, name), Path(item["source"])
                expected = item["revision"]
                if not target.is_file() or not source.is_file():
                    raise FileNotFoundError(name)
                originals[name] = target.read_bytes()
                if hashlib.sha256(originals[name]).hexdigest() != expected:
                    raise ValueError(f"migration_source_changed: {name}")
                replacements[name] = source.read_bytes()
            shutil.copytree(recipe, backup / "original")
            receipt["status"] = "applying"
            write_json(backup / "receipt.json", receipt)
            for name, payload in replacements.items():
                if (recipe / name).read_bytes() != originals[name]:
                    raise ValueError(f"migration_source_changed: {name}")
                _replace_bytes(recipe / name, payload)
                replaced.append(name)
            record["updated_at"] = datetime.now(UTC).isoformat()
            put(db, "task", record, replace=True)
            write_json(task_file, record)
            receipt["status"] = "applied"
            write_json(backup / "receipt.json", receipt)
        except BaseException:
            # 只恢复本次已替换的文件；用户没有参与迁移的正文不受影响。
            for name in reversed(replaced):
                _replace_bytes(recipe / name, originals[name])
            if replaced:
                _replace_bytes(task_file, old_task)
            if (backup / "receipt.json").exists():
                receipt["status"] = "rolled_back"
                write_json(backup / "receipt.json", receipt)
            raise
    return {"replaced": replaced, "backup": str(backup)}


def _replace_bytes(path: Path, payload: bytes) -> None:
    """同级临时文件原子替换，不留下半份脚本。"""
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temp.write_bytes(payload)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)
