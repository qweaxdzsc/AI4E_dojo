"""外流训练业务装配：项目准备、模型、监督、评估和续训。"""

import hashlib
import json
import math
import random
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.constraint.supervised import supervised
from ai4e_core.abilities.data.source.split import named_slice
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.eval.evaluation import evaluate
from ai4e_core.abilities.eval.metrics import selected_metrics
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.abilities.training.optimization import (
    build_optimizer,
    parameter_groups,
    resolve_device,
)
from ai4e_core.abilities.training.schedule import build_scheduler, total_updates
from ai4e_core.abilities.training.split import route
from ai4e_core.applications.aero_cfd.model.abupt import build
from ai4e_core.applications.aero_cfd.model.objectives import objectives
from ai4e_core.applications.aero_cfd.model.protocol import describe
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep import preparation
from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    iter_partition_batches,
    prepare_partition_sample,
    repeated_samples,
)
from ai4e_core.base.config import operation_record, plain, resolve_operation
from ai4e_core.base.events import sample_context
from ai4e_spec.components.model import describe_model


def training_slice(settings) -> str:
    """开训切片默认 train；旧 validation 并进 eval。"""
    return named_slice((settings or {}).get("training_split"), "train")


@dataclass
class TrainingJob:
    """训练装配状态；由业务步骤逐项构造，循环只消费明确的组件。"""

    config: dict
    run: object
    data: object
    factory: object
    predict: object
    source: str
    model: object = None
    terms: object = None
    optimizer: object = None
    scheduler: object = None
    ema: object = None
    scaler: object = None
    device: object = None
    execution: dict | None = None
    protocol: dict | None = None
    objective: object = None
    extensions: dict | None = None


def open_training(config, run, *, factory, predict, prepare, collate, source, reference=None):
    """消费持久化准备交付；兼容调用未提供引用时先完整准备。"""
    config = apply_resolved(config, validate=True)
    if run.dry_run:
        raise ValueError("fit 检查请使用 trainprep；不会更新模型")
    reference = reference or config["train"].get("preparation")
    if reference:
        data = preparation.consume(config, reference, prepare=prepare, collate=collate)
    else:
        data = preparation.open_dataset(config)
        data = preparation.prepare_fields(data)
        data = preparation.freeze_normalization(data)
        data = preparation.configure_sampling(data, prepare=prepare)
        data = preparation.configure_batching(data, collate=collate)
        data = preparation.validate_preparation(data)
        preparation.publish(data, run)
    effective = data.config
    effective["train"]["manifest"] = str(data.index.path.resolve())
    if reference:
        effective["train"]["preparation"] = (
            reference["preparation"] if isinstance(reference, dict) else str(reference)
        )
    return TrainingJob(effective, run, data, factory, predict, source)


