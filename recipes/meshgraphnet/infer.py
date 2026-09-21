"""从固定权重执行 MeshGraphNet rollout、评价并保存固定结果。"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from configuration import load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.inference import (
    evaluation_rollout_input,
    rollout_prediction,
)
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_model
from ai4e_core import run
from ai4e_core.abilities.data.save.bundle import (
    file_digest,
    load_bundle,
    save_bundle,
    save_json,
)
from ai4e_core.abilities.eval.trajectory import horizon_mse
from ai4e_core.abilities.training.optimization import resolve_device

HORIZONS = (1, 10, 20, 50, 100, 200)


def infer(cfg, prepared=None, trained=None):
    """恢复固定权重，执行 rollout、评价并保存逐轨迹结果。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = prepared or cfg["inputs"]["infer"].get("preparation")
    if isinstance(prepared, (str, Path)):
        declaration = json.loads(Path(prepared).read_text())
        prepared = {
            split: value["path"] if isinstance(value, dict) else value
            for split, value in declaration.get("splits", {}).items()
        }
    checkpoint = (trained or {}).get("checkpoint") or cfg["inputs"]["infer"].get("checkpoint")
    if not isinstance(prepared, dict) or "test" not in prepared:
        raise ValueError("infer 需要 trainprep 的 test 分片")
    if not checkpoint:
        raise ValueError("infer 需要固定 checkpoint")
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = build_model(cfg)
    expected = {
        "structure_version": model.structure_version,
        "hidden_dim": int(cfg["model"]["hidden_dim"]),
        "processor_layers": int(cfg["model"]["processor_layers"]),
    }
    contract = state.get("contract", {})
    if any(contract.get(key) != value for key, value in expected.items()):
        raise ValueError("推理检查点与当前 MeshGraphNet 结构不兼容")
    model.load_state_dict(state["model"], strict=True)
    device = resolve_device(cfg["infer"].get("device", "auto"))
    model.to(device).eval()
    records, metric_rows = [], []
    for sample_index, sample in enumerate(load_bundle(prepared["test"])):
        graph, target, steps = evaluation_rollout_input(sample, cfg["infer"]["steps"])
        device_graph = {
            key: value.to(device) if isinstance(value, torch.Tensor) else value
            for key, value in graph.items()
        }
        prediction = rollout_prediction(model, device_graph, steps).cpu()
        target = target.cpu()
        metrics = horizon_mse(
            prediction,
            target,
            HORIZONS,
            time_dim=0,
            includes_initial=True,
        )
        metric_rows.append(metrics)
        records.append(
            {
                "sample_id": str(sample.get("sample_id", f"test/{sample_index:06d}")),
                "prediction": prediction,
                "target": target,
                "position": graph["position"].cpu(),
                "cells": graph["cells"].cpu(),
                "node_type": graph["node_type"].cpu(),
                "metrics": metrics,
            }
        )
    if not records:
        raise ValueError("test 分片没有可推理轨迹")
    names = sorted(set.intersection(*(set(row) for row in metric_rows))) if metric_rows else []
    aggregate = {name: sum(row[name] for row in metric_rows) / len(metric_rows) for name in names}
    output = session.output_dir("infer")
    bundle = output / "results.pt"
    save_bundle(bundle, {"samples": records, "metrics": aggregate})
    metrics_path = save_json(
        output / "metrics.json",
        {
            "protocol": "DeepMind cfd_eval cumulative rollout MSE",
            "aggregate": aggregate,
            "per_sample": [
                {"sample_id": record["sample_id"], "metrics": record["metrics"]}
                for record in records
            ],
        },
    )
    manifest = save_json(
        output / "manifest.json",
        {
            "kind": "meshgraphnet-cylinder-flow-trajectory-v2",
            "bundle": str(bundle),
            "bundle_sha256": file_digest(bundle),
            "metrics": metrics_path,
            "metrics_sha256": file_digest(metrics_path),
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": file_digest(checkpoint),
            "samples": len(records),
        },
    )
    session.record_asset(
        "rollout-results",
        bundle,
        kind="other",
        stage="infer",
        dependencies=[checkpoint, prepared["test"]],
        semantics={"kind": "meshgraphnet-cylinder-flow-trajectory-v2"},
    )
    session.record_asset(
        "rollout-metrics",
        metrics_path,
        kind="other",
        stage="infer",
        dependencies=[bundle],
        semantics={"protocol": "DeepMind cfd_eval cumulative rollout MSE"},
    )
    for name, value in aggregate.items():
        session.record_metric(
            name,
            value,
            stage="infer",
            semantics={
                "field": "velocity",
                "unit": "unknown",
                "split": "test",
                "statistic": f"cumulative rollout MSE through {name.removeprefix('mse_').removesuffix('_steps')} steps",
                "data_identity": file_digest(bundle),
            },
            assets=[bundle, metrics_path],
        )
    result = {
        "manifest": manifest,
        "bundle": str(bundle),
        "metrics": metrics_path,
        "aggregate": aggregate,
    }
    session.report(result, stage="infer")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": infer}, script=__file__, only=["infer"], config_loader=load_configuration
        )
    )
