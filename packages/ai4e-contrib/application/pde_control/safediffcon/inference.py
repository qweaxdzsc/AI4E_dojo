"""控制推理的样本、更新和物理数组连接；不隐式执行求解器。"""

import numpy as np
import torch

from ai4e_contrib.ability.constraint.safediffcon.calibration import calibrate
from ai4e_contrib.ability.inference.safediffcon.adaptation import adaptation_loss
from ai4e_contrib.ability.inference.safediffcon.control import sample
from ai4e_contrib.ability.training.safediffcon.moving_average import MovingAverage
from ai4e_contrib.ability.transform.safediffcon.preparation import physical
from ai4e_core.applications.pde_control.contracts import digest, read_arrays
from ai4e_core.applications.pde_control.model import restore_model
from ai4e_core.applications.pde_control.train import train_model

from .stream import BatchStream
from .training import calibration_inputs, seed_all


def inputs(cfg: dict, prepared: dict) -> dict:
    """只从显式测试分片选固定前缀，返回模型空间和物理空间两种输入。"""
    _, arrays = read_arrays(prepared["test"], kind="control_prepared_v1")
    n = cfg["infer"]["test_samples"]
    if not 1 <= n <= len(arrays["model"]):
        raise ValueError("推理样本数超出测试分片")
    device = cfg["infer"]["device"]
    return {
        "states": torch.tensor(np.array(arrays["model"][:n]), device=device),
        "target": torch.tensor(np.array(arrays["target"][:n]), device=device),
        "paper_target": np.array(arrays["paper_target"][:n]),
        "ids": np.arange(n) + (49950 if cfg["case"] == "tokamak" else 0),
    }


def adapt(
    cfg: dict, prepared: dict, checkpoint: str, values: dict, *, construct, guide, session
) -> tuple[torch.nn.Module, str, float]:
    """明确更新参数并写入本次有效权重，普通采样不调用此函数。"""
    seed_all(cfg["seed"] + 200)
    case, settings = cfg["case"], cfg["infer"]
    model, state = restore_model(
        checkpoint, construct=construct, settings=cfg["model"], case=case, device=settings["device"]
    )
    if state["contract"]["phase"] != "posttrain" or state["algorithm_state"]["round"] != 1:
        raise ValueError("推理适配须使用两轮后训练完成的明确检查点")
    if state["contract"]["prepared"] != digest(prepared["train"]):
        raise ValueError("推理准备与后训练来源不一致")
    q = state["algorithm_state"]["q"]
    cal_states, cal_targets = calibration_inputs(prepared, cfg["posttrain"], settings["device"])
    q = calibrate(
        model,
        cal_states,
        cal_targets,
        case=case,
        q=q,
        weight=settings["weight"],
        alpha=cfg["posttrain"]["alpha"],
        previous_q=q,
        previous_weight=settings["weight"] if case == "burgers" else cfg["posttrain"]["weight"],
    )
    if settings["adaptation_updates"] == 0:
        return model, checkpoint, q
    optimizer = (
        torch.optim.AdamW(model.parameters(), lr=settings["lr"], weight_decay=1e-4)
        if case == "burgers"
        else torch.optim.Adam(model.parameters(), lr=settings["lr"], betas=(0.99, 0.999))
    )
    ema = MovingAverage(model, beta=0.995) if case == "burgers" else None
    scheduler = (
        torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=max(1, settings["adaptation_updates"]), eta_min=1e-6
        )
        if case == "burgers"
        else None
    )
    stream = BatchStream(len(values["states"]), len(values["states"]), seed=cfg["seed"] + 200)

    def objective(current, ignored):
        return adaptation_loss(
            current,
            values["states"],
            values["target"],
            case=case,
            q=q,
            weight=settings["weight"],
            guide=guide,
        )

    result = train_model(
        model,
        optimizer,
        stream,
        lambda i: i,
        objective,
        updates=settings["adaptation_updates"],
        session=session,
        contract={"case": case, "model": cfg["model"], "phase": "adapt", "parent": checkpoint},
        namespace="adapt",
        ema=ema,
        scheduler=scheduler,
        algorithm_state={"phase": "adapt", "q": q},
        max_grad_norm=1.0 if case == "burgers" else None,
    )
    return ema.model if ema else model, result["checkpoint"], q


def generate(
    cfg: dict, model: torch.nn.Module, values: dict, *, q: float, guide
) -> tuple[np.ndarray, np.ndarray]:
    """普通生成不更新参数，逐批保留模型预测与物理控制。"""
    model.eval()
    outputs = []
    with torch.no_grad():
        for start in range(0, len(values["states"]), cfg["infer"]["batch_size"]):
            stop = start + cfg["infer"]["batch_size"]
            result = sample(
                model,
                values["states"][start:stop],
                values["target"][start:stop],
                case=cfg["case"],
                q=q,
                weight=cfg["infer"]["weight"],
                guide=guide,
            )
            outputs.append(physical(result, case=cfg["case"]).cpu().numpy())
    generated = np.concatenate(outputs)
    if cfg["case"] == "burgers":
        return generated[:, 1, :10], generated[:, 0, :11]
    return generated[:, 3:, :121].transpose(0, 2, 1), generated[:, :3, :122]
