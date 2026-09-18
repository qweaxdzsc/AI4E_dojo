"""WDNO 的模型准备、优化参数和完整续训装配。"""

import random
import time

import numpy as np
import torch

from ai4e_contrib.ability.training.moving_average import MovingAverage
from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays
from ai4e_core.applications.spatiotemporal_pde.train import fit

from .configuration import component
from .model import diffusion
from .provenance import identity, numerical_sources, recipe_sources
from .stream import SourceStream


def contract(
    cfg: dict,
    prepared: str,
    construct,
    objective,
    *,
    optimizer_factory=None,
    scheduler_factory=None,
    update_step=None,
) -> dict:
    """总目标步数可增加；数据、算法、优化与随机语义不可静默变化。"""
    result = {
        "kind": "wdno-burgers-base-v1",
        "prepared_sha256": digest(prepared),
        "model": {k: v for k, v in cfg["model"].items() if k != "ddim_steps"},
        "train": {
            k: v for k, v in cfg["train"].items() if k not in ("resume", "updates", "seconds")
        },
        "seed": cfg["seed"],
        "network": identity(construct),
        "objective": identity(objective),
        "numerical_sources": numerical_sources(),
        "torch": torch.__version__,
    }
    strategies = {
        name: identity(function)
        for name, function in {
            "optimizer": optimizer_factory,
            "scheduler": scheduler_factory,
            "update": update_step,
        }.items()
        if function is not None
    }
    if strategies:
        result["strategies"] = strategies
    return result


def train(
    cfg: dict,
    prepared: dict,
    *,
    construct,
    objective,
    session,
    cancelled=None,
    optimizer_factory=None,
    scheduler_factory=None,
    update_step=None,
) -> dict:
    """原 Adam/调度/EMA 顺序；全状态 resume 与原权重导入分开。"""
    optimizer_factory = optimizer_factory or component(cfg["components"].get("optimizer"))
    scheduler_factory = scheduler_factory or component(cfg["components"].get("scheduler"))
    update_step = update_step or component(cfg["components"].get("update"))
    started = time.monotonic()
    session.artifact("wdno-recipe.json", recipe_sources(session.entrypoint))
    record, arrays = read_arrays(prepared["train"], kind="spatiotemporal-prepared-v1")
    if record["metadata"]["declaration"]["transform"] != identity(
        component(cfg["components"]["transform"])
    ):
        raise ValueError("准备变换与当前组件不兼容，须重新准备")
    torch.set_num_threads(8)
    random.seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    torch.manual_seed(cfg["seed"])
    device = torch.device(cfg["train"]["device"])
    if device.type == "mps":
        torch.mps.manual_seed(cfg["seed"])
    model = diffusion(cfg["model"], construct).to(device)
    optimizer = (
        torch.optim.Adam(model.parameters(), lr=cfg["train"]["lr"], betas=(0.9, 0.99))
        if optimizer_factory is None
        else optimizer_factory(model, dict(cfg["train"]))
    )
    scheduler = (
        torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10000, eta_min=0)
        if scheduler_factory is None
        else scheduler_factory(optimizer, dict(cfg["train"]))
    )
    ema = MovingAverage(model, beta=0.995, update_every=10)
    stream = SourceStream(len(arrays["values"]), cfg["train"]["batch_size"])
    frozen = contract(
        cfg,
        prepared["train"],
        construct,
        objective,
        optimizer_factory=optimizer_factory,
        scheduler_factory=scheduler_factory,
        update_step=update_step,
    )
    result = fit(
        model,
        prepared["train"],
        optimizer,
        stream,
        objective,
        device=device,
        session=session,
        contract=frozen,
        updates=cfg["train"]["updates"],
        scheduler=scheduler,
        ema=ema,
        resume=cfg["inputs"]["train"]["resume"],
        deadline=started + cfg["train"]["seconds"],
        cancelled=cancelled,
        update_step=update_step,
    )
    result["parameters"] = sum(p.numel() for p in model.parameters())
    session.report(result, stage="train")
    return result
