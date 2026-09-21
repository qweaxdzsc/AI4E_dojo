"""领域无关的迭代训练装配；算法、数据流和组件从调用方注入。"""

from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iterations import fit_iterations


def train_model(
    model,
    optimizer,
    stream,
    batch,
    objective,
    *,
    updates,
    session,
    contract,
    namespace,
    scheduler=None,
    ema=None,
    resume=None,
    algorithm_state=None,
    max_grad_norm=1.0,
    deadline=None,
    iterate=fit_iterations,
    cancelled=None,
    update_step=None,
    accumulate=1,
    accumulation_reduction="mean",
    scaler=None,
    epoch_end=None,
    checkpoint_every=500,
    evaluate=None,
    evaluate_every=None,
):
    """显式恢复后执行训练并交付当前完整状态，writer 独占检查点写入。"""
    if type(updates) is not int or updates < 0:
        raise ValueError("更新次数须为非负整数")
    if (
        type(accumulate) is not int
        or accumulate < 1
        or accumulation_reduction not in {"mean", "sum"}
    ):
        raise ValueError("梯度累积或归约非法")
    if update_step is not None and (accumulate != 1 or scaler is not None):
        raise ValueError("自定义更新不能叠加默认累积或混合精度")
    execution_options = {}
    if evaluate is not None:
        execution_options["evaluate"] = evaluate
    if update_step is not None:
        execution_options["update_step"] = update_step
    if accumulate != 1:
        execution_options["accumulate"] = accumulate
    if accumulation_reduction != "mean":
        execution_options["accumulation_reduction"] = accumulation_reduction
    if scaler is not None:
        execution_options["scaler"] = scaler
    if epoch_end is not None:
        execution_options["epoch_end"] = epoch_end
    if (
        accumulate != 1
        or scaler is not None
        or accumulation_reduction != "mean"
        or epoch_end is not None
    ):
        contract = {
            **contract,
            "execution": {
                "accumulate": accumulate,
                "accumulation_reduction": accumulation_reduction,
                "mixed_precision": scaler is not None,
                "finite_epoch_boundary": epoch_end is not None,
            },
        }
    history = []
    start = 0
    if resume:
        import torch

        candidate = torch.load(resume, map_location="cpu", weights_only=False)
        if candidate.get("updates", 0) > updates:
            raise ValueError("恢复更新次数超过本次总目标")
        if candidate.get("algorithm_state") != (algorithm_state or {}):
            raise ValueError("恢复的校准值、阶段或重加权设置不相容")
        state = restore_iteration(
            resume,
            model,
            optimizer,
            stream=stream,
            contract=contract,
            ema=ema,
            scheduler=scheduler,
            scaler=scaler,
        )
        if state.get("algorithm_state") != (algorithm_state or {}):
            raise ValueError("恢复的校准值、阶段或重加权设置不相容")
        start, history = state["updates"], state["history"]
    result = {}

    def save(index, losses, status):
        payload = capture_iteration(
            model,
            optimizer,
            updates=index,
            stream=stream,
            contract=contract,
            history=losses,
            ema=ema,
            scheduler=scheduler,
            scaler=scaler,
        )
        payload.update(algorithm_state=algorithm_state or {}, status=status)
        result["checkpoint"] = str(session.checkpoint("latest", payload, namespace=namespace))
        result.update(updates=index, loss=losses[-1] if losses else None, status=status)
        session.report(result, stage=namespace)

    def after_update(index, current):
        if index % 50 == 0:
            import logging

            logging.getLogger(__name__).info("%s update=%s/%s", namespace, index, updates)
        if ema:
            ema.update(current)

    history = iterate(
        model,
        optimizer,
        stream,
        batch,
        objective,
        updates=updates,
        start=start,
        scheduler=scheduler,
        ema=None,
        after_update=after_update,
        checkpoint=save,
        evaluate_every=checkpoint_every if evaluate_every is None else evaluate_every,
        deadline=deadline,
        **({"cancelled": cancelled} if cancelled is not None else {}),
        history=history,
        max_grad_norm=max_grad_norm,
        **execution_options,
    )
    result["history"] = history
    return result
