"""锚点推理步骤：原数值路径与完整网格回贴，运行会话由调用方提供。"""

import json
from contextlib import contextmanager, nullcontext
from functools import partial
from pathlib import Path

import torch

from ai4e_core.abilities.data.source.manifest import ManifestIndex
from ai4e_core.abilities.inference.randomness import preserve_randomness, seeded_randomness
from ai4e_core.abilities.inference.rebuild import rebuild
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.applications.aero_cfd.infer.anchor_evaluation import evaluate_model
from ai4e_core.applications.aero_cfd.infer.anchor_export import (
    save_anchor_sample,
    save_reference_sample,
)
from ai4e_core.applications.aero_cfd.infer.mesh import query_meshes
from ai4e_core.applications.aero_cfd.infer.vtk_export import record_vtk_status
from ai4e_core.applications.aero_cfd.model.abupt import build
from ai4e_core.applications.aero_cfd.model.objectives import objectives
from ai4e_core.applications.aero_cfd.model.protocol import describe, record_inputs
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    iter_partition_batches,
    prepare_physical_sample,
)
from ai4e_core.applications.aero_cfd.trainprep.normalization import (
    Normalization,
    bind_normalization,
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


def restore_model(config, run, *, construct, prepared=None):
    """按当前配置构造模型，只恢复检查点权重。"""
    settings = config.get("train") or {}
    # 独立进程固定起始种子后沿参考全局流采样；旧独立样本流仍可显式选择。
    stream = config.get("post", {}).get("random_stream", "global")
    if stream not in {"independent", "global"}:
        raise ValueError("后处理采样流必须为 independent/global")
    config["sampling"] = {**config["sampling"], "random_stream": stream}
    requested = settings.get("device", "auto")
    device = resolve_device(requested)
    index = prepared.index if prepared is not None else ManifestIndex(
        settings.get("manifest") or Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    )
    physical_prepare = prepared.physical_prepare if prepared is not None else partial(
        prepare_physical_sample, rules=config["trainprep"].get("physical_rules", {})
    )
    normalized_input = index.manifest["state"] == "normalized"
    normalization = prepared.normalization if prepared is not None else (
        Normalization(index.manifest["normalization"])
        if normalized_input
        else bind_normalization(config, index.manifest)
    )
    if normalized_input and normalization.digest != index.manifest["normalization_digest"]:
        raise ValueError("归一化数据摘要冲突")
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
    """历史入口使用与新 recipe 相同的公开步骤。"""
    from types import SimpleNamespace

    component = SimpleNamespace(
        construct=construct,
        predict=predict,
        prepare_inputs=prepare_inputs,
        collate=collate,
        InferenceContext=context_factory,
    )
    job = open_post(config, model_component=component, session=run)
    job = configure_restore(job)
    job = configure_prediction(job)
    job = configure_physical_output(job)
    job = configure_evaluation(job)
    job = configure_save(job, output=config["paths"]["datasets"]["predictions"])
    job = configure_mesh_export(job)
    return execute(job)


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
    evaluator=None,
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

    if config.get("infer", {}).get("fields") or config.get("infer", {}).get("metrics"):
        from ai4e_core.applications.aero_cfd.infer.anchor import run_selected_batches

        with progress.operation("predictions" if save_predictions else "evaluation"):
            return run_selected_batches(
                config,
                restored,
                batches(),
                predict=predict,
                progress=progress,
                protocol=report["inference_protocol"],
            )

    if evaluate:
        with progress.operation("evaluation") if progress else nullcontext():
            result = (evaluator or evaluate_model)(
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


# 以下为新 recipe 的公开装配；兼容 run 也使用相同执行路径。
from copy import deepcopy
from dataclasses import dataclass, field

from ai4e_core.base.config import operation_record, plain, resolve_operation


@dataclass
class AnchorPost:
    """锚点后处理装配，保持评价/保存随机流与完整网格流隔离。"""

    config: dict
    component: object
    session: object
    steps: list = field(default_factory=list)
    predict: object = None
    metric: object = None
    extensions: dict = field(default_factory=dict)
    restored: dict | None = None
    physical: bool = False
    restore: bool = False


def open_post(config, *, model_component, session, dataset_component=None, trained=None):
    """打开后处理配置与训练交付，不执行模型恢复。"""
    config = deepcopy(config)
    if trained is not None:
        if "checkpoints" not in trained:
            raise ValueError("训练检查报告不是检查点产物")
        value = config["post"].get("checkpoint")
        if value in (None, "last", "latest", "best"):
            config["post"]["checkpoint"] = trained["checkpoints"][value or "last"]
    job = AnchorPost(config, model_component, session)
    job.dataset_component = dataset_component
    return job


def configure_restore(job, *, settings=None):
    """登记权重与冻结变换恢复。"""
    if job.restore:
        raise ValueError("恢复步骤重复")
    job.restore = True
    return job


def configure_prediction(job, *, settings=None, operation=None):
    """配置 model/inputs → 归一化预测映射，供评价和保存共同使用。"""
    if not job.restore or job.physical:
        raise ValueError("预测必须在恢复之后、物理输出之前登记")
    spec = plain(settings or job.config["post"]).get("prediction", {})
    job.predict = resolve_operation(spec, default=job.component.predict, operation=operation)
    if operation is not None or spec.get("target"):
        job.extensions["prediction"] = operation_record(job.predict)
    return job


def configure_physical_output(job):
    """声明按冻结变换恢复物理输出；具体数组变换在逐批保存中执行。"""
    if not job.restore or job.predict is None or job.physical:
        raise ValueError("物理输出必须在预测之后且只登记一次")
    job.physical = True
    return job


def configure_evaluation(job, *, settings=None, operation=None):
    """登记评价分支；与保存分支共用预测函数但保留原两次遍历。"""
    if not job.physical:
        raise ValueError("评价需要物理输出声明")
    settings = plain(settings or job.config["post"])
    if settings.get("evaluate", True):
        spec = settings.get("metric", {})
        job.metric = resolve_operation(spec, default=evaluate_model, operation=operation)
        if operation is not None or spec.get("target"):
            job.extensions["metric"] = operation_record(job.metric)
        job.steps.append("evaluation")
    return job


def configure_save(job, *, output, settings=None):
    """登记锚点张量和可选点云保存。"""
    if not job.physical:
        raise ValueError("保存需要物理输出声明")
    settings = plain(settings or job.config["post"])
    job.config["paths"]["datasets"]["predictions"] = str(output)
    if settings.get("save_predictions", True):
        job.steps.append("predictions")
    return job


def configure_mesh_export(job, *, settings=None):
    """登记独立完整网格查询，保留模型专用缓存策略。"""
    settings = plain(settings or job.config["post"])
    if settings.get("query", True) or settings.get("export_mesh"):
        job.steps.append("mesh")
    return job


def _export_full_meshes(job, config, session, restored, *, prepare, collate, progress, protocol):
    """有原始 VTK 时查询回贴；只有连接关系时用数据集 comparison_mesh。"""
    from ai4e_core.applications.aero_cfd.infer.vtk_capability import describe_vtk_exports
    from ai4e_core.applications.aero_cfd.post.mesh_export import export_prediction_meshes

    capability = getattr(job, "vtk_exports", None) or describe_vtk_exports(
        config, dataset_component=getattr(job, "dataset_component", None)
    )
    sources = (capability.get("mesh") or {}).get("sources") or []
    if "source_vtk" in sources:
        return query_meshes(
            config,
            session,
            restored,
            prepare_inputs=prepare,
            collate=collate,
            context_factory=job.component.InferenceContext,
            progress=progress,
            protocol=protocol,
        )
    dataset = getattr(job, "dataset_component", None)
    if dataset is None or not callable(getattr(dataset, "comparison_mesh", None)):
        raise FileNotFoundError("训练集没有可还原的 VTK 网格")
    written = []
    for item in progress.report.get("predictions") or progress.report.get("results") or []:
        manifest = item.get("manifest")
        if not manifest:
            continue
        meshes = export_prediction_meshes(
            config, dataset, manifest, committed=progress.committed
        )
        written.append(
            {
                "sample_id": item.get("sample_id", item.get("sample")),
                "kind": "full_source_mesh",
                "fields": {
                    domain: record.get("fields", []) for domain, record in meshes.items()
                },
                **{
                    domain: str(Path(manifest).parent / record["path"])
                    for domain, record in meshes.items()
                },
                "points": {
                    domain: record.get("point_count") for domain, record in meshes.items()
                },
            }
        )
    return {"meshes": written}


def check_report(job):
    """检查引用和声明，不构建网络或发布成功产物。"""
    if not job.restore or not job.physical or not job.steps:
        raise ValueError("后处理必须配置恢复、物理输出和至少一种交付")
    checkpoint = resolve_checkpoint(job.config["post"].get("checkpoint"), job.session.run_dir)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    for key in ("model", "trainprep"):
        if state["contract"].get(key) != job.config[key]:
            raise ValueError(f"检查点 {key} 声明冲突")
    result = {
        "mode": "infer_check" if job.config.get("infer") else "post_check",
        "checkpoint": str(checkpoint),
    }
    job.session.report(result, stage="infer" if job.config.get("infer") else "post")
    return result


def execute(job):
    """严格按已登记分支顺序执行，未登记分支不执行。"""
    if job.session.dry_run:
        return check_report(job)
    if (
        not job.restore
        or not job.physical
        or not job.steps
        or len(set(job.steps)) != len(job.steps)
    ):
        raise ValueError("后处理步骤缺失或重复")
    config, session, component = job.config, job.session, job.component
    progress = PostProgress(
        session,
        {name: name in job.steps for name in ("evaluation", "predictions", "mesh")},
        phase="infer" if config.get("infer") else "post",
    )
    report = progress.report
    try:
        with seeded_randomness(int(config["sampling"]["seed"])):
            progress.publish()
            from time import perf_counter

            restore_started = perf_counter()
            prepare = resolve_operation(config["sampling"], default=component.prepare_inputs)
            collate = component.collate
            checkpoint = resolve_checkpoint(config.get("post", {}).get("checkpoint"), session.run_dir)
            reference = config["train"].get("preparation")
            preparation_path = Path(reference or checkpoint.parent.parent / "artifacts/preparation.json")
            prepared = None
            if reference or preparation_path.is_file():
                from ai4e_core.applications.aero_cfd.trainprep.preparation import consume

                # 与训练消费同一冻结记录；不能在推理时重新拟合统计量。
                prepared = consume(config, preparation_path, prepare=prepare, collate=collate)
                prepare, collate = prepared.prepare, prepared.collate
            restored = restore_model(config, session, construct=component.construct, prepared=prepared)
            if config.get("infer"):
                from ai4e_core.abilities.inference.timing import synchronize

                synchronize(restored["device"])
                report["timings"] = {"restore": perf_counter() - restore_started}
            job.restored = restored
            if config.get("infer"):
                split = config["infer"]["split"]
                selected = config["infer"]["samples"]
                available = restored["index"].partitions.get(split, [])
                if not selected or not set(selected) <= set(available):
                    raise ValueError("infer.samples 不属于指定分片")
                # 索引实例归本次推理所有，旧调用不进入此分支。
                restored["index"].partitions[split] = list(selected)
                config["post"]["sample_indices"] = list(range(len(selected)))
            if prepare is not component.prepare_inputs:
                job.extensions["sampling"] = operation_record(prepare)
            report["checkpoint"] = str(restored["checkpoint"])
            training_protocol = (
                restored["checkpoint"].parent.parent / "artifacts/training-protocol.json"
            )
            original = (
                json.loads(training_protocol.read_text()) if training_protocol.is_file() else {}
            )
            protocol = describe(
                config,
                restored["index"],
                restored["normalization"],
                restored["model"],
                component.construct,
                initial=original.get("initialization"),
                entrypoint=getattr(session, "entrypoint", None),
            )
            if job.extensions:
                protocol["extensions"] = job.extensions
            progress.protocol = protocol
            modern = bool(
                config.get("infer", {}).get("fields") or config.get("infer", {}).get("metrics")
            )
            if modern:
                from ai4e_core.abilities.data.validate.fingerprint import (
                    file_fingerprint,
                    fingerprint,
                )

                inference_protocol = {
                    "version": 2,
                    "weights": file_fingerprint(restored["checkpoint"]),
                    "dataset": file_fingerprint(restored["index"].path)
                    if hasattr(restored["index"], "path")
                    else fingerprint(restored["index"].manifest),
                    "preparation": file_fingerprint(preparation_path),
                    "model": config["model"],
                    "settings": config["infer"],
                    "samples": config["infer"]["samples"],
                    "split": config["infer"]["split"],
                    "execution": {"device": str(restored["device"]), "precision": "fp32"},
                }
                inference_protocol["digest"] = fingerprint(inference_protocol)
                report["inference_protocol"] = inference_protocol
            # 锚点评价/保存共用一个隔离流；完整网格使用恢复后的主流。
            anchor_rng = None
            from ai4e_core.abilities.inference.randomness import capture_rng, restore_rng

            for step in job.steps:
                if modern and step == "evaluation" and "predictions" in job.steps:
                    continue
                if step == "mesh":
                    try:
                        with progress.operation("mesh"):
                            report.update(
                                _export_full_meshes(
                                    job,
                                    config,
                                    session,
                                    restored,
                                    prepare=prepare,
                                    collate=collate,
                                    progress=progress,
                                    protocol=protocol,
                                )
                            )
                    except (FileNotFoundError, KeyError, TypeError, ValueError, OSError) as exc:
                        from ai4e_core.base.events import event

                        reason = f"完整网格无法写出: {exc}"
                        event("网格", "跳过", 原因=reason)
                        report["meshes"] = []
                        report["vtk_full_mesh"] = {"exported": False, "reason": reason}
                        for item in report.get("predictions") or report.get("results") or []:
                            manifest = item.get("manifest")
                            if manifest:
                                record_vtk_status(
                                    manifest,
                                    {"exported": False, "reason": reason},
                                    channel="mesh",
                                )
                        raise
                else:
                    with preserve_randomness():
                        if anchor_rng is not None:
                            restore_rng(anchor_rng)
                        report.update(
                            _run_anchor_path(
                                config,
                                restored,
                                predict=job.predict,
                                prepare=prepare,
                                collate=collate,
                                evaluate=step == "evaluation",
                                save_predictions=step == "predictions",
                                export_vtk=config["post"].get(
                                    "export_pointcloud", config["post"].get("export_vtk", True)
                                ),
                                progress=progress,
                                protocol=protocol,
                                evaluator=job.metric or evaluate_model,
                            )
                        )
                        anchor_rng = capture_rng()
            session.artifact("comparison-protocol.json", protocol)
            progress.finish()
            return report
    except BaseException as exc:
        progress.finish(exc)
        raise
