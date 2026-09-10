"""外流后处理阶段：锚点评估保存与完整网格回贴按配置并存。"""

import json
from contextlib import contextmanager, nullcontext
from functools import partial
from pathlib import Path

import torch

from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.inference.randomness import preserve_randomness, seeded_randomness
from ai4e_core.abilities.inference.rebuild import rebuild
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.model.abupt import build
from ai4e_core.applications.aero_cfd.model.objectives import objectives
from ai4e_core.applications.aero_cfd.model.protocol import describe, record_inputs
from ai4e_core.applications.aero_cfd.post.evaluation import evaluate_model
from ai4e_core.applications.aero_cfd.post.export import save_anchor_sample, save_reference_sample
from ai4e_core.applications.aero_cfd.post.mesh import query_meshes
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    iter_partition_batches,
    prepare_physical_sample,
)
from ai4e_core.applications.aero_cfd.trainprep.normalization import (
    Normalization,
    bind_normalization,
    validate_frozen,
)
from ai4e_core.base.events import sample_context
from ai4e_spec.components.model import describe_model

CHECKPOINT_TAGS = {"last", "best", "latest"}


def resolve_checkpoint(value, run_dir: Path) -> Path:
    """空值或标签落到本次运行目录；显式路径保持原样。"""
    if value in (None, "") or str(value) in CHECKPOINT_TAGS:
        tag = "last" if value in (None, "") else str(value)
        path = Path(run_dir) / "checkpoints" / f"{tag}.pt"
    else:
        path = Path(value)
    if not path.is_file():
        raise ValueError(f"post 需要可用检查点: {path}")
    return path


def restore_model(config, run, *, construct):
    """按当前配置构造模型，只恢复检查点权重。"""
    settings = config.get("train") or {}
    # 独立进程固定起始种子后沿参考全局流采样；旧独立样本流仍可显式选择。
    stream = config.get("post", {}).get("random_stream", "global")
    if stream not in {"independent", "global"}:
        raise ValueError("后处理采样流必须为 independent/global")
    config["sampling"] = {**config["sampling"], "random_stream": stream}
    requested = settings.get("device", "auto")
    device = resolve_device(requested)
    index = ManifestIndex(
        settings.get("manifest") or Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    )
    physical_prepare = partial(
        prepare_physical_sample, rules=config["trainprep"].get("physical_rules", {})
    )
    normalized_input = index.manifest["state"] == "normalized"
    normalization = (
        Normalization(index.manifest["normalization"])
        if normalized_input
        else bind_normalization(config, index.manifest)
    )
    if normalized_input and normalization.digest != index.manifest["normalization_digest"]:
        raise ValueError("归一化数据摘要冲突")
    validate_frozen(config, normalization)
    model_config = {
        **config.get("model", {}).get("parameters", {}),
        "data_specs": config["model"]["data_specs"],
    }
    model = build(construct, model_config, batch_size=int(settings.get("batch_size", 1))).to(device)
    checkpoint = resolve_checkpoint(config.get("post", {}).get("checkpoint"), run.run_dir)
    loaded = rebuild(
        checkpoint,
        model,
        contract={
            "model_version": describe_model(construct, model)["model_version"],
            "model": config.get("model", {}),
            "trainprep": config["trainprep"],
            "normalization": normalization.record,
        },
    )
    if (
        tuple(loaded["contract"].get("input_layout") or ())
        != describe_model(construct, model)["input_layout"]
    ):
        raise ValueError("推理域或字段顺序冲突")
    return {
        "model": model,
        "device": next(model.parameters()).device,
        "index": index,
        "normalization": normalization,
        "physical_prepare": physical_prepare,
        "normalized_input": normalized_input,
        "checkpoint": checkpoint,
    }


def run(config, run, *, construct, predict, prepare_inputs, collate, context_factory):
    """按开关依次做锚点评估、保存、点云和完整网格回贴。"""
    with seeded_randomness(int(config["sampling"]["seed"])):
        return _execute(
            config,
            run,
            construct=construct,
            predict=predict,
            prepare_inputs=prepare_inputs,
            collate=collate,
            context_factory=context_factory,
        )


def _execute(config, run, *, construct, predict, prepare_inputs, collate, context_factory):
    """在独立随机上下文中装配后处理，两个输出分支不相互推进采样流。"""
    settings = config.get("post") or {}
    evaluate = bool(settings.get("evaluate", True))
    save_predictions = bool(settings.get("save_predictions", True))
    export_vtk = bool(settings.get("export_vtk", True))
    query = bool(settings.get("query", True))
    if not (evaluate or save_predictions or query):
        raise ValueError("post 需要打开评估、保存或查询中的至少一路")
    progress = PostProgress(
        run, {"evaluation": evaluate, "predictions": save_predictions, "mesh": query}
    )
    report = progress.report
    try:
        if not run.dry_run:
            progress.publish()
        restored = restore_model(config, run, construct=construct)
        if run.dry_run:
            run.report(
                {"mode": "post_check", "checkpoint": str(restored["checkpoint"])}, stage="post"
            )
            return None
        report["checkpoint"] = str(restored["checkpoint"])
        training_protocol = (
            restored["checkpoint"].parent.parent / "artifacts/training-protocol.json"
        )
        original = json.loads(training_protocol.read_text()) if training_protocol.is_file() else {}
        protocol = describe(
            config,
            restored["index"],
            restored["normalization"],
            restored["model"],
            construct,
            initial=original.get("initialization"),
            entrypoint=getattr(run, "entrypoint", None),
        )
        progress.protocol = protocol
        run.artifact("comparison-protocol.json", protocol)
        if evaluate or save_predictions:
            with preserve_randomness():
                report.update(
                    _run_anchor_path(
                        config,
                        restored,
                        predict=predict,
                        prepare=prepare_inputs,
                        collate=collate,
                        evaluate=evaluate,
                        save_predictions=save_predictions,
                        export_vtk=export_vtk,
                        progress=progress,
                        protocol=protocol,
                    )
                )
        if query:
            with progress.operation("mesh"):
                report.update(
                    query_meshes(
                        config,
                        run,
                        restored,
                        prepare_inputs=prepare_inputs,
                        collate=collate,
                        context_factory=context_factory,
                        progress=progress,
                        protocol=protocol,
                    )
                )
        run.artifact("comparison-protocol.json", protocol)
        progress.finish()
        return report
    except Exception as exc:
        if not run.dry_run:
            progress.finish(exc)
        raise


