<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "由训练装配构造优化器和调度器，并定义恢复边界。", "tasks": ["编写用户组件", "组件调用证明"], "title": "优化器与调度器", "topic_id": "user-component:optimizer-scheduler"} -->
# 优化器与调度器

配置保存构造器、参数和调度触发时机。训练循环仍由公开 training ability/application 承担，用户代码只替换构造或局部更新策略。

完整恢复需要优化器、调度器、更新步、EMA 和相关 RNG。参数组或更新语义变化时拒绝旧状态，或明确作为仅权重初始化。

## 使用现有选择器

若案例配置已经提供 `train.optimizer`、`train.scheduler`、学习率、warmup 或衰减参数，优先使用这些公开选择。先运行：

```python
import ai4e_task as task

for query in ("optimizer", "scheduler", "warmup cosine", "training update"):
    print(query, [h["topic_id"] for h in task.search_help(query, limit=8)])
```

不要把某个案例的配置键当作全仓协议。以所选 `train.py` 或训练 application 的实际构造调用为准。

## 普通函数扩展

`recipe_extensions.wdno` 提供可复制的三种扩展：

```python
# variant_training.py
import torch


def optimizer(model, options):
    return torch.optim.AdamW(
        model.parameters(),
        lr=options["lr"],
        weight_decay=0.01,
    )


def scheduler(optimizer, options):
    return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10_000)


def update(model, optimizer, value, objective, *, max_grad_norm):
    optimizer.zero_grad(set_to_none=True)
    loss = objective(model, value)
    if loss.ndim or not torch.isfinite(loss):
        raise FloatingPointError("目标必须是有限标量")
    loss.backward()
    if max_grad_norm is not None:
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
    optimizer.step()
    return float(loss.detach()), True
```

配置只增加实际需要替换的函数：

```yaml
components:
  optimizer: variant_training.optimizer
  scheduler: variant_training.scheduler
  update: variant_training.update
```

训练 application 仍负责批次、日志、取消、检查点和恢复。自定义 update 不应另写一套 run 目录或绕过检查点合同。

## 调度语义

必须明确调度器按 update 还是 epoch 推进，warmup 是否计入总目标，梯度累积后何时 step，以及恢复时从哪个计数继续。延长总训练目标时，不应暗中重画原调度曲线；如果 `T_max`、milestones 或 warmup 比例随目标变化，应把它记为新的训练策略。

## 验证

1. 构造器只收到声明参数，参数组覆盖全部预期可训练权重。
2. 一次 update 后参数、优化器 step 和学习率按预期变化。
3. 连续 N 次更新与在固定检查点恢复后的剩余更新逐值或在声明容差内一致。
4. 检查点包含 optimizer、scheduler、EMA/scaler 和更新计数；缺项时只能做权重初始化。
5. 更换优化器、参数组、调度单位或 update 实现后，旧完整恢复应明确拒绝。

优化器能运行只属于工程接线；学习效果需要固定数据、初始化、预算和指标的对照实验。
