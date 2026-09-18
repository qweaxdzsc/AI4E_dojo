"""离线 recipe 文件迁移事务；只消费审阅过的逐文件替换，不识别模型。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path


def inventory(root: Path) -> dict[str, str]:
    """记录原件完整字节；拒绝链接，防止备份遗漏目录外的实际源码。"""
    if not root.is_dir():
        raise FileNotFoundError(root)
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"migration_symlink: {path}")
        if path.is_file():
            files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def _inside(root: Path, name: str) -> Path:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"migration_invalid_path: {name}")
    return root / path


def _write(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def prepare(source: Path, bundle: Path, replacements: dict[str, bytes | None]) -> dict:
    """生成可审阅替换副本、原件与清单；不修改工作目录或任何历史产物。"""
    source, bundle = source.resolve(), bundle.resolve()
    if not source.is_dir() or bundle == source or bundle.is_relative_to(source):
        raise ValueError("migration_bundle_must_be_outside_recipe")
    if bundle.exists():
        raise FileExistsError(bundle)
    before = inventory(source)
    for name in replacements:
        _inside(source, name)
    bundle.mkdir(parents=True)
    shutil.copytree(source, bundle / "original")
    shutil.copytree(source, bundle / "candidate")
    for name, payload in replacements.items():
        target = _inside(bundle / "candidate", name)
        if payload is None:
            target.unlink(missing_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    after = inventory(bundle / "candidate")
    record = {
        "version": 1, "source": str(source), "status": "prepared",
        "before": before, "after": after,
        "changes": [name for name in sorted(before.keys() | after.keys())
                    if before.get(name) != after.get(name)],
    }
    if inventory(bundle / "original") != before or inventory(source) != before:
        raise ValueError("migration_source_changed_during_prepare")
    _write(bundle / "journal.json", record)
    return record


def _paths(bundle: Path):
    record = json.loads((bundle / "journal.json").read_text())
    source = Path(record["source"])
    # 同级 rename 保证同一文件系统；路径稳定，领域清单无需重写。
    return record, source, source.with_name(".recipe-migration-old"), source.with_name(".recipe-migration-new")


def apply(bundle: Path) -> dict:
    """停止运行器后显式应用；任何内容漂移拒绝，异常保留日志供回滚。"""
    bundle = bundle.resolve()
    record, source, old, staged = _paths(bundle)
    lock = source.with_name(".recipe-migration.lock")
    with lock.open("x"):
        pass
    try:
        if record["status"] != "prepared":
            raise ValueError("migration_not_prepared")
        if old.exists() or staged.exists():
            raise ValueError("migration_recovery_required")
        if inventory(source) != record["before"]:
            raise ValueError("migration_source_changed")
        if inventory(bundle / "candidate") != record["after"]:
            raise ValueError("migration_candidate_changed")
        if inventory(bundle / "original") != record["before"]:
            raise ValueError("migration_backup_changed")
        record["status"] = "applying"
        _write(bundle / "journal.json", record)
        shutil.copytree(bundle / "candidate", staged)
        source.rename(old)
        staged.rename(source)
        record["status"] = "applied"
        _write(bundle / "journal.json", record)
        # 原件一直保留在 bundle，旧目录留到验收/回滚，避免清理故障破坏事务。
        return record
    finally:
        lock.unlink(missing_ok=True)


def rollback(bundle: Path) -> dict:
    """回滚已应用或中断的迁移；拒绝覆盖应用后用户又改过的源码。"""
    bundle = bundle.resolve()
    record, source, old, staged = _paths(bundle)
    lock = source.with_name(".recipe-migration.lock")
    with lock.open("x"):
        pass
    try:
        if record["status"] not in {"applied", "applying"}:
            raise ValueError("migration_not_applied")
        if inventory(bundle / "original") != record["before"]:
            raise ValueError("migration_backup_changed")
        if source.exists() and inventory(source) not in (record["after"], record["before"]):
            raise ValueError("migration_source_changed_after_apply")
        if old.exists() and inventory(old) != record["before"]:
            raise ValueError("migration_old_changed")
        if not old.exists():
            shutil.copytree(bundle / "original", old)
        if source.exists():
            shutil.rmtree(source)
        old.rename(source)
        if staged.exists():
            shutil.rmtree(staged)
        record["status"] = "rolled_back"
        _write(bundle / "journal.json", record)
        return record
    finally:
        lock.unlink(missing_ok=True)
