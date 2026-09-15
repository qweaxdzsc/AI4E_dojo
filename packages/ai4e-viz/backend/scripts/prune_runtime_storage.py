"""Safely prune reproducible AI4E_Vis runtime artifacts.

Dry-run is the default. Pass ``--apply`` only after reviewing the exact list.
User uploads, fixtures, source data, environments, dependencies, SQLite state,
and report download outputs are never selected for deletion.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
PROJECT = BACKEND.parent
FRONTEND = PROJECT / "frontend"
EXPORT_ROOT = BACKEND / "state" / "report_exports"
DB_PATH = BACKEND / "state" / "ai4e_vis.sqlite3"
QUARTO_ROOT = BACKEND / ".tools" / "quarto" / "1.10.18"


@dataclass(frozen=True)
class Candidate:
    path: Path
    reason: str


def path_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file() or path.is_symlink():
        return path.lstat().st_size
    return sum(item.lstat().st_size for item in path.rglob("*") if item.is_file() or item.is_symlink())


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    amount = float(value)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _strict_export_root(export_id: str) -> Path:
    root = (EXPORT_ROOT / export_id).resolve()
    if root.parent != EXPORT_ROOT.resolve() or root.name != export_id:
        raise RuntimeError(f"Unsafe export id: {export_id}")
    return root


def export_candidates() -> list[Candidate]:
    if not DB_PATH.is_file():
        return []
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            "SELECT export_id, format, mode, status, output_path FROM report_exports ORDER BY created_at"
        ).fetchall()
    finally:
        connection.close()

    result: list[Candidate] = []
    for row in rows:
        root = _strict_export_root(row["export_id"])
        project = root / "project"
        if not project.is_dir():
            continue
        output = Path(row["output_path"]).resolve() if row["output_path"] else None
        if row["status"] != "succeeded" or output is None or not output.is_file():
            result.append(Candidate(project, f"{row['export_id']}: failed/incomplete Quarto project"))
            continue
        try:
            output.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(f"Output escapes export root: {output}") from exc

        if project not in output.parents:
            result.append(Candidate(project, f"{row['export_id']}: portable ZIP already preserved"))
            continue

        output_dir = project / "output"
        try:
            output.relative_to(output_dir.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Unexpected output layout: {output}") from exc
        for child in project.iterdir():
            if child != output_dir:
                result.append(Candidate(child, f"{row['export_id']}: reproducible Quarto source/intermediate"))
        if row["format"] == "pdf":
            for child in output_dir.iterdir():
                if child.resolve() != output:
                    result.append(Candidate(child, f"{row['export_id']}: PDF does not require HTML runtime assets"))
    return result


def cache_candidates() -> list[Candidate]:
    result = [
        Candidate(FRONTEND / "node_modules" / ".vite", "Vite dependency cache"),
        Candidate(BACKEND / "test-results", "backend test output"),
        Candidate(FRONTEND / "test-results", "frontend/E2E test output"),
    ]
    excluded = {".venv", ".tools", "node_modules", "report_exports"}
    for root, dirs, _files in os.walk(PROJECT):
        dirs[:] = [name for name in dirs if name not in excluded]
        current = Path(root)
        for name in list(dirs):
            if name == "__pycache__":
                path = current / name
                result.append(Candidate(path, "Python bytecode cache"))
                dirs.remove(name)
    return result


def quarto_candidate() -> Candidate | None:
    if platform.system() != "Darwin":
        return None
    machine = platform.machine()
    unused = "x86_64" if machine == "arm64" else "aarch64"
    path = QUARTO_ROOT / "bin" / "tools" / unused
    if not path.is_dir():
        return None
    return Candidate(path, f"unused Quarto architecture on {machine}")


def validate_candidate(candidate: Candidate) -> None:
    path = candidate.path.resolve()
    allowed_roots = [EXPORT_ROOT.resolve(), FRONTEND.resolve(), BACKEND.resolve(), PROJECT.resolve()]
    if not any(path != root and root in path.parents for root in allowed_roots):
        raise RuntimeError(f"Refusing path outside allowlist: {path}")
    protected = {
        (BACKEND / ".venv").resolve(),
        (FRONTEND / "node_modules").resolve(),
        (FRONTEND / "dist").resolve(),
        (BACKEND / "uploads").resolve(),
        (PROJECT / "resources").resolve(),
        (PROJECT / "fixtures").resolve(),
        DB_PATH.resolve(),
    }
    if path in protected:
        raise RuntimeError(f"Refusing protected path: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prune reproducible runtime storage (dry-run by default)")
    parser.add_argument("--apply", action="store_true", help="Delete the listed reproducible files")
    args = parser.parse_args()

    binary = QUARTO_ROOT / "bin" / "quarto"
    before_version = None
    quarto = quarto_candidate()
    if quarto and binary.is_file():
        before_version = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=30, check=True
        ).stdout.strip()

    candidates = export_candidates() + cache_candidates()
    if quarto:
        candidates.append(quarto)
    unique: dict[Path, Candidate] = {}
    for candidate in candidates:
        if candidate.path.exists():
            validate_candidate(candidate)
            unique[candidate.path.resolve()] = candidate
    selected = sorted(unique.values(), key=lambda item: str(item.path))
    total = sum(path_bytes(item.path) for item in selected)

    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    for item in selected:
        print(f"{human_bytes(path_bytes(item.path)):>10}  {item.path}  [{item.reason}]")
    print(f"Selected: {len(selected)} paths, reclaimable {human_bytes(total)}")

    if not args.apply:
        print("No files changed. Re-run with --apply after reviewing this list.")
        return
    for item in selected:
        _remove(item.path)
    if before_version is not None:
        after_version = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=30, check=True
        ).stdout.strip()
        if after_version != before_version:
            raise RuntimeError(f"Quarto verification failed: {before_version!r} -> {after_version!r}")
    print(f"Reclaimed approximately {human_bytes(total)}; protected source, data, uploads and outputs were retained.")


if __name__ == "__main__":
    main()
