"""正式网络和完整网格的更新/评价测速，训练目标据此冻结。"""

from __future__ import annotations

import argparse
import json
import resource
import time
from functools import partial
from pathlib import Path

import torch
import yaml

from ai4e_contrib.application.geotransolver import build_model, build_optimizer
from ai4e_core.abilities.constraint.relative_norm import relative_norm, supervised_objective
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
from ai4e_core.abilities.inference.prediction import named_array_batch
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs


def benchmark(case, preparation, device, side="dojo"):
    """包含反向和真实组合优化的一整次更新，不以局部前馈推断耗时。"""
    from ai4e_contrib.application.parametric_pde.geotransolver import binding as darcy
    from ai4e_contrib.application.spatiotemporal_pde.geotransolver import binding as bumper

    binding = darcy if case == "darcy" else bumper
    cfg = yaml.safe_load(
        (
            Path(__file__).resolve().parents[3] / "recipes/geotransolver" / case / "config.yaml"
        ).read_text()
    )
    torch.set_num_threads(4)
    torch.manual_seed(42)
    record, arrays = read_field_inputs(preparation, "train")
    if side == "reference":
        from .reference import cached_cpu_radius, load_reference, reference_optimizer

        reference = load_reference()
        cached_cpu_radius(reference)
        model = reference.GeoTransolver(**cfg["model"]).to(device)
        optimizer = reference_optimizer(
            model, lr=cfg["train"]["lr"], weight_decay=cfg["train"]["weight_decay"]
        )
    else:
        model = build_model(cfg["model"]).to(device)
        if case != "darcy":
            install_prepared_queries(
                model,
                arrays,
                radii=cfg["model"]["radii"],
                neighbors=cfg["model"]["neighbors_in_radius"],
                cache_spec={
                    "radii": record["metadata"]["declaration"]["model"]["radii"],
                    "neighbors": record["metadata"]["declaration"]["model"]["neighbors_in_radius"],
                },
            )
        optimizer = build_optimizer(
            model, lr=cfg["train"]["lr"], weight_decay=cfg["train"]["weight_decay"]
        )
    item = named_array_batch(
        arrays,
        list(range(cfg["train"]["batch_size"])),
        device=device,
        names=(*binding.INPUT_NAMES, "target", "physical_target"),
    )
    decode, target = binding.objective_binding(record["metadata"]["statistics"])
    objective = partial(
        supervised_objective,
        input_names=binding.INPUT_NAMES,
        decode=decode,
        target_name=target,
        loss=relative_norm if case == "darcy" else torch.nn.functional.mse_loss,
    )

    def sync():
        if device == "mps":
            torch.mps.synchronize()

    times = []
    for _ in range(2):
        sync()
        started = time.monotonic()
        optimizer.zero_grad()
        loss = objective(model, item)
        loss.backward()
        optimizer.step()
        sync()
        times.append(time.monotonic() - started)
    with torch.no_grad():
        sync()
        started = time.monotonic()
        value = model(**{k: item[k] for k in binding.INPUT_NAMES})
        sync()
        evaluation = time.monotonic() - started
    return {
        "case": case,
        "device": device,
        "side": side,
        "update_seconds": times,
        "evaluation_batch_seconds": evaluation,
        "parameters": sum(p.numel() for p in model.parameters()),
        "input_nodes": item["local_embedding"].shape[1],
        "batch": cfg["train"]["batch_size"],
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "mps_allocated_bytes": torch.mps.current_allocated_memory() if device == "mps" else 0,
        "loss": float(loss.detach()),
        "finite": bool(torch.isfinite(value).all()),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--case", choices=["darcy", "bumper_beam"], required=True)
    p.add_argument("--preparation", required=True)
    p.add_argument("--device", default="mps")
    p.add_argument("--side", choices=["dojo", "reference"], default="dojo")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = benchmark(a.case, a.preparation, a.device, a.side)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
