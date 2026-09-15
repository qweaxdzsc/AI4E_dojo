#!/usr/bin/env python3
"""Remove only reproducible files and retain the newest report exports."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DB = BACKEND / "state" / "ai4e_vis.sqlite3"
EXPORT_ROOT = BACKEND / "state" / "report_exports"
CACHE_TARGETS = (
    ROOT / ".pytest_cache",
    BACKEND / ".pytest_cache",
    BACKEND / "__pycache__",
    BACKEND / "cache",
    ROOT / "frontend" / "dist",
    ROOT / "frontend" / "test-results",
    ROOT / "frontend" / "playwright-report",
    # Dependency download/install trees stay in place; only their generated
    # bytecode and Vite pre-bundle caches are safe to rebuild on demand.
    ROOT / "frontend" / "node_modules" / ".vite",
)
VENV_ROOT = BACKEND / ".venv"


def allocated_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file() or path.is_symlink():
        return path.lstat().st_size
    return sum(item.lstat().st_size for item in path.rglob("*") if item.is_file() or item.is_symlink())


def export_prune_plan(keep: int = 1) -> list[dict]:
    if not DB.is_file():
        return []
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT * FROM report_exports ORDER BY report_id, format, mode, updated_at DESC, export_id DESC"
        ).fetchall()
    finally:
        connection.close()
    known_export_ids = {row["export_id"] for row in rows}
    seen: dict[tuple[str, str, str], int] = {}
    plan = []
    for row in rows:
        item = dict(row)
        key = (item["report_id"], item["format"], item["mode"])
        seen[key] = seen.get(key, 0) + 1
        remove = item["status"] != "succeeded" or seen[key] > keep
        if remove:
            path = EXPORT_ROOT / item["export_id"]
            plan.append({"export_id": item["export_id"], "path": str(path), "bytes": allocated_bytes(path), "reason": "old_or_failed"})
    # Isolated browser tests intentionally use a temporary database while the
    # renderer still writes into the normal generated-output directory.  Any
    # directory absent from the durable export table is unreachable from the
    # application and is therefore safe to remove as an orphaned cache.
    if EXPORT_ROOT.is_dir():
        for path in EXPORT_ROOT.iterdir():
            if path.is_dir() and path.name not in known_export_ids:
                plan.append({"export_id": path.name, "path": str(path), "bytes": allocated_bytes(path), "reason": "orphaned"})
    return plan


def run(*, apply: bool, keep_exports: int = 1) -> dict:
    cache_plan = [{"path": str(path), "bytes": allocated_bytes(path)} for path in CACHE_TARGETS if path.exists()]
    bytecode_dirs = tuple(VENV_ROOT.rglob("__pycache__")) if VENV_ROOT.exists() else ()
    bytecode_bytes = sum(allocated_bytes(path) for path in bytecode_dirs)
    if bytecode_bytes:
        cache_plan.append({"path": str(VENV_ROOT / "**" / "__pycache__"), "bytes": bytecode_bytes})
    export_plan = export_prune_plan(keep_exports)
    if apply:
        for item in cache_plan[: len(cache_plan) - (1 if bytecode_bytes else 0)]:
            path = Path(item["path"])
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=True)
        for path in bytecode_dirs:
            shutil.rmtree(path, ignore_errors=True)
        if export_plan and DB.is_file():
            with sqlite3.connect(DB) as connection:
                connection.executemany("DELETE FROM report_exports WHERE export_id=?", [(item["export_id"],) for item in export_plan])
            for item in export_plan:
                shutil.rmtree(item["path"], ignore_errors=True)
    reclaimed = sum(item["bytes"] for item in [*cache_plan, *export_plan])
    return {
        "applied": apply,
        "keep_successful_exports_per_format": keep_exports,
        "reclaimed_bytes": reclaimed,
        "reclaimed_mib": round(reclaimed / 1048576, 2),
        "cache_targets": cache_plan,
        "old_exports": export_plan,
        "preserved": ["resources/examples", "fixtures", "var/objects/datasets", "SQLite drafts/specs/artifacts", "latest successful export per format", "all renderer dependencies"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI4E_Vis safe generated-file maintenance")
    parser.add_argument("--apply", action="store_true", help="apply the displayed safe cleanup plan")
    parser.add_argument("--keep-exports", type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(run(apply=args.apply, keep_exports=max(1, args.keep_exports)), ensure_ascii=False, indent=2))
