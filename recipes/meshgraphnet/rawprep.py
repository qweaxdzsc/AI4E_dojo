"""读取 CylinderFlow 官方 TFRecord 或显式小样本并保存逐分片轨迹。"""

from __future__ import annotations

from pathlib import Path

import torch
from configuration import load_configuration, validate

from ai4e_contrib.application.datasets.cylinder_flow.adapter import (
    read_samples,
    read_tfrecord_split,
)
from ai4e_core import run
from ai4e_core.abilities.data.save.bundle import file_digest, save_bundle, save_json


def rawprep(cfg):
    """读取官方 TFRecord 或小样本，并固定按 split 保存的轨迹。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    declared = cfg["inputs"]["rawprep"].get("source")
    if not declared:
        raise ValueError("rawprep 需要 inputs.rawprep.source")
    source = Path(declared).resolve()
    limit = cfg["rawprep"].get("max_trajectories")
    limit = None if limit is None else int(limit)
    if source.is_dir():
        loaded = {
            split: read_tfrecord_split(source, split, limit=limit)
            for split in cfg["rawprep"]["splits"]
        }
    else:
        loaded = torch.load(source, map_location="cpu", weights_only=True)
        if not isinstance(loaded, dict):
            raise TypeError("CylinderFlow 小样本输入必须是按 split 划分的字典")
    output = session.output_dir("rawprep")
    paths, declarations = {}, {}
    for split, samples in loaded.items():
        parsed = read_samples(samples)
        if limit is not None:
            parsed = parsed[:limit]
        if not parsed:
            raise ValueError(f"CylinderFlow split {split!r} 没有样本")
        target = output / f"{split}.pt"
        save_bundle(target, parsed)
        paths[split] = str(target)
        declarations[split] = {
            "path": str(target),
            "sha256": file_digest(target),
            "samples": len(parsed),
        }
    manifest = save_json(
        output / "manifest.json",
        {
            "kind": "meshgraphnet-cylinder-flow-raw-v2",
            "source": str(source),
            "splits": declarations,
        },
    )
    session.report({"manifest": manifest, "splits": declarations}, stage="rawprep")
    return paths


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
