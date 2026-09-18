"""默认轮次循环：有效更新、评估、信号收尾及检查点策略。"""

import math
import signal
import sys
import time
from copy import deepcopy
from itertools import islice

from ai4e_core.base.events import event

from .checkpoint import capture, restore, restore_selection
from .diagnostics import parameter_count, peak_memory
from .execution import execute
from .online import OnlineLoss
from .optimization import update


def fit(
    model,
    optimizer,
    batches,
    step,
    evaluate,
    run,
    *,
    config,
    contract,
    ema=None,
    scaler=None,
    scheduler=None,
    evaluate_repeat=None,
    callbacks=(),
    preserve_selection=False,
):
    """组织一次可恢复训练；业务与模型通过显式调用接口注入。"""
    start, updates, best = 0, 0, math.inf
    if config.get("resume"):
        state = restore(
            config["resume"],
            model,
            optimizer,
            contract=contract,
            ema=ema,
            scaler=scaler,
            scheduler=scheduler,
        )
        start, updates, best = state["epoch"], state["updates"], state["best"]
    epochs = int(config.get("max_epochs", 2))
    if epochs <= start:
        raise ValueError("目标轮次必须大于已恢复轮次")
    log_every = int(config.get("log_every", 1))
    if log_every <= 0:
        raise ValueError("日志轮次间隔必须为正")
    update_interval = _update_interval(config)
    accumulate = int(config.get("accumulate", 1))
    if accumulate < 1:
        raise ValueError("梯度累积步必须为正")
    ema_every = int(config.get("ema_save_every", 10))
    if ema_every < 1:
        raise ValueError("EMA 落盘间隔必须为正")
    device = next(model.parameters()).device
    if config.get("split_counts") is not None:
        event(
            "训练",
            "诊断",
            规模=config["split_counts"],
            参数量=parameter_count(model),
            设备=str(device),
        )
    history = (
        list(state.get("history", []))
        if config.get("resume") and config.get("restore_history")
        else []
    )
    curves = (
        deepcopy(state.get("curves", {}))
        if config.get("resume") and config.get("restore_history")
        else {}
    )
    curves.setdefault("loss", [])
    curves.setdefault("learning_rate", [])
    selected = (
        restore_selection(state, config["resume"], best_on_equal=config.get("best_on_equal", False))
        if preserve_selection and config.get("resume")
        else None
    )
    scheduler_unit = config.get("scheduler_unit", "update")
    validation_interval = int(config.get("validation_interval", 1))
    validation_unit = config.get("validation_unit", "epoch")
    if scheduler_unit not in {"update", "epoch"} or validation_unit not in {"update", "epoch"} or validation_interval < 1:
        raise ValueError("调度单位或验证间隔不合法")
    stop = {"value": False}
    previous = _install_signals(stop, bool(config.get("save_on_interrupt", True)))
    # 异常恢复重放当前 epoch：保存其起始状态，避免带着更新后权重重跑已消费样本。
    recovery = _snapshot(
        model,
        optimizer,
        epoch=start,
        updates=updates,
        best=best,
        contract=contract,
        ema=ema,
        scaler=scaler,
        scheduler=scheduler,
    )
    try:
        if selected is not None:
            run.checkpoint("best", selected)
        for epoch in range(start, epochs):
            recovery = _snapshot(
                model,
                optimizer,
                epoch=epoch,
                updates=updates,
                best=best,
                contract=contract,
                ema=ema,
                scaler=scaler,
                scheduler=scheduler,
            )
            if config.get("restore_history"):
                recovery["history"] = list(history)
                recovery["curves"] = deepcopy(curves)
            if preserve_selection:
                recovery["selection"] = selected
            model.train()
            started = time.monotonic()
            losses = []
            error_sum, element_count = 0.0, 0
            window = OnlineLoss()
            epoch_window = OnlineLoss()

            def advance(index, batch):
                return update(
                    model,
                    optimizer,
                    step,
                    batch,
                    clip=(
                        None
                        if config.get("gradient_clip", 1) is None
                        else float(config.get("gradient_clip", 1))
                    ),
                    scaler=scaler,
                    scheduler=scheduler if scheduler_unit == "update" else None,
                    accumulate=accumulate,
                    accumulation_reduction=config.get("accumulation_reduction", "mean"),
                    accum_index=index,
                    stability=bool(config.get("stability")),
                )

            for completed in execute(
                _complete_groups(batches(epoch), accumulate), advance, start=updates
            ):
                result, advanced = completed.result, completed.advanced
                window.record(result)
                epoch_window.record(result)
                losses.append(float(result["loss"].detach()))
                if config.get("loss_reduction") == "elements":
                    error_sum += float(result["squared_error"])
                    element_count += int(result["element_count"])
                if advanced:
                    updates = completed.updates
                    if ema:
                        ema.update(model)
                    curves["loss"].append(
                        {"epoch": epoch + 1, "updates": updates, "value": float(result["loss"].detach())}
                    )
                    curves["learning_rate"].append(
                        {"epoch": epoch + 1, "updates": updates, "value": float(optimizer.param_groups[0]["lr"])}
                    )
                    for callback in callbacks:
                        callback("update", epoch=epoch + 1, updates=updates, result=result)
                    if update_interval and updates % update_interval == 0:
                        _emit_online_progress(
                            window.flush(),
                            epoch=epoch + 1,
                            updates=updates,
                            lr=optimizer.param_groups[0]["lr"],
                        )
                if stop["value"]:
                    raise InterruptedError("训练收到终止信号")
            if not losses:
                raise ValueError("训练分片为空")
            if scheduler is not None and scheduler_unit == "epoch":
                scheduler.step()
            validation_value = updates if validation_unit == "updates" else epoch
            should_evaluate = config.get("evaluation_enabled", True) and (
                validation_value % validation_interval == 0 or epoch + 1 == epochs
            )
            evaluation = evaluate() if should_evaluate else None
            if evaluation is not None and not math.isfinite(evaluation["loss"]):
                raise ValueError("评估损失非有限")
            repeat = (
                evaluate_repeat()
                if evaluate_repeat is not None and config.get("evaluation_enabled", True)
                else None
            )
            improved = evaluation is not None and (
                evaluation["loss"] <= best
                if config.get("best_on_equal", False)
                else evaluation["loss"] < best
            )
            if improved:
                best = evaluation["loss"]
            record = {
                "epoch": epoch + 1,
                "updates": updates,
                "loss": error_sum / element_count if element_count else sum(losses) / len(losses),
                "learning_rate": optimizer.param_groups[0]["lr"],
                "evaluation": evaluation,
                "seconds": time.monotonic() - started,
            }
            if repeat is not None:
                record["test_repeat"] = repeat
            history.append(record)
            leftover = None if window.empty() else window.flush()
            # 更新日志会清空自己的窗口；页面报告始终保留完整轮次平均。
            record["online"] = epoch_window.flush()
            _publish_training_report(
                run,
                {
                    "epochs": epoch + 1,
                    "updates": updates,
                    "best": best if math.isfinite(best) else None,
                    "history": list(history),
                    "curves": deepcopy(curves),
                },
            )
            if (epoch + 1) % log_every == 0 or epoch + 1 == epochs:
                extra = {}
                memory = peak_memory(device)
                if memory is not None:
                    extra["峰值内存"] = memory
                if sys.stderr.isatty() and epoch + 1 < epochs and record["seconds"] > 0:
                    extra["预计剩余"] = record["seconds"] * (epochs - epoch - 1)
                if config.get("stability"):
                    extra["稳定性"] = result.get("diagnostics", {})
                items = {key: value for key, value in (leftover or {}).items() if key != "loss"}
                if items:
                    extra["在线"] = items
                event(
                    "训练",
                    "进度",
                    轮次=epoch + 1,
                    更新=updates,
                    损失=record["loss"],
                    学习率=optimizer.param_groups[0]["lr"],
                    耗时=record["seconds"],
                    **extra,
                )
            include_ema = ema is not None and (epoch + 1) % ema_every == 0
            payload = _snapshot(
                model,
                optimizer,
                epoch=epoch + 1,
                updates=updates,
                best=best,
                contract=contract,
                ema=ema,
                scaler=scaler,
                scheduler=scheduler,
            )
            for callback in callbacks:
                callback("epoch", epoch=epoch + 1, updates=updates, result=record)
            if config.get("restore_history"):
                payload["history"] = list(history)
                payload["curves"] = deepcopy(curves)
            if preserve_selection:
                if improved:
                    selected = deepcopy(payload)
                payload["selection"] = selected
            run.checkpoint("latest", payload)
            if include_ema:
                run.checkpoint(
                    "ema_latest",
                    {
                        "model": ema.state,
                        "epoch": epoch + 1,
                        "updates": updates,
                        "contract": contract,
                        "weights_only": True,
                    },
                )
            if improved:
                run.checkpoint("best", payload)
        run.checkpoint("last", payload)
    except BaseException as error:
        if config.get("save_on_interrupt", True) or not isinstance(
            error, (KeyboardInterrupt, InterruptedError)
        ):
            try:
                run.checkpoint("latest", recovery)
            except Exception as save_error:  # noqa: BLE001 - 收尾失败保留原始异常
                error.add_note(f"恢复检查点写入失败: {save_error}")
        raise
    finally:
        _restore_signals(previous)
    return {"epochs": epochs, "updates": updates, "best": best, "history": history, "curves": curves}


