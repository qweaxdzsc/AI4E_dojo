"""外流分块查询业务；贡献模型通过上下文构造器注入，不再作为案例默认产物。"""

from copy import deepcopy
from functools import partial
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.abilities.inference.query import query_model
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization


def query_prepared(config, run, model, *, prepare_inputs, collate, context_factory):
    """对一个探测样本做全分辨率查询并写入独立查询目录。"""
    prepared_config = deepcopy(config)
    prepared_config["train"]["mode"] = "prepare"
    prepare = partial(
        prepare_inputs,
        data_specs=prepared_config["model"]["data_specs"],
        bindings=prepared_config["trainprep"],
    )
    prepared = probe(prepared_config, prepare=prepare, dry_run=run.dry_run)
    if run.dry_run:
        return {"sample_id": prepared["sample_id"]}
    batch = collate([prepared["sampled"]])["inputs"]
    batch.pop("domain_query_positions", None)
    batch.pop("domain_query_features", None)
    positions = {
        d: prepared["normalized"][binding["position"]][None]
        for d, binding in config["trainprep"]["domains"].items()
    }
    features = {}
    for d, spec in config["model"]["data_specs"]["domains"].items():
        names = list((spec.get("feature_dim") or {}).keys())
        if names and config["trainprep"].get("use_physics_features", True):
            features[d] = torch.cat(
                [
                    prepared["normalized"][config["trainprep"]["domains"][d]["features"][n]]
                    for n in names
                ],
                dim=-1,
            )[None]
    device = next(model.parameters()).device
    result = query_model(
        model,
        to_device(batch, device),
        to_device(positions, device),
        context_factory=context_factory,
        features=to_device(features, device) or None,
        preparation_id=prepared["normalization_path"] + ":" + prepared["sample_id"],
        chunk_size=int(config["post"]["query_chunk_size"]),
    )
    norm = Normalization(prepared["normalization"])
    mapping = config["post"].get("denormalization") or {
        "query_" + term["prediction"]: term["normalization"]
        for term in config["model"]["supervision"]
        if not term["prediction"].startswith("query_")
    }
    output = {name: norm.inverse(field, result[name]).squeeze(0) for name, field in mapping.items()}
    target = Path(config["paths"]["datasets"]["predictions"]) / "query" / prepared["sample_id"]
    write_named_tensors(
        target,
        output,
        {name: name + ".pt" for name in output},
        overwrite=config["post"].get("overwrite", False),
    )
    return {
        "sample_id": prepared["sample_id"],
        "output": str(target),
        "shapes": {k: list(v.shape) for k, v in output.items()},
    }


def infer(config, run, *, construct, prepare_inputs, collate, context_factory):
    """兼容入口：只跑完整网格回贴，检查点由阶段装配恢复。"""
    from ai4e_core.applications.aero_cfd.post.mesh import query_meshes
    from ai4e_core.applications.aero_cfd.post.stage import restore_model

    restored = restore_model(config, run, construct=construct)
    if run.dry_run:
        run.report({"mode": "post_check", "checkpoint": str(restored["checkpoint"])}, stage="post")
        return None
    report = {
        "mode": "post",
        **query_meshes(
            config,
            run,
            restored,
            prepare_inputs=prepare_inputs,
            collate=collate,
            context_factory=context_factory,
        ),
    }
    run.report(report, stage="post")
    return report
