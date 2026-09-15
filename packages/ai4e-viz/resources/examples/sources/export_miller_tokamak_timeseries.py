#!/usr/bin/env python3
"""Export the exact data used by the Miller tokamak promotional animation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np


DEFAULT_ROOT = Path("/Users/bill/Desktop/bootstrapNO/GK_core")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_generator(path: Path):
    spec = importlib.util.spec_from_file_location("miller_promo_video_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8)).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gk-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    generator_path = args.gk_root / "miller_promo_video.py"
    video_path = args.gk_root / "炫酷公司视频制作/回旋动理学视频.avi"
    metadata_path = (args.gk_root
                     / "miller_promo_outputs/miller_geometry_promo_white_metadata.json")
    for required in (generator_path, video_path, metadata_path):
        if not required.is_file():
            raise FileNotFoundError(required)

    generator = load_generator(generator_path)
    recorded = json.loads(metadata_path.read_text(encoding="utf-8"))
    case = recorded["solver_case"]
    render = recorded["render"]
    geometry = recorded["miller_geometry"]
    frames, fps = int(render["frames"]), int(render["fps"])
    rho = float(geometry["rho"])
    kappa = float(geometry["kappa"])
    delta = float(geometry["delta"])
    shift = float(geometry["shift"])

    theta = np.linspace(-math.pi, math.pi, 148, dtype=np.float64)
    zeta = np.linspace(0.0, 2.0 * math.pi, 176, dtype=np.float64)
    x, y, z, r_pol, theta2 = generator.miller_surface(
        theta, zeta, r_minor=rho, r_major=float(case["R0"]),
        kappa=kappa, delta=delta, shift=shift)
    _, zeta2 = np.meshgrid(theta, zeta, indexing="ij")

    frame = np.arange(frames, dtype=np.int32)
    time = frame.astype(np.float64) / float(fps)
    phase = 2.0 * math.pi * frame.astype(np.float64) / max(frames, 1)
    phi_raw = np.empty((frames, theta.size, zeta.size), dtype=np.float32)
    phi_normalized = np.empty_like(phi_raw)
    phi_scale = np.empty(frames, dtype=np.float64)
    for index in range(frames):
        value = generator.electrostatic_potential(
            theta2, zeta2, index, frames,
            q=float(case["q"]), s_hat=float(case["s_hat"]),
            gamma=float(case["gamma_ref"]), omega=float(case["omega_ref"]),
            normalize=False)
        scale = float(np.max(np.abs(value)) + 1.0e-12)
        phi_raw[index] = value.astype(np.float32)
        phi_normalized[index] = (value / scale).astype(np.float32)
        phi_scale[index] = scale

    progress = np.linspace(0.0, 1.0, frames, dtype=np.float64)
    trace_growth = 0.22 + 0.78 / (1.0 + np.exp(-8.0 * (progress - 0.36)))
    field_energy = trace_growth + 0.024 * np.sin(
        6.0 * math.pi * progress + 0.35) * (0.25 + 0.75 * trace_growth)
    field_energy = np.maximum.accumulate(field_energy - 0.012 * progress)
    field_energy /= field_energy.max() + 1.0e-12

    ky_axis = np.linspace(0.04, 0.98, 48, dtype=np.float64)
    ky_time_spectrum = np.zeros((frames, ky_axis.size), dtype=np.float64)
    for index, value in enumerate(progress):
        center = (0.30 + 0.045 * (1.0 - math.exp(-4.0 * value))
                  + 0.012 * math.sin(4.0 * math.pi * value))
        width = 0.075 + 0.055 / (1.0 + math.exp(-8.0 * (value - 0.45)))
        growth = 0.18 + 0.82 / (1.0 + math.exp(-8.0 * (value - 0.36)))
        primary = np.exp(-0.5 * ((ky_axis - center) / width) ** 2)
        shoulder_amp = 0.12 + 0.22 / (1.0 + math.exp(-9.0 * (value - 0.55)))
        shoulder = shoulder_amp * np.exp(-0.5 * ((ky_axis - 0.58) / 0.13) ** 2)
        ripple = 0.035 * (1.0 + np.sin(28.0 * ky_axis - 4.0 * value))
        ky_time_spectrum[index] = growth * (primary + shoulder + ripple)
    ky_time_spectrum /= ky_time_spectrum.max() + 1.0e-12
    ky_peak_index = np.argmax(ky_time_spectrum, axis=1)
    ky_peak = ky_axis[ky_peak_index]

    gamma_live = float(case["gamma_ref"]) * (
        0.70 + 0.38 * field_energy + 0.04 * np.sin(phase))
    omega_live = float(case["omega_ref"]) * (
        0.92 + 0.10 * np.cos(phase + 0.4))
    cfl_live = 0.58 + 0.18 * field_energy + 0.035 * np.sin(phase + 0.8)
    wphi_live = 8.0e-4 + 8.2e-3 * field_energy**1.35
    qi_live = 0.18 + 0.72 * ky_time_spectrum[frame, ky_peak_index]

    theta_cross = np.linspace(-math.pi, math.pi, 260, dtype=np.float64)
    cross_r_minus_r0 = shift + rho * np.cos(
        theta_cross + np.arcsin(delta) * np.sin(theta_cross))
    cross_z = kappa * rho * np.sin(theta_cross)
    phi_cross_normalized = np.empty((frames, theta_cross.size), dtype=np.float32)
    for index in range(frames):
        value = generator.electrostatic_potential(
            theta_cross[:, None], np.zeros((theta_cross.size, 1)),
            index, frames, q=float(case["q"]), s_hat=float(case["s_hat"]),
            gamma=float(case["gamma_ref"]), omega=float(case["omega_ref"]),
            normalize=False).ravel()
        phi_cross_normalized[index] = (value / phi_scale[index]).astype(np.float32)

    arrays = {
        "frame": frame,
        "time_R_over_vti": time,
        "phase_rad": phase,
        "theta_rad": theta,
        "zeta_rad": zeta,
        "surface_x": np.asarray(x, dtype=np.float64),
        "surface_y": np.asarray(y, dtype=np.float64),
        "surface_z": np.asarray(z, dtype=np.float64),
        "surface_R": np.asarray(r_pol, dtype=np.float64),
        "phi_surface_raw": phi_raw,
        "phi_surface_scale": phi_scale,
        "phi_surface_normalized": phi_normalized,
        "field_energy_normalized": field_energy,
        "ky_axis_normalized": ky_axis,
        "ky_time_spectrum_normalized": ky_time_spectrum,
        "ky_peak_normalized": ky_peak,
        "gamma_live": gamma_live,
        "omega_live": omega_live,
        "cfl_live": cfl_live,
        "Wphi_live": wphi_live,
        "Qi_live": qi_live,
        "theta_cross_rad": theta_cross,
        "cross_R_minus_R0": cross_r_minus_r0,
        "cross_Z": cross_z,
        "phi_cross_boundary_normalized": phi_cross_normalized,
        "camera_elevation_deg": 22.0 + 5.0 * np.sin(phase),
        "camera_azimuth_deg": 33.0 + 360.0 * frame / float(frames),
    }
    provenance = {
        "title": "Miller tokamak promotional animation time-series export",
        "frames": frames,
        "fps": fps,
        "duration_seconds": frames / fps,
        "surface_grid": [int(theta.size), int(zeta.size)],
        "solver_case": case,
        "miller_geometry": geometry,
        "source_generator": str(generator_path),
        "source_generator_sha256": sha256(generator_path),
        "source_video": str(video_path),
        "source_video_sha256": sha256(video_path),
        "source_metadata": str(metadata_path),
        "source_metadata_sha256": sha256(metadata_path),
        "scope": (
            "Exact arrays used to construct the promotional toroidal surface and "
            "dashboard. The electrostatic field is a deterministic synthetic "
            "presentation field, not a validated nonlinear gyrokinetic rollout."
        ),
        "surface_field_storage": (
            "phi_surface_raw and phi_surface_normalized are float32; all coordinate "
            "and scalar diagnostic arrays are float64."
        ),
        "array_sha256": {name: array_sha256(value) for name, value in arrays.items()},
    }
    arrays["metadata_json"] = np.asarray(
        json.dumps(provenance, ensure_ascii=False, indent=2))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output, **arrays)
    print(json.dumps({
        "output": str(args.output),
        "bytes": args.output.stat().st_size,
        "sha256": sha256(args.output),
        "frames": frames,
        "surface_grid": [int(theta.size), int(zeta.size)],
        "arrays": {name: list(value.shape) for name, value in arrays.items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
