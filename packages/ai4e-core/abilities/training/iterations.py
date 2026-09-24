"""按有效更新次数训练，计算目标与局部更新由普通函数提供。"""

import math
import time

import torch

from .execution import execute
from .optimization import update


def fit_iterations(
    model,
    optimizer,
    stream,
    batch,
    objective,
    *,
    updates,
    start=0,
    scheduler=None,
    ema=None,
    evaluate=None,
    evaluate_every=100,
    checkpoint=None,
    checkpoint_every=None,
    deadline=None,
    history=None,
    max_grad_norm=1.0,
    after_update=None,
    cancelled=None,
    update_step=None,
    accumulate=1,
    accumulation_reduction="mean",
    scaler=None,
    epoch_end=None,
):
    """完成有效更新预算；默认保留原算术，显式选用累积/精度能力。

    epoch_end(stream) 在取批后报告真实轮次末尾，用于丢弃不足一组的尾批。
    未传表示连续无限流；自定义更新限无状态、完整精度且不叠加累积。
    checkpoint_every 未指定时沿用评价周期；同一步先评价后保存。
    """
    if any(type(x) is not int for x in (updates, start, evaluate_every)):
        raise ValueError("更新次数和评价间隔须为整数")
    if updates < start or start < 0 or evaluate_every < 1:
        raise ValueError("更新次数或评价间隔非法")
    if checkpoint_every is None:
        checkpoint_every = evaluate_every
    if type(checkpoint_every) is not int or checkpoint_every < 1:
        raise ValueError("检查点间隔须为正整数")
    if type(accumulate) is not int or accumulate < 1:
        raise ValueError("梯度累积步必须为正整数")
    if accumulation_reduction not in {"mean", "sum"}:
        raise ValueError("梯度累积归约必须为 mean 或 sum")
    if update_step is not None and (accumulate != 1 or scaler is not None):
        raise ValueError("自定义更新不能叠加默认累积或混合精度")
    losses = list(history or [])
    if len(losses) != start:
        raise ValueError("恢复历史与有效更新次数不匹配")
    if updates == start:
        if checkpoint:
            checkpoint(start, losses, "complete")
        return losses
    model.train()

    def before(index):
        if (cancelled and cancelled()) or (deadline is not None and time.monotonic() >= deadline):
            if checkpoint:
                checkpoint(index, losses, "interrupted")
            raise TimeoutError("训练计算预算耗尽")

    def work():
        while True:
            values = []
            for _ in range(accumulate):
                try:
                    ids = stream.next()
                except StopIteration:
                    return
                values.append(batch(ids))
                if epoch_end is not None and epoch_end(stream):
                    break
            # 尾组仍报告一次跳步，使取消/截止检查不被不断丢弃的短轮次饿死。
            yield values

    def advance(_index, values):
        if len(values) < accumulate:
            return None, False
        if update_step is not None:
            loss, advanced = update_step(
                model, optimizer, values[0], objective, max_grad_norm=max_grad_norm
            )
            if not math.isfinite(float(loss)):
                raise FloatingPointError("局部更新损失非法")
            return loss, advanced
        if accumulate != 1 or scaler is not None:
            group_losses = []
            for index, value in enumerate(values):
                result, advanced = update(
                    model,
                    optimizer,
                    lambda current, item: {"loss": objective(current, item)},
                    value,
                    clip=max_grad_norm,
                    scaler=scaler,
                    accumulate=accumulate,
                    accumulation_reduction=accumulation_reduction,
                    accum_index=index,
                )
                group_losses.append(float(result["loss"].detach()))
            return sum(group_losses) / len(group_losses), advanced
        # 原迭代入口的数值顺序保持不变，不暗换成另一种梯度检查/清理算法。
        optimizer.zero_grad()
        loss = objective(model, values[0])
        if loss.ndim or not torch.isfinite(loss):
            raise FloatingPointError(f"第 {len(losses)} 次更新损失非法")
        loss.backward()
        if max_grad_norm is not None:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        optimizer.step()
        return loss, True

    completed = start
    for event in execute(work(), advance, start=start, updates=updates, before=before):
        if not event.advanced:
            continue
        completed = event.updates
        if ema:
            ema.update(model)
        if scheduler:
            scheduler.step()
        if after_update:
            after_update(completed, model)
        loss = event.result
        losses.append(float(loss.detach()) if isinstance(loss, torch.Tensor) else float(loss))
        if (completed % evaluate_every == 0 or completed == updates) and evaluate:
            evaluate(completed, model)
        if (completed % checkpoint_every == 0 or completed == updates) and checkpoint:
            checkpoint(completed, losses, "running" if completed < updates else "complete")
    if completed < updates:
        if checkpoint:
            checkpoint(completed, losses, "interrupted")
        raise ValueError("数据流耗尽，未完成有效更新预算")
    return losses
