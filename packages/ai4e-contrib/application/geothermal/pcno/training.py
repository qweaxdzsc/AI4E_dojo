"""PCNO 分支训练装配；迭代、取消、检查点和 RNG 恢复复用共享训练。"""

import hashlib
import inspect
from pathlib import Path

import torch

from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
from ai4e_core.applications.base.iteration_training import train_model
from ai4e_core.applications.geothermal.data import read_bundle

from .protocol import ModelConfig, TrainConfig


def component_identity(function):
    """冻结所选组件正文，用户可替换构造器而不能静默改变恢复算法。"""
    return {
        "name": function.__module__ + "." + function.__qualname__,
        "sha256": hashlib.sha256(inspect.getsource(function).encode()).hexdigest(),
    }


def train_branch(
    cfg, preparation, branch, *, construct, objective, session, resume=None, cancelled=None
):
    """按原始250轮调度推进明确的更新预算；两个分支各自重置种子。"""
    record = read_bundle(preparation, kind="preparation")
    root = Path(preparation).resolve().parent
    TrainConfig.set_seed(cfg["seed"])
    device = torch.device(cfg["train"]["device"])
    torch.set_num_threads(cfg["train"]["threads"])
    model = construct(
        branch=branch, modes=cfg["model"]["modes"], width=cfg["model"][branch + "_width"]
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    schedule = ModelConfig.lr_lambda(
        1e-3, 9e-4, 1e-3, 1e-5, 1e-6, 15 * 21, 5 * 21, 150 * 21, 80 * 21
    )
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, schedule)
    stats = TrainConfig.stats_to_device(record["statistics"], device)
    target = objective(branch=branch, stats=stats)

    def checked_gradient(value):
        if not torch.isfinite(value).all():
            raise FloatingPointError("PCNO梯度含非有限值；未执行该次更新")
        return value

    for parameter in model.parameters():
        if parameter.requires_grad:
            parameter.register_hook(checked_gradient)
    chunks = [f"chunk_{i:02d}.pt" for i in range(8)]
    stream = RotatingChunkStream(chunks, 3)
    cache = {}

    def read_one(name, row):
        if cache.get("name") != name:
            cache.clear()
            cache.update(
                name=name, value=torch.load(root / name, map_location="cpu", weights_only=False)
            )
        sample = {
            key: (
                [x.to(device) for x in value[row : row + 1]]
                if isinstance(value, list)
                else value[row : row + 1].to(device)
            )
            for key, value in cache["value"].items()
        }
        return sample

    def batch(item):
        name, row, epoch = item
        return read_one(name, row), epoch

    def evaluate(index, current):
        epoch = index // 21
        if index % 21 or epoch < 30 or epoch % 5:
            return
        training = current.training
        current.eval()
        try:
            with torch.no_grad():
                losses = [
                    float(target(current, (read_one(stream.chunks[-1], i), epoch)))
                    for i in range(3)
                ]
            session.report(
                {
                    "epoch": epoch,
                    "validation_loss": sum(losses) / 3,
                    "scope": "rotating validation, not independent test",
                },
                stage=branch + "_validation",
            )
        finally:
            current.train(training)

    contract = {
        "model": cfg["model"],
        "branch": branch,
        "seed": cfg["seed"],
        "data": record["sha256"],
        "statistics": record["statistics"],
        "network": component_identity(construct),
        "objective": component_identity(objective),
        "schedule_epochs": 250,
        "device": str(device),
        "threads": cfg["train"]["threads"],
        "format": "pcno-source-v1-vis-masked",
    }
    return train_model(
        model,
        optimizer,
        stream,
        batch,
        target,
        updates=cfg["train"]["updates"],
        session=session,
        contract=contract,
        namespace=branch,
        scheduler=scheduler,
        resume=resume,
        cancelled=cancelled,
        evaluate=evaluate,
        evaluate_every=21,
    )
