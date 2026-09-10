"""外流训练业务装配：项目准备、模型、监督、评估和续训。"""

import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.constraint.supervised import supervised
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.eval.evaluation import evaluate
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
from ai4e_core.base.events import sample_context
from ai4e_spec.components.model import describe_model


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


def build_model(job):
    """在选定设备构建正式模型，并应用初始权重与冻结设置。"""
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
    job.run.artifact("training-protocol.json", job.protocol)
    return job


def configure_objectives(job):
    """按公开监督声明构造比较目标。"""
    job.terms = objectives(job.config.get("model", {}))
    return job


def configure_optimization(job):
    """配置优化器、有效更新调度、EMA 和精度状态。"""
    settings, model, index = job.config["train"], job.model, job.data.index
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
        math.ceil(len(index.partitions["train"]) / int(settings["batch_size"])),
        int(settings.get("accumulate", 1)),
    )
    scheduler = build_scheduler(
        settings.get("scheduler", "warmup_cosine"),
        optimizer,
        total_updates=updates,
        warmup_ratio=float(settings.get("warmup_ratio", 0.05)),
        min_lr=float(settings.get("min_lr", 1e-6)),
    )
    ema = MovingAverage(model, float(settings.get("ema_decay", 0.9999)))
    scaler = torch.amp.GradScaler("cuda") if precision == "amp" else None

    job.optimizer, job.scheduler, job.ema, job.scaler = optimizer, scheduler, ema, scaler
    return job


def configure_evaluation(job, *, step=None, callbacks=()):
    """装配共享数据迭代、评估与恢复契约，训练尚未启动。"""
    config = job.config
    settings = config["train"]
    index, normalization = job.data.index, job.data.normalization
    physical_prepare = job.data.physical_prepare
    normalized_input = index.manifest["state"] == "normalized"
    prepare, collate = job.data.prepare, job.data.collate
    model, predict, terms = job.model, job.predict, job.terms
    device, source, factory = job.device, job.source, job.factory
    selection = settings.get("evaluation_split", "test")

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
        preserve = config["sampling"].get("random_stream") != "global"
        result = evaluate(
            model,
            batches(selection, evaluation=True),
            predict,
            terms,
            normalization,
            preserve_rng=preserve,
            batch_context=batch_scope,
        )
        if not preserve:
            # 官方 OfflineLoss 与 AeroMetrics 为两个独立遍历，必须保留采样流的推进。
            metric_result = evaluate(
                model,
                batches(selection, evaluation=True),
                predict,
                terms,
                normalization,
                preserve_rng=False,
                batch_context=batch_scope,
            )
            result["metrics"] = metric_result["metrics"]
        result["split"] = selection
        return result

    repeats = int(settings.get("test_repeat", 10))

    def evaluate_repeat():
        samples = list(index.partitions[selection])

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
            model, repeated(), predict, terms, normalization, batch_context=batch_scope
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
            if k not in {"resume", "max_epochs", "device", "log_every", "preparation"}
        },
    }
    settings = {
        **settings,
        "split_counts": {name: len(items) for name, items in index.partitions.items()},
    }
    job.execution = {
        "batches": lambda epoch: batches("train", epoch),
        "step": actual_step,
        "evaluate": evaluate_test,
        "repeat": evaluate_repeat if settings.get("evaluate_repeat", False) else None,
        "settings": settings,
        "contract": contract,
        "callbacks": tuple(callbacks),
    }
    return job


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
