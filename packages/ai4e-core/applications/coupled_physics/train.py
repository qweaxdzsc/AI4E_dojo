"""单物理场训练装配，领域不实现梯度更新或训练循环。"""

import time
from functools import partial

import torch

from ai4e_core.abilities.inference.execution import inference_execution
from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.abilities.training.moving_average import MovingAverage
from ai4e_core.base.events import event

from .trainprep import FieldSamples, open_preparation


def train_field(settings, prepared, *, field, construct, reader, objective, session, validate=None):
    """装配网络、目标、优化和恢复，返回独立场最新检查点引用。"""
    for key in ("updates", "batch_size", "updates_per_run"):
        value = settings.get(key, settings.get("updates"))
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{key} 必须为正整数")
    preparation = open_preparation(prepared)
    data = FieldSamples(preparation["descriptions"][field + "/train"], reader)
    device = settings["device"]
    torch.manual_seed(settings["seed"])
    model = construct(settings["model"]).to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=settings["lr"], betas=tuple(settings.get("betas", (0.9, 0.999)))
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, settings["updates"], eta_min=settings.get("eta_min", 0.0)
    )
    ema = MovingAverage(model, 0.995, buffer_policy="copy")
    stream = IterationStream(len(data), settings["batch_size"], seed=settings["seed"])
    contract = {
        "field": field,
        "system_id": preparation["content_id"],
        "model": settings["model"],
        "training": {key: settings[key] for key in ("lr", "updates", "batch_size", "seed")},
        "objective": settings["objective"],
        "ema_buffer_policy": "copy",
        "eta_min": settings.get("eta_min", 0.0),
        "betas": list(settings.get("betas", (0.9, 0.999))),
    }
    start, history = 0, []
    best = [float("inf")]
    improved = [False]
    selection = [None]
    if settings.get("resume"):
        state = restore_iteration(
            settings["resume"],
            model,
            optimizer,
            stream=stream,
            contract=contract,
            ema=ema,
            scheduler=scheduler,
        )
        start, history = state["updates"], state["history"]
        best[0] = state.get("selection_metric", float("inf"))
        selection[0] = state.get("selection")
        if selection[0] is not None:
            session.checkpoint("best", selection[0], namespace=field)
    saved = {}

    def checkpoint(updates, losses, status):
        state = capture_iteration(
            model,
            optimizer,
            updates=updates,
            stream=stream,
            contract=contract,
            history=losses,
            ema=ema,
            scheduler=scheduler,
        )
        state["status"] = status
        state["selection_metric"] = best[0]
        if improved[0]:
            selection[0] = state.copy()
            session.checkpoint("best", selection[0], namespace=field)
            improved[0] = False
        state["selection"] = selection[0]
        saved["path"] = session.checkpoint("latest", state, namespace=field)
        event("训练", "更新", field=field, updates=updates, loss=losses[-1] if losses else None)

    def evaluate(updates, current):
        if validate is None:
            return
        with inference_execution(current):
            metric = float(validate(current))
        if metric < best[0]:
            best[0] = metric
            improved[0] = True

    if start == settings["updates"]:
        # 只有当前权重、没有选优快照时重新评价当前状态，不伪造历史最佳。
        if selection[0] is None:
            best[0] = float("inf")
        evaluate(start, model)
    losses = fit_iterations(
        model,
        optimizer,
        stream,
        partial(data.batch, device=device),
        partial(objective, **settings["objective"]),
        updates=min(settings["updates"], start + settings.get("updates_per_run", settings["updates"])),
        start=start,
        scheduler=scheduler,
        ema=ema,
        evaluate=evaluate,
        evaluate_every=settings["evaluate_every"],
        checkpoint=checkpoint,
        history=history,
        deadline=time.monotonic() + settings["seconds"],
    )
    session.report(
        {
            "field": field,
            "updates": len(losses),
            "target_updates": settings["updates"],
            "status": "complete" if len(losses) == settings["updates"] else "budget_slice_complete",
            "initial_loss": losses[0],
            "final_loss": losses[-1],
            "checkpoint": str(saved["path"]),
            "resumed_from": settings.get("resume"),
            "executed_updates": len(losses) - start,
        },
        stage="train/" + field,
    )
    return str(saved["path"])