def _publish_training_report(run, report: dict) -> None:
    """每个轮次覆盖训练报告，检查模式不写。"""
    if getattr(run, "dry_run", False):
        return
    artifact = getattr(run, "artifact", None)
    if callable(artifact):
        artifact("training.json", report)
    publish = getattr(run, "report", None)
    if callable(publish):
        publish(report)


def _update_interval(config) -> int | None:
    """读取更新间隔；空值表示只在轮次末冲刷。"""
    raw = config.get("log_every_updates")
    if raw in (None, ""):
        return None
    value = int(raw)
    if value < 1:
        raise ValueError("日志更新间隔必须为正")
    return value


def _emit_online_progress(averages: dict, *, epoch: int, updates: int, lr: float) -> None:
    """写出一次更新后的在线平均，不触发评估或检查点。"""
    items = {key: value for key, value in averages.items() if key != "loss"}
    extra = {"在线": items} if items else {}
    event("训练", "进度", 轮次=epoch, 更新=updates, 损失=averages["loss"], 学习率=lr, **extra)


def _snapshot(model, optimizer, **kwargs):
    """打包当前可恢复状态。"""
    return capture(model, optimizer, **kwargs)


def _install_signals(stop: dict, save_interrupt: bool) -> dict:
    """监听终止信号；SIGINT 仅在允许保存中断时接管。"""
    previous = {}

    def handle(signum, _frame):
        stop["value"] = True

    previous[signal.SIGTERM] = signal.signal(signal.SIGTERM, handle)
    if save_interrupt:
        previous[signal.SIGINT] = signal.signal(signal.SIGINT, handle)
    return previous


def _restore_signals(previous: dict) -> None:
    """恢复进入循环前的信号处理。"""
    for signum, handler in previous.items():
        signal.signal(signum, handler)


def _complete_groups(batches, accumulate):
    """消耗但不前向或反向不完整尾组，与官方每轮丢弃策略一致。"""
    iterator = iter(batches)
    while group := list(islice(iterator, accumulate)):
        if len(group) < accumulate:
            return
        yield from group
