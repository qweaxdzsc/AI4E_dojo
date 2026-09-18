"""共享外流物理数据工作流：模型输入和预测策略由组件注入。"""

import random
from pathlib import Path

import numpy as np
import torch
from omegaconf import OmegaConf

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
from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
from ai4e_core.base.events import sample_context


def datapre(cfg, *, dataset_component, model_component, executor, session):
    """数据组件选择原始处理，已有物理数据可直接从训练准备开始。"""
    return dataset_component.prepare_physical(cfg, executor=executor, session=session)


def trainprep(cfg, dataset=None, *, dataset_component, model_component, session):
    """冻结数据与模型准备，计算结果留在产物而非用户 YAML。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    if dataset:
        config["train"]["manifest"] = dataset["manifest"]
    _, _, record = open_preparation(config, dataset_component, model_component)
    if session.dry_run:
        return {"mode": "trainprep_check", "split_counts": record["split_counts"]}
    path = session.artifact("preparation.json", record)
    report = {"preparation": str(path), "split_counts": record["split_counts"]}
    session.report(report, stage="trainprep")
    return report


class PreparedSamples(torch.utils.data.Dataset):
    """按需读一个物理样本，组件返回单实例计算批次。"""

    def __init__(self, view, component, config, normalization):
        self.view, self.component = view, component
        self.config, self.normalization, self.epoch = config, normalization, 0

    def __len__(self):
        return len(self.view.partitions["train"])

    def __getitem__(self, index):
        with sample_context(
            "训练准备",
            [
                {
                    "sample": self.view.partitions["train"][index],
                    "partition": "train",
                    "index": index,
                }
            ],
        ):
            sample = self.view.read("train", index)
            validate_bindings(sample, self.config["trainprep"])
            return self.component.prepare_sample(
                sample, self.config, self.normalization, epoch=self.epoch
            )


def train(cfg, prepared=None, *, dataset_component, model_component, session):
    """模型选择不改变训练循环，顺序训练独立实例。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    settings = config["train"]
    if (
        settings["batch_size"] != 1
        or settings["num_workers"] != 0
        or settings["precision"] != "fp32"
    ):
        raise ValueError("当前共享物理路径要求 batch_size=1、num_workers=0、fp32")
    if settings.get("evaluation_enabled", True):
        raise ValueError("当前共享实验训练需关闭训练期评价，使用独立 post 全点评价")
    reference = prepared or settings.get("preparation")
    if isinstance(reference, dict):
        reference = reference["preparation"]
    if reference:
        import json

        config["train"]["manifest"] = json.loads(Path(reference).read_text())["manifest"]
    view, normalization, record = open_preparation(
        config, dataset_component, model_component, reference
    )
    if session.dry_run:
        return {"mode": "train_check", "split_counts": record["split_counts"]}
    session.artifact("preparation.json", record)
    seed = int(config["sampling"]["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    device = resolve_device(settings["device"])
    generator = (
        torch.Generator().manual_seed(seed)
        if config["sampling"].get("random_stream") != "global"
        else None
    )
    data = PreparedSamples(view, model_component, config, normalization)
    loader = torch.utils.data.DataLoader(
        data, batch_size=None, shuffle=True, num_workers=0, generator=generator
    )
    model = (
        model_component.construct(**model_component.training_parameters(config)).to(device).float()
    )
    initialize_weights(
        model, path=config["model"].get("initial_weights"), freeze=config["model"].get("freeze", [])
    )
    optimizer = build_optimizer(
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
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=settings["max_epochs"],
            eta_min=settings["learning_rate"] * settings["min_lr_ratio"],
        )
    else:
        scheduler = build_scheduler(
            settings["scheduler"],
            optimizer,
            total_updates=total_updates(settings["max_epochs"], len(data), settings["accumulate"]),
            warmup_ratio=settings["warmup_ratio"],
            min_lr=settings["min_lr"],
        )
    contract = {
        "component": model_component.describe(model),
        "preparation": record["digest"],
        "train": {
            k: v
            for k, v in settings.items()
            if k not in {"manifest", "preparation", "resume", "snapshot", "device"}
        },
    }
    protocol = {
        "version": 1,
        "dataset": record["dataset"],
        "partitions": view.partitions,
        "normalization": normalization.record,
        "model": model_component.describe(model),
        "initialization": fingerprint(model.state_dict()),
        "training": contract["train"],
        "sampling": config["sampling"],
        "execution": {"device": str(device), "precision": "fp32", "torch": torch.__version__},
        "inputs": [],
    }
    session.artifact("training-protocol.json", protocol)

    def batches(epoch):
        data.epoch = epoch
        for batch in loader:
            yield to_device(batch, device)

    def step(network, batch):
        with sample_context("训练前向", batch["metadata"]):
            protocol["inputs"].append(
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
            return model_component.loss(network, batch, config)

    try:
        report = fit(
            model,
            optimizer,
            batches,
            step,
            None,
            session,
            config={**settings, "split_counts": record["split_counts"]},
            contract=contract,
            scheduler=scheduler,
        )
        protocol["weights"] = fingerprint(model.state_dict())
        session.artifact("training-protocol.json", protocol)
        report["checkpoints"] = {
            key: str(session.run_dir / "checkpoints" / f"{key}.pt") for key in ("latest", "last")
        }
        session.artifact("training.json", report)
        session.report(report)
        return report
    finally:
        del model, optimizer, scheduler
        if device.type == "mps":
            torch.mps.empty_cache()
        elif device.type == "cuda":
            torch.cuda.empty_cache()


def post(cfg, *, dataset_component, model_component, session):
    """统一具名物理预测交接。"""
    from ai4e_core.applications.aero_cfd.workflow import post as legacy_post

    return legacy_post(
        cfg, dataset_component=dataset_component, model_component=model_component, session=session
    )
