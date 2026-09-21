"""共享物理训练的公开装配步骤；保留原始数据顺序、初始化和更新算术。"""

import random
from dataclasses import dataclass
from time import perf_counter
from types import SimpleNamespace

import numpy as np
import torch

from ai4e_core.abilities.data.source.split import named_slice
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.data.validate.physical import validate_bindings
from ai4e_core.abilities.modeling.weights import initialize_weights
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.optimization import (
    build_optimizer,
    parameter_groups,
    resolve_device,
)
from ai4e_core.abilities.training.schedule import build_scheduler, total_updates
from ai4e_core.applications.aero_cfd.trainprep import physical as preparation
from ai4e_core.base.config import operation_record, plain, resolve_operation
from ai4e_core.base.events import sample_context


class PreparedSamples(torch.utils.data.Dataset):
    """按需打开物理样本；用户采样函数在 __getitem__ 中得到当前轮次。"""

    def __init__(self, data, component=None, config=None, normalization=None):
        if component is not None:
            from types import SimpleNamespace

            data = SimpleNamespace(
                view=data,
                prepare=component.prepare_sample,
                config=config,
                normalization=normalization,
            )
        self.data, self.epoch = data, 0

    def _split(self):
        return named_slice((self.data.config.get("train") or {}).get("training_split"), "train")

    def __len__(self):
        return len(self.data.view.partitions[self._split()])

    def __getitem__(self, index):
        data = self.data
        split = self._split()
        with sample_context(
            "训练准备",
            [
                {
                    "sample": data.view.partitions[split][index],
                    "partition": split,
                    "index": index,
                }
            ],
        ):
            sample = data.view.read(split, index)
            validate_bindings(sample, data.config["trainprep"])
            return data.prepare(sample, data.config, data.normalization, epoch=self.epoch)


@dataclass
class PhysicalTraining:
    """领域训练装配状态，不暴露循环实现给 recipe。"""

    config: dict
    session: object
    component: object
    data: preparation.PhysicalPreparation
    model: object = None
    device: object = None
    samples: object = None
    loader: object = None
    objective: object = None
    optimizer: object = None
    scheduler: object = None
    contract: dict | None = None
    protocol: dict | None = None
    extensions: dict | None = None
    callbacks: tuple = ()
    dataset_component: object = None


def open_training(config, *, reference, dataset_component, model_component, session):
    """只消费准备并检查现有训练限制；缺少引用不隐藏执行另一条准备链。"""
    config = model_component.resolve(config)
    settings = config["train"]
    if (
        settings["batch_size"] != 1
        or settings["num_workers"] != 0
        or settings["precision"] != "fp32"
    ):
        raise ValueError("当前共享物理路径要求 batch_size=1、num_workers=0、fp32")
    data = preparation.consume(config, dataset_component, model_component, reference)
    if not session.dry_run:
        session.artifact("preparation.json", data.record)
    return PhysicalTraining(
        data.config,
        session,
        model_component,
        data,
        extensions={},
        dataset_component=dataset_component,
    )


def configure_callbacks(job: PhysicalTraining, *, callbacks: tuple = ()) -> PhysicalTraining:
    """登记轮次观察函数，不改变既有训练协议或底层回调签名。"""
    callbacks = tuple(callbacks)
    if not all(callable(callback) for callback in callbacks):
        raise TypeError("训练观察者必须可调用")
    job.callbacks = callbacks
    return job


def check_report(job):
    """只交付检查报告，不初始化或更新网络。"""
    result = {"mode": "train_check", "split_counts": job.data.record["split_counts"]}
    job.session.report(result)
    return result


