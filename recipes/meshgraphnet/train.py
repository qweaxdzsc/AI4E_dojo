"""MeshGraphNet 训练阶段；显式展开轨迹取帧、收批、更新和恢复。"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from configuration import load_configuration, validate

from ai4e_contrib.application.datasets.cylinder_flow.adapter import training_frame
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_model
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.training import objective
from ai4e_core import run
from ai4e_core.abilities.data.save.bundle import file_digest, load_bundle
from ai4e_core.abilities.training.checkpoint import capture, restore
from ai4e_core.abilities.training.graph_batch import concatenate_graphs
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.optimization import resolve_device


def _catalog(samples):
    entries = []
    for sample_index, sample in enumerate(samples):
        velocity = sample["velocity"]
        if velocity.ndim == 3:
            entries.extend((sample_index, frame) for frame in range(1, velocity.shape[0] - 1))
        elif velocity.ndim == 2:
            entries.append((sample_index, None))
        else:
            raise ValueError("训练 velocity 必须是物理帧或完整轨迹")
    if not entries:
        raise ValueError("训练分片没有可用时间步")
    return entries


def _frame(samples, entry):
    sample_index, frame_index = entry
    sample = samples[sample_index]
    return training_frame(sample, frame_index) if frame_index is not None else sample


def _contract(cfg, model, prepared, catalog):
    return {
        "kind": "meshgraphnet-cylinder-flow-train-v2",
        "structure_version": model.structure_version,
        "hidden_dim": int(cfg["model"]["hidden_dim"]),
        "processor_layers": int(cfg["model"]["processor_layers"]),
        "batch_size": int(cfg["train"]["batch_size"]),
        "noise_std": float(cfg["train"]["noise_std"]),
        "normalizer_warmup": int(cfg["train"]["normalizer_warmup"]),
        "lr": float(cfg["train"]["lr"]),
        "lr_decay_steps": int(cfg["train"]["lr_decay_steps"]),
        "lr_decay_rate": float(cfg["train"]["lr_decay_rate"]),
        "lr_floor": float(cfg["train"]["lr_floor"]),
        "seed": int(cfg.get("seed", 0)),
        "train_data_sha256": file_digest(prepared["train"]),
        "training_frames": len(catalog),
    }


def _learning_rate(cfg, update):
    settings = cfg["train"]
    return float(settings["lr"]) * float(settings["lr_decay_rate"]) ** (
        update / int(settings["lr_decay_steps"])
    ) + float(settings["lr_floor"])


def train(cfg, prepared=None):
    """按配置执行更新、恢复并保存固定命名空间检查点。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    prepared = prepared or cfg["inputs"]["train"]["preparation"]
    if isinstance(prepared, (str, Path)):
        declaration = json.loads(Path(prepared).read_text())
        prepared = {
            split: value["path"] if isinstance(value, dict) else value
            for split, value in declaration.get("splits", {}).items()
        }
    if not isinstance(prepared, dict) or "train" not in prepared:
        raise ValueError("train 需要 trainprep 的 train 分片")
    samples = load_bundle(prepared["train"])
    catalog = _catalog(samples)
    torch.manual_seed(int(cfg.get("seed", 0)))
    model = build_model(cfg)
    device = resolve_device(cfg["train"].get("device", "auto"))
    model.to(device).train()
    optimizer = torch.optim.Adam(model.parameters(), lr=_learning_rate(cfg, 0))
    contract = _contract(cfg, model, prepared, catalog)
    target_updates = int(cfg["train"]["updates"])
    stream = IterationStream(
        len(catalog), int(cfg["train"]["batch_size"]), seed=int(cfg.get("seed", 0))
    )
    losses, start = [], 0
    resume = cfg["inputs"]["train"].get("resume")
    if resume:
        state = restore(resume, model, optimizer, contract=contract)
        losses = list(state.get("losses", []))
        start = int(state["updates"])
        if "stream" not in state:
            raise ValueError("恢复检查点缺少图帧流状态")
        stream.load_state_dict(state["stream"])
        if target_updates <= start:
            raise ValueError("训练总目标必须大于恢复进度")
    warmup = int(cfg["train"]["normalizer_warmup"])
    for update in range(start, target_updates):
        selection = stream.next().tolist()
        frames = [_frame(samples, catalog[index]) for index in selection]
        graph = concatenate_graphs(frames)
        graph = {
            key: value.to(device)
            for key, value in graph.items()
            if key in {"node_features", "edge_features", "edge_index"}
        }
        current = torch.cat([item["velocity"] for item in frames]).to(device)
        target_velocity = torch.cat(
            [item.get("target_velocity", item["velocity"]) for item in frames]
        ).to(device)
        target = target_velocity - current
        node_type = torch.cat([item["node_type"] for item in frames]).to(device)
        loss_mask = (node_type == 0) | (node_type == 5)
        noise_mask = node_type == 0
        for group in optimizer.param_groups:
            group["lr"] = _learning_rate(cfg, update)
        optimizer.zero_grad(set_to_none=True)
        loss = objective(
            model,
            graph,
            target,
            loss_mask,
            noise_std=float(cfg["train"]["noise_std"]),
            noise_mask=noise_mask,
            accumulate_normalizers=True,
        )
        if update >= warmup:
            loss.backward()
            optimizer.step()
        losses.append(float(loss.detach().cpu()))
    state = capture(
        model,
        optimizer,
        epoch=0,
        updates=target_updates,
        best=min(losses[warmup:] or losses),
        contract=contract,
    )
    state.update(
        losses=losses,
        learning_rate=_learning_rate(cfg, target_updates - 1),
        stream=stream.state_dict(),
    )
    checkpoint = session.checkpoint(
        "last",
        state,
        namespace=f"step-{target_updates:08d}",
    )
    result = {
        "status": "complete",
        "updates": target_updates,
        "optimized_updates": max(target_updates - warmup, 0),
        "losses": losses,
        "checkpoint": str(checkpoint),
        "contract": contract,
    }
    session.report(result, stage="train")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"train": train}, script=__file__, only=["train"], config_loader=load_configuration
        )
    )