def _run_anchor_path(
    config,
    restored,
    *,
    predict,
    prepare,
    collate,
    evaluate,
    save_predictions,
    export_vtk,
    progress=None,
    protocol=None,
):
    settings = config.get("train") or {}
    post = config.get("post") or {}
    split = str(post.get("split") or settings.get("evaluation_split") or "test")
    if not restored["index"].partitions.get(split):
        raise ValueError(f"后处理评估分片缺失: {split}")
    batch_size = int(settings.get("batch_size", 1))

    def batches():
        return iter_partition_batches(
            restored["index"],
            split,
            prepare=prepare,
            collate=collate,
            normalization=restored["normalization"],
            physical_prepare=restored["physical_prepare"],
            normalized_input=restored["normalized_input"],
            sampling=config["sampling"],
            config=config,
            batch_size=batch_size,
            device=restored["device"],
            evaluation=True,
        )

    report = progress.report if progress else {}
    report["split"] = split

    @contextmanager
    def evaluating(batch):
        samples = [
            {
                "sample_id": item["sample"],
                "index": restored["index"].partitions[split].index(item["sample"]),
            }
            for item in batch["metadata"]
        ]
        with progress.unit(samples) if progress else sample_context("evaluation", samples):
            if protocol is not None:
                record_inputs(protocol, "evaluation", samples, batch["inputs"])
            yield

    if evaluate:
        with progress.operation("evaluation") if progress else nullcontext():
            result = evaluate_model(
                restored["model"],
                batches(),
                predict=predict,
                objectives=objectives(config.get("model", {})),
                normalization=restored["normalization"],
                batch_context=evaluating,
            )
            result["split"] = split
            report["evaluation"] = result
    if save_predictions:
        with progress.operation("predictions") if progress else nullcontext():
            root = Path(config["paths"]["datasets"]["predictions"])
            written = []
            report["predictions"] = written
            report["export_vtk"] = export_vtk
            for batch in batches():
                _save_batch(
                    batch,
                    restored["model"],
                    restored["normalization"],
                    predict=predict,
                    root=root,
                    start_index=len(written),
                    overwrite=bool(post.get("overwrite", False)),
                    export_vtk=export_vtk,
                    progress=progress,
                    protocol=protocol,
                    written=written,
                )
    return report


def _save_batch(
    batch,
    model,
    normalization,
    *,
    predict,
    root: Path,
    overwrite: bool,
    export_vtk: bool,
    start_index: int = 0,
    progress=None,
    protocol=None,
    written=None,
):
    """对一批锚点预测做反归一化并按样本提交。"""
    samples = [
        {"sample_id": meta["sample"], "index": start_index + i}
        for i, meta in enumerate(batch["metadata"])
    ]
    if protocol is not None:
        record_inputs(protocol, "predictions", samples, batch["inputs"])
    modes = {module: module.training for module in model.modules()}
    try:
        model.eval()
        with torch.no_grad(), sample_context("predictions.forward", samples):
            predictions = predict(model, batch["inputs"])
    finally:
        for module, mode in modes.items():
            module.training = mode
    written = [] if written is None else written
    count = next(iter(predictions.values())).shape[0]
    positions = batch["inputs"]["domain_anchor_positions"]
    metadata = batch["metadata"]
    for item in range(count):
        sample_id = metadata[item]["sample"]
        with (
            progress.unit([samples[item]])
            if progress
            else sample_context("predictions.save", [samples[item]])
        ):
            payloads = {
                "surface_pressure": normalization.inverse(
                    "surface_pressure", predictions["surface_pressure"][item].detach().cpu()
                ),
                "volume_velocity": normalization.inverse(
                    "volume_velocity", predictions["volume_velocity"][item].detach().cpu()
                ),
                "surface_anchor_position": positions["surface"][item].detach().cpu(),
                "volume_anchor_position": positions["volume"][item].detach().cpu(),
            }
            dest = root / sample_id
            save_anchor_sample(
                dest,
                payloads,
                overwrite=overwrite,
                export_vtk=export_vtk,
                on_commit=progress.committed if progress else None,
            )
            packed = save_reference_sample(
                root,
                start_index + item,
                payloads,
                overwrite=overwrite,
                export_vtk=export_vtk,
                on_commit=progress.committed if progress else None,
            )
            written.append(
                {
                    "sample_id": sample_id,
                    "output": str(dest),
                    "packed": str(packed),
                    "shapes": {name: list(value.shape) for name, value in payloads.items()},
                }
            )
    return written