def build_model(job, *, settings=None):
    """在选定设备构建正式模型，并应用初始权重与冻结设置。"""
    if settings is not None:
        requested = plain(settings)
        requested.pop("sampling", None)
        if requested != job.config["model"]:
            raise ValueError("模型设置与准备声明不一致")
    config, settings, factory = job.config, job.config["train"], job.factory
    device = resolve_device(settings.get("device", "auto"))
    precision = settings.get("precision", "fp32")
    if precision not in {"fp32", "amp"} or (precision == "amp" and device.type != "cuda"):
        raise ValueError("混合精度仅支持 CUDA")
    job.device = device
    seed = int(config["sampling"]["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    model_config = config.get("model", {}).get("parameters", {})
    model_config = {**model_config, "data_specs": config["model"]["data_specs"]}
    model = build(factory, model_config, batch_size=int(settings["batch_size"])).to(device)
    from ai4e_core.abilities.modeling.weights import initialize_weights

    initialize_weights(
        model,
        path=config.get("model", {}).get("initial_weights"),
        freeze=config.get("model", {}).get("freeze", []),
    )
    job.model = model
    initial = fingerprint(model.state_dict())
    if settings.get("resume"):
        previous = Path(settings["resume"]).parent.parent / "artifacts/training-protocol.json"
        initial = (
            json.loads(previous.read_text()).get("initialization") if previous.is_file() else None
        )
    job.protocol = describe(
        config,
        job.data.index,
        job.data.normalization,
        model,
        factory,
        initial=initial,
        entrypoint=getattr(job.run, "entrypoint", None),
    )
    if config["sampling"].get("target") or not job.data.prepare.__module__.startswith(
        "ai4e_contrib."
    ):
        job.extensions = {**(job.extensions or {}), "sampling": operation_record(job.data.prepare)}
    job.run.artifact("training-protocol.json", job.protocol)
    return job


def configure_objectives(job, *, settings=None, operation=None):
    """按公开监督声明构造比较目标。"""
    if settings is not None:
        job.config["model"]["supervision"] = plain(settings)
    job.terms = objectives(job.config.get("model", {}))
    selection = job.config.get("model", {}).get("objective", {})
    if operation is not None or selection.get("target"):
        job.objective = resolve_operation(selection, operation=operation)
        job.extensions = {**(job.extensions or {}), "objective": operation_record(job.objective)}
    return job


def configure_optimization(job, *, settings=None):
    """配置优化器、有效更新调度、EMA 和精度状态。"""
    if settings is not None:
        supplied = plain(settings)
        for key in ("batch_size", "device", "precision"):
            if supplied.get(key, job.config["train"][key]) != job.config["train"][key]:
                raise ValueError(f"优化阶段不能改变已准备的 {key}")
        job.config["train"].update(supplied)
    settings, model, index = job.config["train"], job.model, job.data.index
    split = training_slice(settings)
    if not index.partitions.get(split):
        raise ValueError(f"训练切片 {split} 为空，请选择有样本的切片")
    precision = settings.get("precision", "fp32")
    optimizer = build_optimizer(
        settings.get("optimizer", "lion"),
        parameter_groups(model, weight_decay=float(settings.get("weight_decay", 0.05))),
        lr=float(settings.get("learning_rate", 5e-5)),
        weight_decay=float(settings.get("weight_decay", 0.05)),
        betas=settings.get("betas"),
    )
    updates = total_updates(
        int(settings.get("max_epochs", 2)),
        math.ceil(len(index.partitions[split]) / int(settings["batch_size"])),
        int(settings.get("accumulate", 1)),
    )
    scheduler = build_scheduler(
        settings.get("scheduler", "warmup_cosine"),
        optimizer,
        total_updates=updates,
        warmup_ratio=float(settings.get("warmup_ratio", 0.05)),
        min_lr=float(settings.get("min_lr", 1e-6)),
    )
    decay = settings.get("ema_decay", 0.9999)
    ema = MovingAverage(model, float(decay)) if decay is not None else None
    scaler = torch.amp.GradScaler("cuda") if precision == "amp" else None

    job.optimizer, job.scheduler, job.ema, job.scaler = optimizer, scheduler, ema, scaler
    return job


def configure_evaluation(job, *, step=None, callbacks=(), settings=None, operation=None):
    """装配共享数据迭代、评估与恢复契约，训练尚未启动。"""
    if settings is not None:
        supplied = plain(settings)
        for key in (
            "evaluation_split",
            "evaluation_metrics",
            "evaluation_fields",
            "evaluation_aggregate",
            "evaluation_enabled",
            "validation_interval",
            "test_repeat",
            "evaluate_repeat",
            "metric",
        ):
            if key in supplied:
                job.config["train"][key] = supplied[key]
    config = job.config
    settings = config["train"]
    index, normalization = job.data.index, job.data.normalization
    physical_prepare = job.data.physical_prepare
    normalized_input = index.manifest["state"] == "normalized"
    prepare, collate = job.data.prepare, job.data.collate
    model, predict, terms = job.model, job.predict, job.terms
    device, source, factory = job.device, job.source, job.factory
    selection = named_slice(settings.get("evaluation_split"), "test")
    metric_names = selected_metrics(settings.get("evaluation_metrics"))
    requested_fields = set(settings.get("evaluation_fields") or [])
    evaluation_terms = [
        term
        for term in terms
        if not requested_fields
        or term.get("name") in requested_fields
        or term.get("prediction") in requested_fields
        or term.get("target") in requested_fields
        or f"{term.get('domain', '')}/{term.get('name', '')}" in requested_fields
    ]
    if settings.get("evaluation_enabled", True) and requested_fields and not evaluation_terms:
        raise ValueError("evaluation_fields 未匹配任何可评估物理量")
    if settings.get("evaluation_enabled", True) and not index.partitions.get(selection):
        raise ValueError(f"评估分片 {selection} 为空，请选择有样本的分片或关闭测试评估")

    def batches(partition, epoch=0, evaluation=False, repeat=None):
        yield from iter_partition_batches(
            index,
            partition,
            prepare=prepare,
            collate=collate,
            normalization=normalization,
            physical_prepare=physical_prepare,
            normalized_input=normalized_input,
            sampling=config["sampling"],
            config=config,
            batch_size=int(settings["batch_size"]),
            device=device,
            epoch=epoch,
            evaluation=evaluation,
            repeat=repeat,
        )

    def batch_scope(batch):
        return sample_context(
            "训练计算",
            [
                {"sample_id": value["sample"], "index": value.get("index")}
                for value in batch.get("metadata", [])
            ],
        )

    def actual_step(network, batch):
        with batch_scope(batch):
            return (step or default_step)(network, batch)

    def default_step(network, batch):
        if job.objective is not None:
            return job.objective(network, batch, config)
        predictions = route(
            predict(network, batch["inputs"]),
            [item["prediction"] for item in terms],
            kind="预测",
        )
        targets = route(
            batch["targets"],
            [item["target"] for item in terms],
            kind="目标",
        )
        return supervised(predictions, targets, terms)

    def evaluate_test():
        if not index.partitions.get(selection):
            return {"split": selection, "skipped": True, "metrics": {}, "length": 0}
        preserve = config["sampling"].get("random_stream") != "global"
        result = evaluate(
            model,
            batches(selection, evaluation=True),
            predict,
            evaluation_terms,
            normalization,
            preserve_rng=preserve,
            batch_context=batch_scope,
            metric_names=metric_names,
        )
        if not preserve:
            # 官方 OfflineLoss 与 AeroMetrics 为两个独立遍历，必须保留采样流的推进。
            metric_result = evaluate(
                model,
                batches(selection, evaluation=True),
                predict,
                evaluation_terms,
                normalization,
                preserve_rng=False,
                batch_context=batch_scope,
                metric_names=metric_names,
            )
            result["metrics"] = metric_result["metrics"]
        result["split"] = selection
        return result

    repeats = int(settings.get("test_repeat", 10))

    def evaluate_repeat():
        samples = list(index.partitions.get(selection) or [])
        if not samples:
            return {"split": "test_repeat", "skipped": True, "repeats": repeats, "length": 0}

        def repeated():
            for item, _sample, repeat in repeated_samples(samples, repeats):
                batch = collate(
                    [
                        prepare_partition_sample(
                            index,
                            selection,
                            item,
                            prepare=prepare,
                            normalization=normalization,
                            physical_prepare=physical_prepare,
                            normalized_input=normalized_input,
                            sampling=config["sampling"],
                            config=config,
                            evaluation=True,
                            repeat=repeat,
                        )
                    ]
                )
                yield to_device(batch, device)

        result = evaluate(
            model,
            repeated(),
            predict,
            evaluation_terms,
            normalization,
            batch_context=batch_scope,
            metric_names=metric_names,
        )
        result["split"] = "test_repeat"
        result["repeats"] = repeats
        result["length"] = len(samples) * repeats
        return result

    contract = {
        **(
            {"planned_epochs": int(settings["max_epochs"])}
            if settings.get("scheduler") == "warmup_cosine"
            else {}
        ),
        "model_version": describe_model(factory, model)["model_version"],
        "input_layout": describe_model(factory, model)["input_layout"],
        "trainprep": config["trainprep"],
        "source": source,
        "factory": factory.__module__ + "." + factory.__qualname__,
        "model": config.get("model", {}),
        "objectives": terms,
        "normalization": normalization.record,
        "sampling": config["sampling"],
        "manifest_digest": hashlib.sha256(
            json.dumps(index.manifest, sort_keys=True).encode()
        ).hexdigest(),
        "train": {
            k: v
            for k, v in settings.items()
            if k
            not in {
                "resume",
                "max_epochs",
                "device",
                "log_every",
                "preparation",
                "evaluation_metrics",
            }
        },
    }
    settings = {
        **settings,
        "split_counts": {name: len(items) for name, items in index.partitions.items()},
    }
    job.execution = {
        "batches": lambda epoch: batches(training_slice(settings), epoch),
        "step": actual_step,
        "evaluate": evaluate_test,
        "repeat": evaluate_repeat if settings.get("evaluate_repeat", False) else None,
        "settings": settings,
        "contract": contract,
        "callbacks": tuple(callbacks),
    }
    metric_selection = (
        settings.get("metric", {}) if settings is not None else config["train"].get("metric", {})
    )
    if operation is not None or metric_selection.get("target"):
        metric = resolve_operation(metric_selection, operation=operation)

        def evaluate_custom():
            if not index.partitions.get(selection):
                return {"split": selection, "skipped": True, "metrics": {}, "length": 0}
            return metric(model, batches(selection, evaluation=True), config, normalization)

        job.execution["evaluate"] = evaluate_custom
        job.extensions = {**(job.extensions or {}), "metric": operation_record(metric)}
    if job.extensions:
        job.execution["contract"]["extensions"] = job.extensions
        job.protocol["extensions"] = job.extensions
    return job


def configure_resume(job, *, checkpoint=None):
    """登记完整状态恢复；实际恢复仍在既有 fit 生命周期中完成。"""
    job.config["train"]["resume"] = checkpoint
    if job.execution is not None:
        job.execution["settings"]["resume"] = checkpoint
    return job


def check_or_prepare(
    config, *, reference, model_component, prepare_stage, session, public_config=None
):
    """兼容探测与检查模式；准备模式调用 recipe 显式准备阶段。"""
    from ai4e_core.applications.aero_cfd.trainprep.dataset import probe

    if session.dry_run and reference:
        if isinstance(reference, dict) and reference.get("mode", "").endswith("_check"):
            result = {"mode": "train_check", "deferred": True, "reason": "准备检查没有发布产物"}
        else:
            data = preparation.consume(
                config,
                reference,
                prepare=model_component.prepare_inputs,
                collate=model_component.collate,
            )
            result = {"mode": "train_check", "split_counts": data.record["split_counts"]}
        session.report(result)
        return result
    if config["train"].get("mode") == "prepare" and not session.dry_run:
        return prepare_stage(public_config if public_config is not None else config)
    probe_config = deepcopy(config)
    if probe_config["train"].get("mode") == "fit":
        probe_config["train"]["mode"] = "prepare"
    result = probe(probe_config, prepare=model_component.prepare_inputs, dry_run=session.dry_run)
    session.report(
        {
            "mode": config["train"].get("mode", "probe"),
            "sample_id": result["sample_id"],
            "split_counts": result["split_counts"],
            "names": list(result["physical"]),
        }
    )
    return result


def execute_training(job):
    """执行已完整装配的任务，把训练结果交给唯一运行写入方。"""
    if job.execution is None:
        raise ValueError("执行前必须配置评估和保存契约")
    context, run = job.execution, job.run
    model, optimizer = job.model, job.optimizer
    ema, scaler, scheduler = job.ema, job.scaler, job.scheduler
    report = fit(
        model,
        optimizer,
        context["batches"],
        context["step"],
        context["evaluate"],
        run,
        config=context["settings"],
        contract=context["contract"],
        ema=ema,
        scaler=scaler,
        scheduler=scheduler,
        evaluate_repeat=context["repeat"],
        callbacks=context["callbacks"],
    )
    report["checkpoints"] = {
        name: str(run.run_dir / "checkpoints" / (name + ".pt"))
        for name in ("last", "latest", "best")
    }
    if job.protocol is not None:
        job.protocol["weights"] = fingerprint(model.state_dict())
        job.protocol["result"] = {"epochs": report["epochs"], "updates": report["updates"]}
        run.artifact("training-protocol.json", job.protocol)
    if not isinstance(report.get("best"), (int, float)) or not math.isfinite(report["best"]):
        report["best"] = None
    run.artifact("training.json", report)
    run.report(report)
    return report


def train(config, run, *, factory, predict, prepare, collate, source: str, step=None):
    """兼容已有调用，公开 recipe 可逐步装配训练任务。"""
    job = open_training(
        config,
        run,
        factory=factory,
        predict=predict,
        prepare=prepare,
        collate=collate,
        source=source,
    )
    job = build_model(job)
    job = configure_objectives(job)
    job = configure_optimization(job)
    job = configure_evaluation(job, step=step)
    return execute_training(job)
