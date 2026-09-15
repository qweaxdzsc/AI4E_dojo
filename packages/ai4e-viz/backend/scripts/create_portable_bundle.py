#!/usr/bin/env python3
"""Create a portable source + business-data bundle without machine-specific dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "var" / "db" / "ai4e_vis.sqlite3"
EXCLUDED_PARTS = {
    ".DS_Store", ".git", ".pytest_cache", "__pycache__", ".venv", ".tools", "node_modules",
    "dist", "test-results", "playwright-report", "report_exports", "runtime",
    "backups", "derived", "exports", "logs", "telemetry", "tmp", "quarantine",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_exclude(path: Path) -> bool:
    if path == ROOT / "portable-manifest.json":
        return True
    relative = path.relative_to(ROOT)
    return bool(set(relative.parts) & EXCLUDED_PARTS) or path.suffix in EXCLUDED_SUFFIXES or path.name.endswith(("-wal", "-shm"))


def source_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not path.is_symlink() and not should_exclude(path) and path.resolve() != DB.resolve():
            yield path


def check() -> dict:
    files = list(source_files())
    size = sum(path.stat().st_size for path in files) + (DB.stat().st_size if DB.is_file() else 0)
    forbidden = [str(path.relative_to(ROOT)) for path in files if set(path.relative_to(ROOT).parts) & {".venv", ".tools", "node_modules", "report_exports"}]
    return {
        "ok": not forbidden,
        "files": len(files) + (1 if DB.is_file() else 0),
        "source_and_business_data_bytes": size,
        "source_and_business_data_mib": round(size / 1048576, 2),
        "forbidden": forbidden,
        "reinstall": ["Python dependencies from backend/requirements.txt", "npm dependencies from frontend/package-lock.json", "Quarto 1.10.18 via backend/scripts/install_quarto.py"],
    }


def create(output: Path) -> dict:
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("PORTABLE_OUTPUT_MUST_BE_OUTSIDE_PROJECT_ROOT")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"created_at": datetime.now(timezone.utc).isoformat(), "root": "AI4E_Vis", "files": []}
    with tempfile.TemporaryDirectory(prefix="qoder-portable-") as temporary:
        db_snapshot = Path(temporary) / "ai4e_vis.sqlite3"
        if DB.is_file():
            source = sqlite3.connect(DB)
            target = sqlite3.connect(db_snapshot)
            try:
                source.backup(target)
                # report_exports are generated cache entries whose output
                # directories are intentionally excluded from the portable
                # source bundle.  Do not leave successful-looking rows that
                # point to files absent on the destination machine.
                target.execute("DELETE FROM report_exports")
                target.commit()
            finally:
                target.close()
                source.close()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
            for path in source_files():
                relative = path.relative_to(ROOT)
                data = path.read_bytes()
                bundle.writestr(str(Path("AI4E_Vis") / relative), data)
                manifest["files"].append({"path": str(relative), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            if db_snapshot.is_file():
                data = db_snapshot.read_bytes()
                relative = Path("var/db/ai4e_vis.sqlite3")
                bundle.writestr(str(Path("AI4E_Vis") / relative), data)
                manifest["files"].append({"path": str(relative), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
            bundle.writestr("AI4E_Vis/portable-manifest.json", manifest_bytes)
    return {**check(), "output": str(output), "archive_bytes": output.stat().st_size, "manifest_entries": len(manifest["files"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a portable AI4E_Vis ZIP")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        result = check()
    elif args.output:
        result = create(args.output)
    else:
        parser.error("use --check-only or --output /path/AI4E_Vis-portable.zip")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