def build_model(job, *, settings=None):
    """按原顺序设置随机流、数据迭代器与模型初始化。"""
    config = job.config
    if settings is not None:
        model_settings = plain(settings)
        model_settings.pop("sampling", None)
        if model_settings != config["model"]:
            raise ValueError("模型设置与已冻结准备不一致")
    seed = int(config["sampling"]["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    job.device = resolve_device(config["train"]["device"])
    generator = (
        torch.Generator().manual_seed(seed)
        if config["sampling"].get("random_stream") != "global"
        else None
    )
    job.samples = PreparedSamples(job.data)
    job.loader = torch.utils.data.DataLoader(
        job.samples, batch_size=None, shuffle=True, num_workers=0, generator=generator
    )
    job.model = (
        job.component.construct(**job.component.training_parameters(config)).to(job.device).float()
    )
    initialize_weights(
        job.model,
        path=config["model"].get("initial_weights"),
        freeze=config["model"].get("freeze", []),
    )
    return job


def configure_objectives(job, *, settings=None, operation=None):
    """注入 network/batch/config → 损失报告；默认使用模型原学习目标。"""
    settings = plain(settings)
    if settings is not None and not isinstance(settings, dict):
        job.config["model"]["supervision"] = settings
    selection = (
        settings
        if isinstance(settings, dict) and "target" in settings
        else job.config["model"].get("objective", {})
    )
    job.objective = resolve_operation(selection, default=job.component.loss, operation=operation)
    if operation is not None or selection.get("target"):
        job.extensions["objective"] = operation_record(job.objective)
    return job


def configure_optimization(job, *, settings=None, optimizer_factory=None, scheduler_factory=None):
    """装配优化与调度；可选工厂消费 model/settings 或 optimizer/settings/updates_per_epoch。

    未提供工厂时保持原装配；显式工厂来源进入检查点恢复合同。
    """
    if settings is not None:
        supplied = plain(settings)
        for key in ("batch_size", "device", "precision", "num_workers"):
            if supplied.get(key, job.config["train"][key]) != job.config["train"][key]:
                raise ValueError(f"优化阶段不能改变已准备的 {key}")
        job.config["train"].update(supplied)
    settings = job.config["train"]
    model = job.model
    if optimizer_factory is not None or scheduler_factory is not None:
        if optimizer_factory is None or scheduler_factory is None:
            raise ValueError("优化器和调度器工厂须同时提供")
        job.optimizer = optimizer_factory(model, settings)
        job.scheduler = scheduler_factory(
            job.optimizer,
            settings,
            updates_per_epoch=total_updates(1, len(job.samples), settings["accumulate"]),
        )
        job.extensions["optimizer_factory"] = operation_record(optimizer_factory)
        job.extensions["scheduler_factory"] = operation_record(scheduler_factory)
        return job
    job.optimizer = build_optimizer(
        settings["optimizer"],
        parameter_groups(
            model,
            weight_decay=settings["weight_decay"],
            policy=settings.get("parameter_group_policy", "exclude_bias_norm"),
        ),
        lr=settings["learning_rate"],
        weight_decay=settings["weight_decay"],
        betas=settings["betas"],
    )
    if settings.get("scheduler_unit", "update") == "epoch":
        job.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            job.optimizer,
            T_max=settings["max_epochs"],
            eta_min=settings["learning_rate"] * settings["min_lr_ratio"],
        )
    else:
        job.scheduler = build_scheduler(
            settings["scheduler"],
            job.optimizer,
            total_updates=total_updates(
                settings["max_epochs"], len(job.samples), settings["accumulate"]
            ),
            warmup_ratio=settings["warmup_ratio"],
            min_lr=settings["min_lr"],
        )
    return job


def configure_evaluation(job, *, settings=None):
    """冻结训练协议；当前物理路线保留独立全点评价的既有边界。"""
    settings = job.config["train"]
    # 完整物理评价需要逐样本全点推理，统一在独立 infer 中执行。旧案例即使
    # 保留 evaluation_enabled，也不能让通用训练循环调用一个不存在的批次评价器。
    settings["evaluation_enabled"] = False
    job.contract = {
        "component": job.component.describe(job.model),
        "preparation": job.data.record["digest"],
        "train": {
            k: v
            for k, v in settings.items()
            if k
            not in {
                "manifest",
                "preparation",
                "resume",
                "snapshot",
                "device",
                "max_epochs",
                "log_every",
                "log_every_updates",
            }
        },
    }
    if job.extensions:
        job.contract["extensions"] = job.extensions
    job.protocol = {
        "version": 1,
        "dataset": job.data.record["dataset"],
        "partitions": job.data.view.partitions,
        "normalization": job.data.normalization.record,
        "model": job.component.describe(job.model),
        "initialization": fingerprint(job.model.state_dict()),
        "training": job.contract["train"],
        "sampling": job.config["sampling"],
        "execution": {"device": str(job.device), "precision": "fp32", "torch": torch.__version__},
        "inputs": [],
    }
    if job.extensions:
        job.protocol["extensions"] = job.extensions
    job.session.artifact("training-protocol.json", job.protocol)
    return job


def configure_resume(job, *, checkpoint=None):
    """登记恢复要求；真正恢复由 fit 在原有位置加载完整状态。"""
    job.config["train"]["resume"] = checkpoint
    if checkpoint and job.loader.generator is not None:
        # 历史检查点只保存全局 RNG；独立 DataLoader 的种子/轮次仍可重建。
        # 复用相同 DataLoader/RandomSampler 消耗方式，不读物理数据或重做训练。
        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        replay = torch.utils.data.DataLoader(
            range(len(job.samples)),
            batch_size=None,
            shuffle=True,
            num_workers=0,
            generator=job.loader.generator,
        )
        for _epoch in range(int(state["epoch"])):
            for _index in replay:
                pass
    return job


def execute_training(job):
    """执行已装配任务；批次循环留在库内，保留部分来源与硬件资源释放。"""
    if job.objective is None or job.optimizer is None or job.protocol is None:
        raise ValueError("执行前必须配置模型、学习目标、优化及评价协议")

    def batches(epoch):
        job.samples.epoch = epoch
        for batch in job.loader:
            yield to_device(batch, job.device)

    def step(network, batch):
        with sample_context("训练前向", batch["metadata"]):
            job.protocol["inputs"].append(
                {
                    "identity": [
                        {
                            k: v
                            for k, v in item.items()
                            if k in {"sample", "partition", "index", "chunk", "offset"}
                        }
                        for item in batch["metadata"]
                    ],
                    "digest": fingerprint({"inputs": batch["inputs"], "targets": batch["targets"]}),
                }
            )
            return job.objective(network, batch, job.config)

    observations = []

    def observe(event, *, epoch, updates, result):
        if event != "epoch":
            return
        context = SimpleNamespace(
            model=job.model,
            prepared=job.data,
            component=job.component,
            dataset_component=job.dataset_component,
            epoch=epoch,
            updates=updates,
            origin={"run": str(job.session.run_dir), "epoch": epoch, "updates": updates},
        )
        for callback in job.callbacks:
            started = perf_counter()
            produced = callback(context)
            if produced is not None:
                elapsed = perf_counter() - started
                snapshot_seconds = (
                    produced.get("timings", {}).get("snapshot_seconds", 0)
                    if isinstance(produced, dict)
                    else 0
                )
                observations.append(
                    {
                        "epoch": epoch,
                        "updates": updates,
                        "seconds": elapsed,
                        "snapshot_seconds": snapshot_seconds,
                        "analysis_seconds": max(0, elapsed - snapshot_seconds),
                        "result": produced,
                    }
                )

    try:
        report = fit(
            job.model,
            job.optimizer,
            batches,
            step,
            None,
            job.session,
            config={**job.config["train"], "split_counts": job.data.record["split_counts"]},
            contract=job.contract,
            scheduler=job.scheduler,
            callbacks=(observe,) if job.callbacks else (),
        )
        if observations:
            report["observations"] = observations
        job.protocol["weights"] = fingerprint(job.model.state_dict())
        job.session.artifact("training-protocol.json", job.protocol)
        report["checkpoints"] = {
            key: str(job.session.run_dir / "checkpoints" / f"{key}.pt")
            for key in ("latest", "last")
        }
        job.session.artifact("training.json", report)
        job.session.report(report)
        return report
    finally:
        job.model = job.optimizer = job.scheduler = None
        if job.device.type == "mps":
            torch.mps.empty_cache()
        elif job.device.type == "cuda":
            torch.cuda.empty_cache()
