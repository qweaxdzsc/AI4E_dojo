"""逐点监督外流标准装配；数据、模型、运行会话由 recipe 注入。"""

import random

import numpy as np
import torch
from omegaconf import OmegaConf

from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.eval.pointwise import evaluate
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.abilities.training.loop import fit
from ai4e_core.abilities.training.optimization import (
    build_optimizer,
    parameter_groups,
    resolve_device,
)
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample, prepare, publish
from ai4e_core.applications.aero_cfd.trainprep.pointfields import (
    PointDataset,
    collate,
    open_preparation,
)
from ai4e_core.base.events import sample_context


def datapre(cfg, *, dataset_component, model_component, executor, session):
    """显式前处理交接，样本循环仍由既有运行器执行。"""
    config = OmegaConf.to_container(cfg, resolve=True)
    data, raw = prepare(config, dataset_component)
    save = SaveSample(raw, dataset_component, resume=bool(config["dataset"].get("resume", False)))
    result = executor(data, save=save, output=config["paths"]["datasets"])
    result = publish(result, raw, dataset_component)
    session.report(result, stage="rawprep")
    return result


def trainprep(cfg, dataset=None, *, dataset_component, model_component, session):
    """冻结数据和输入声明，可供独立训练进程消费。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    if dataset:
        config["train"]["manifest"] = dataset["manifest"]
    _, _, record = open_preparation(config, dataset_component)
    if session.dry_run:
        return {"mode": "trainprep_check", "split_counts": record["split_counts"]}
    path = session.artifact("preparation.json", record)
    result = {"preparation": str(path), "split_counts": record["split_counts"]}
    session.report(result, stage="trainprep")
    return result


def train(cfg, prepared=None, *, dataset_component, model_component, session):
    """装配数据、模型和评估；参数更新调用唯一通用训练循环。"""
    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    settings = config["train"]
    reference = prepared or settings.get("preparation")
    view, normalization, record = open_preparation(config, dataset_component, reference)
    if session.dry_run:
        return {"mode": "train_check", "split_counts": record["split_counts"]}
    if not reference:
        session.artifact("preparation.json", record)
    seed = int(config["sampling"]["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    device = resolve_device(settings["device"])
    generator = torch.Generator().manual_seed(seed)
    train_loader = torch.utils.data.DataLoader(
        PointDataset(view, normalization, "train", training=True),
        batch_size=1,
        shuffle=True,
        num_workers=0,
        generator=generator,
        collate_fn=collate,
    )
    validation_loader = torch.utils.data.DataLoader(
        PointDataset(view, normalization, "validation"),
        batch_size=1,
        shuffle=False,
        num_workers=0,
        collate_fn=collate,
    )
    model = model_component.construct(**config["model"]["parameters"]).to(device).float()
    optimizer = build_optimizer(
        settings["optimizer"],
        parameter_groups(model, weight_decay=settings["weight_decay"], policy="all"),
        lr=settings["learning_rate"],
        weight_decay=settings["weight_decay"],
        betas=settings["betas"],
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=int(settings["max_epochs"]),
        eta_min=settings["learning_rate"] * settings["min_lr_ratio"],
    )
    contract = {
        "component": model_component.describe(model),
        "preparation": record["digest"],
        "train": {
            k: v
            for k, v in settings.items()
            if k not in {"resume", "manifest", "preparation", "device", "snapshot"}
        },
    }
    protocol = {
        "version": 1,
        "source": model_component.SOURCE,
        "dataset": record["dataset"],
        "partitions": view.partitions,
        "normalization": normalization.record,
        "model": model_component.describe(model),
        "initialization": fingerprint(model.state_dict()),
        "sampling": config["sampling"],
        "training": contract["train"],
        "execution": {"device": str(device), "torch": torch.__version__, "precision": "fp32"},
        "inputs": [],
    }
    session.artifact("training-protocol.json", protocol)

    def batches(epoch):
        for batch in train_loader:
            yield to_device(batch, device)

    def step(network, batch):
        with sample_context("训练前向", batch["metadata"]):
            protocol["inputs"].append(
                {
                    "identity": batch["metadata"],
                    "digest": fingerprint(
                        {
                            "inputs": batch["inputs"],
                            "targets": batch["targets"],
                            "ids": batch["point_ids"],
                        }
                    ),
                }
            )
            output = model_component.predict(network, batch["inputs"])["fields"]
            target = batch["targets"]["fields"]
            if output.shape != target.shape:
                raise ValueError("预测与目标形状不一致")
            difference = output - target
            return {
                "loss": difference.square().mean(),
                "squared_error": float(difference.detach().square().sum().cpu()),
                "element_count": difference.numel(),
            }

    report = fit(
        model,
        optimizer,
        batches,
        step,
        lambda: evaluate(model, validation_loader, model_component.predict, normalization),
        session,
        config={**settings, "split_counts": record["split_counts"]},
        contract=contract,
        scheduler=scheduler,
        preserve_selection=True,
    )
    protocol["weights"] = fingerprint(model.state_dict())
    session.artifact("training-protocol.json", protocol)
    report["checkpoints"] = {
        key: str(session.run_dir / "checkpoints" / f"{key}.pt")
        for key in ("latest", "last", "best")
    }
    session.artifact("training.json", report)
    session.report(report)
    return report


def post(cfg, *, dataset_component, model_component, session):
    """独立推理和导出操作由外流后处理装配。"""
    from ai4e_core.applications.aero_cfd.post.pointfields import execute

    config = model_component.resolve(OmegaConf.to_container(cfg, resolve=True))
    return execute(config, dataset_component, model_component, session)
