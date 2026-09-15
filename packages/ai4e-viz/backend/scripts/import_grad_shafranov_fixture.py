"""Build the portable Grad–Shafranov fixture selected for AI4E_Vis.

The source directory is intentionally an execution-time input.  The generated
manifest and report provenance contain only project-relative paths, so the
result works on CI and on another machine without the original Downloads tree.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np


MODELS = (
    "cnn_kan", "cnn_mlp", "fno_kan", "fno_mlp",
    "kan_kan", "mlp_mlp", "transformer_kan", "transformer_mlp",
)
GEOMETRIES = (
    "circular", "low_elongation", "medium_elongation", "high_elongation",
    "extreme_elongation", "negative_triangularity", "large_plasma", "small_plasma",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def copy_file(source: Path, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {
        "path": destination.as_posix(),
        "size_bytes": destination.stat().st_size,
        "sha256": digest(destination),
    }


def read_best_validation(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    val_keys = [key for key in rows[0] if "val" in key.lower() and "loss" in key.lower()]
    epoch_key = next((key for key in rows[0] if key.lower() in {"epoch", "step"}), list(rows[0])[0])
    if not val_keys:
        return {"epochs": len(rows), "best_validation_loss": None, "best_epoch": None}
    key = val_keys[0]
    pairs = []
    for row in rows:
        try:
            pairs.append((float(row[key]), int(float(row[epoch_key]))))
        except (TypeError, ValueError):
            continue
    best = min(pairs) if pairs else (None, None)
    return {"epochs": len(rows), "validation_column": key, "best_validation_loss": best[0], "best_epoch": best[1]}


def numeric_metrics(value, prefix="") -> dict[str, float]:
    found: dict[str, float] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            found.update(numeric_metrics(child, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        found[prefix] = float(value)
    return found


def choose_metric(metrics: dict[str, float], *needles: str) -> float | None:
    for key, value in metrics.items():
        normalized = key.lower()
        if all(needle in normalized for needle in needles):
            return value
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("/Users/cqy_uniforce/Downloads/multi_geometry_baseline"))
    parser.add_argument("--report", type=Path, default=Path("/Users/cqy_uniforce/Downloads/PROJECT_DOCUMENTATION(2).html"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[2] / "fixtures" / "gs")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "revision": "gs-portable-audit-v1",
        "source_note": "Portable subset: all eight training histories/summaries plus CNN-MLP eight-geometry field evidence.",
        "excluded": ["last.pt", "non-CNN-MLP per-geometry field arrays", ".DS_Store"],
        "models": {},
        "geometries": {},
        "files": [],
    }

    run_metrics = list((source / "run").glob("*/metrics.csv"))
    for model in MODELS:
        metrics_source = next((path for path in run_metrics if path.parent.name.endswith(model)), None)
        if metrics_source is None:
            raise FileNotFoundError(f"missing metrics.csv for {model}")
        summary_source = source / "tasks" / model / "comparison_summary.json"
        metrics_target = output / "models" / model / "metrics.csv"
        summary_target = output / "models" / model / "comparison_summary.json"
        for source_path, target_path in ((metrics_source, metrics_target), (summary_source, summary_target)):
            entry = copy_file(source_path, target_path)
            entry["path"] = target_path.relative_to(output).as_posix()
            manifest["files"].append(entry)
        summary = json.loads(summary_target.read_text(encoding="utf-8"))
        flat = numeric_metrics(summary)
        psi_values = [float(row["psi_l2_relative"]) for row in summary if isinstance(row, dict) and row.get("psi_l2_relative") is not None] if isinstance(summary, list) else []
        ip_values = [float(row["Ip_relative_error"]) for row in summary if isinstance(row, dict) and row.get("Ip_relative_error") is not None] if isinstance(summary, list) else []
        manifest["models"][model] = {
            **read_best_validation(metrics_target),
            "mean_psi_l2_relative": sum(psi_values) / len(psi_values) if psi_values else choose_metric(flat, "psi", "l2", "relative"),
            "mean_ip_relative_error": sum(ip_values) / len(ip_values) if ip_values else choose_metric(flat, "ip", "relative", "error"),
        }

    for geometry in GEOMETRIES:
        source_dir = source / "tasks" / "cnn_mlp" / geometry
        target_dir = output / "cases" / geometry
        case_files = {}
        for name in (
            "pino_inference.npz", "traditional_inference.npz", "pino_metrics.json",
            "comparison_metrics.json", "pino_vs_traditional_comparison.png",
        ):
            target = target_dir / name
            entry = copy_file(source_dir / name, target)
            entry["path"] = target.relative_to(output).as_posix()
            manifest["files"].append(entry)
            case_files[name] = entry
        with np.load(target_dir / "pino_inference.npz", allow_pickle=False) as fields:
            grid_shape = list(fields["psi"].shape)
            pino_current = float(np.sum(fields["j_phi"] * fields["plasma_mask"]))
        with np.load(target_dir / "traditional_inference.npz", allow_pickle=False) as fields:
            traditional_current = float(np.sum(fields["j_phi"] * fields["plasma_mask"]))
        comparison = json.loads((target_dir / "comparison_metrics.json").read_text(encoding="utf-8"))
        flat = numeric_metrics(comparison)
        manifest["geometries"][geometry] = {
            "grid_shape": grid_shape,
            "psi_l2_relative": choose_metric(flat, "psi", "l2", "relative"),
            "ip_relative_error": choose_metric(flat, "ip", "relative", "error"),
            "pino_current_sum": pino_current,
            "traditional_current_sum": traditional_current,
            "files": case_files,
        }

    report_target = output / "sources" / "PROJECT_DOCUMENTATION_2.html"
    report_entry = copy_file(args.report.resolve(), report_target)
    report_entry["path"] = report_target.relative_to(output).as_posix()
    manifest["files"].append(report_entry)
    manifest["source_report"] = report_entry

    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "files": len(manifest["files"]), "bytes": sum(item["size_bytes"] for item in manifest["files"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
