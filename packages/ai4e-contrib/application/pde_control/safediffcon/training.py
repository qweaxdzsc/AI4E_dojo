"""SafeDiffCon 训练连接：模型能力与通用迭代器之间的局部适配。"""

import random

import numpy as np
import torch

from ai4e_contrib.ability.constraint.safediffcon.calibration import calibrate
from ai4e_contrib.ability.constraint.safediffcon.objective import reweights
from ai4e_contrib.ability.training.safediffcon.moving_average import MovingAverage
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.applications.pde_control.contracts import digest, read_arrays
from ai4e_core.applications.pde_control.model import restore_model
from ai4e_core.applications.pde_control.train import train_model

from .stream import BatchStream


def seed_all(seed: int) -> None:
    """固定所有实际使用的随机流，两侧按同一阶段种子比较。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)
    torch.set_num_threads(4)


def calibration_inputs(
    prepared: dict, settings: dict, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    """固定原校准集前缀；绝不从测试样本拟合 Q。"""
    _, arrays = read_arrays(prepared["cal"], kind="control_prepared_v1")
    n = settings["calibration_samples"]
    return torch.tensor(np.array(arrays["model"][:n]), device=device), torch.tensor(
        np.array(arrays["target"][:n]), device=device
    )


def pretrain(
    cfg: dict, prepared: dict, *, construct, objective, session, iterate=fit_iterations
) -> str:
    """预训练只消费明确准备；固定宽度和步数来自可编辑案例配置。"""
    seed_all(cfg["seed"])
    _, arrays = read_arrays(prepared["train"], kind="control_prepared_v1")
    settings = cfg["train"]
    model = construct(case=cfg["case"], device=settings["device"], **cfg["model"])
    optimizer = torch.optim.Adam(model.parameters(), lr=settings["lr"], betas=(0.9, 0.99))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10000, eta_min=0)
    ema = MovingAverage(model)
    stream = BatchStream(len(arrays["model"]), settings["batch_size"], seed=cfg["seed"])

    def batch(indices):
        return torch.tensor(np.array(arrays["model"][indices.numpy()]), device=settings["device"])

    contract = {
        "case": cfg["case"],
        "model": cfg["model"],
        "prepared": digest(prepared["train"]),
        "lr": settings["lr"],
        "batch_size": settings["batch_size"],
        "seed": cfg["seed"],
        "phase": "pretrain",
    }
    result = train_model(
        model,
        optimizer,
        stream,
        batch,
        objective,
        updates=settings["updates"],
        scheduler=scheduler,
        ema=ema,
        session=session,
        contract=contract,
        namespace="pretrain",
        resume=settings.get("resume"),
        iterate=iterate,
    )
    return result["checkpoint"]


def posttrain_round(
    cfg: dict,
    prepared: dict,
    checkpoint: str,
    *,
    round_index: int,
    q: float,
    construct,
    objective,
    session,
) -> tuple[str, float]:
    """一轮校准/后训练连接；轮次顺序由 recipe 显式表达。"""
    seed_all(cfg["seed"] + 100 + round_index)
    case, settings = cfg["case"], cfg["posttrain"]
    device = cfg["train"]["device"]
    model, prior = restore_model(
        checkpoint, construct=construct, settings=cfg["model"], case=case, device=device
    )
    phase = prior["contract"]["phase"]
    if (
        (round_index == 0 and phase != "pretrain")
        or (round_index == 1 and (phase != "posttrain" or prior["algorithm_state"]["round"] != 0))
        or round_index not in (0, 1)
    ):
        raise ValueError("后训练轮次与输入检查点阶段不一致")
    if prior["contract"]["prepared"] != digest(prepared["train"]):
        raise ValueError("后训练准备与输入检查点来源不一致")
    if round_index and prior["contract"]["settings"] != settings:
        raise ValueError("连续后训练轮次配置发生变化")
    _, arrays = read_arrays(prepared["train"], kind="control_prepared_v1")
    n = min(settings["subset_size"], len(arrays["model"]))
    states = torch.tensor(np.array(arrays["model"][:n]), device=device)
    targets = torch.tensor(np.array(arrays["target"][:n]), device=device)
    cal_states, cal_targets = calibration_inputs(prepared, settings, device)
    # 本次显式采用论文 Algorithm 2：每轮开头校准，修正原 Burgers 轮末更新顺序。
    calibration_model = model
    if case == "burgers" and round_index:
        calibration_model, _ = restore_model(
            checkpoint,
            construct=construct,
            settings=cfg["model"],
            case=case,
            device=device,
            weight_kind="ema",
        )
    q = calibrate(
        calibration_model,
        cal_states,
        cal_targets,
        case=case,
        q=q,
        weight=settings["weight"],
        alpha=settings["alpha"],
    )
    del calibration_model
    weights = reweights(states, targets, case=case, q=q, weight=settings["weight"])
    optimizer = (
        torch.optim.AdamW(model.parameters(), lr=settings["lr"], weight_decay=1e-4)
        if case == "burgers"
        else torch.optim.Adam(model.parameters(), lr=settings["lr"], betas=(0.99, 0.999))
    )
    ema = MovingAverage(model, beta=0.995) if case == "burgers" else None
    scheduler = None
    if case == "burgers":
        warmup = max(1, int(0.05 * settings["updates_per_round"]))
        scheduler = torch.optim.lr_scheduler.SequentialLR(
            optimizer,
            [
                torch.optim.lr_scheduler.LambdaLR(optimizer, lambda step: min(1.0, step / warmup)),
                torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n * 4, eta_min=1e-6),
            ],
            milestones=[warmup],
        )
        if round_index and prior.get("scheduler"):
            scheduler.load_state_dict(prior["scheduler"])
            ema.state = prior["ema"]
    if round_index and prior.get("algorithm_state", {}).get("phase") == "posttrain":
        optimizer.load_state_dict(prior["optimizer"])
    stream = BatchStream(n, settings["batch_size"], seed=cfg["seed"] + 100 + round_index)
    if round_index and prior.get("algorithm_state", {}).get("phase") == "posttrain":
        stream.load_state_dict(prior["stream"])
    contract = {
        "case": case,
        "model": cfg["model"],
        "prepared": digest(prepared["train"]),
        "phase": "posttrain",
        "round": round_index,
        "settings": settings,
    }
    result = train_model(
        model,
        optimizer,
        stream,
        lambda i: (states[i], weights[i]),
        objective,
        updates=settings["updates_per_round"],
        session=session,
        contract=contract,
        namespace=f"posttrain_{round_index}",
        scheduler=scheduler,
        ema=ema,
        algorithm_state={"phase": "posttrain", "round": round_index, "q": q},
        max_grad_norm=1.0 if case == "burgers" else None,
    )
    return result["checkpoint"], q
