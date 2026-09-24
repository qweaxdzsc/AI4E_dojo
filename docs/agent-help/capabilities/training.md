<!-- dojo-help: {"topic_id": "capability:training", "title": "训练、优化与恢复", "kind": "tutorial", "layer": "capability", "domain": "training", "summary": "神经网络优化与恢复，以及 POD、RSM/RBF、Kriging、LightGBM 非梯度拟合", "tasks": ["已有 PyTorch 模型和 DataLoader 如何复用训练循环", "训练循环", "训练恢复", "优化器", "DataLoader", "非梯度拟合", "POD 拟合", "Kriging 拟合", "LightGBM 拟合"], "symbols": ["ai4e_core.applications.base.iteration_training.train_model", "ai4e_core.abilities.training.iterations.fit_iterations", "ai4e_core.abilities.training.iteration_stream.IterationStream", "ai4e_core.abilities.training.loop.fit", "ai4e_core.abilities.training.epoch_stream.EpochBatchStream", "ai4e_core.abilities.training.selection.BestMetric", "ai4e_core.abilities.training.reduced_basis.fit_pod", "ai4e_core.abilities.training.algebraic.fit_least_squares", "ai4e_core.abilities.training.algebraic.fit_rsm", "ai4e_core.abilities.training.algebraic.fit_rbf", "ai4e_core.abilities.training.kriging.solve_kriging_condition", "ai4e_core.abilities.training.kriging.condition_kriging", "ai4e_core.abilities.training.kriging.fit_kriging", "ai4e_core.abilities.training.kriging.kriging_profile_gradient", "ai4e_core.abilities.training.boosting.fit_boosting"], "navigation_order": 5} -->
# 训练、优化与恢复

**完整新训练任务从最接近的 standalone 复制并改写 recipe；已有网络和损失作为用户组件接入。** 下述 `train_model` 小例子演示训练连接，不代替完整案例的流程与组件组织。它接收 model、optimizer、可恢复 stream、batch(ids) 和 objective(model,batch)，负责迭代、停止、检查点及恢复；返回 checkpoint、updates、loss、status 和 history。以下示例直接运行 2 次更新，再用同一合同恢复到累计 4 次；已有成熟工程的局部接入或单工具请求可独立采用。

IterationStream 保存顺序、游标和 RNG；已有 Dataset 可用 batch(ids) 读取并搬到设备。普通 DataLoader 不能直接当作有 next/state_dict/load_state 的 stream；复杂采样器需适配可恢复状态，或选择 epoch 路线的 training.loop.fit 并阅读其合同。用户已有稳定循环且任务只改局部时可继续保留；新训练任务的框架选择按 dojo-research Skill 进行。

优化器、调度器、EMA、梯度累积和自定义 update 均为显式选项；自定义 update 不支持叠加默认累积/scaler。恢复的 updates 是累计总目标。不能把只加载权重称为完整恢复；研究改变数据流或优化策略时更新 contract 并拒绝不相容状态。

## 从研究逻辑连接到框架

先区分职责：模型和科学损失由研究代码定义；`batch(ids)` 完成读取、轴转换与设备搬运；stream 保留抽样顺序、游标和随机状态；框架负责迭代执行和完整检查点。特殊窗口采样可以实现相同公开 stream 合同，不必同时重写优化器循环。验证可由 `evaluate` / `evaluate_every` 接入；有限 epoch 边界与自定义更新分别见 `epoch_end` / `update_step` 的现行合同。

不要直接接受默认数值设置：`train_model` 默认梯度裁剪为 1.0，原实验未裁剪应显式传 `max_grad_norm=None`。`objective` 内应保留原来的归约顺序、滚动计算图及训练模式；推理辅助函数是否禁用梯度必须单独核对。保存模型权重不等于保存 optimizer、stream、RNG 的完整可恢复状态。

## 非梯度拟合入口

普通拟合对象无需 optimizer、反传或 `.parameters()`。显式用训练分片拟合，交付状态后重建预测器；不要包装成虚假的神经网络训练循环。

- [fit_pod](../api/core/abilities/training/reduced_basis.md)：快照矩阵、rank 与可选权重 → POD 状态；下游系数代理另行拟合。
- [fit_least_squares / fit_rsm / fit_rbf](../api/core/abilities/training/algebraic.md)：设计或输入矩阵及多输出目标 → 拟合状态与诊断。默认拒绝不可识别/奇异系统；ridge、smoothing 须显式选择。
- [condition_kriging / fit_kriging](../api/core/abilities/training/kriging.md)：固定协方差条件化或超参数优化；检查优化诊断和趋势项，不能把求解成功等同优化收敛。
- [fit_boosting](../api/core/abilities/training/boosting.md)：经可选 LightGBM 后端拟合，保留原生模型状态；增量树训练与恢复一次中断优化不是同一含义。

`fit_pod/fit_rsm/fit_rbf` 返回状态；`condition_kriging/fit_kriging/fit_boosting` 返回 `(预测对象, 诊断报告)`；用预测对象的公开状态方法持久化，具体结构按链接核对。状态保存见[数据能力](data.md)，可执行的拟合→保存→重建→分批预测例子见[推理能力](inference.md)。状态重建、增量学习和 optimizer/stream/RNG 的完整续训分别说明。

## 直接入口

- `ai4e_core.applications.base.iteration_training.train_model`
- `ai4e_core.abilities.training.iterations.fit_iterations`
- `ai4e_core.abilities.training.iteration_stream.IterationStream`
- `ai4e_core.abilities.training.loop.fit`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
from pathlib import Path
import torch
from ai4e_core import run
from ai4e_core.run import TrainingRun
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.applications.base.iteration_training import train_model

root = Path.cwd().resolve()  # 将本脚本保存在 root/source/ 下；产物与源码分开
x = torch.arange(8, dtype=torch.float32).reshape(-1, 1) / 8

def objective(model, values):
    return (model(values) - 2 * values).square().mean()

def train(cfg):
    torch.manual_seed(42)
    def fit(updates, resume=None):
        model = torch.nn.Linear(1, 1)
        return train_model(model, torch.optim.Adam(model.parameters(), lr=0.01),
            IterationStream(len(x), 4, seed=42), lambda ids: x[ids], objective,
            updates=updates, session=TrainingRun(), contract={"data": "tiny-v1", "loss": "mse"},
            namespace="train", resume=resume, max_grad_norm=None)
    first = fit(2)
    final = fit(4, first["checkpoint"])
    state = torch.load(final["checkpoint"], map_location="cpu", weights_only=False)
    assert state["updates"] == 4 and len(state["history"]) == 4
    assert "optimizer" in state and "stream" in state
    TrainingRun().report({"updates": 4, "checkpoint": final["checkpoint"]}, stage="train")

def config_loader(path, overrides):
    assert not overrides
    return {"run_root": str(root / "records"), "data_root": str(root / "data"),
            "pipeline": {"stages": ["train"]}, "train": {"snapshot": False}}

assert run.launch({"train": train}, script=__file__, config_loader=config_loader, argv=[]) == 0
```

## 尾批数据流与独立选优

`EpochBatchStream(epoch_items, batch_size, source_contract=..., seed=42, drop_last=False)` 接收用户函数 `epoch_items(rng, epoch)` 产生的有限有序 list/tuple。函数决定抽样及排列，框架不再打乱；记录可用有限数值、字符串以及普通 list/tuple/字符串键 dict，不存数据张量或可执行对象。默认保留尾批；70/16 产生 16、16、16、16、6，显式丢尾不会把6条补到下一轮。空轮和丢尾后零批明确失败。

构造、保存、校验及恢复均不调用抽样函数；首次取批和下一轮首批才消费独立 PCG64。`epoch` 从0开始，未取批为-1；`epoch_end` 在本轮最后一批取出后为真，可传 `epoch_end=lambda stream: stream.epoch_end` 给现有训练入口。恢复校验 `source_contract`、batch和丢尾声明，先完整预检再更改状态。`seed` 仅初始化随机源，恢复后以保存的 RNG 为准。调用者须把数据身份、采样规则和版本写进来源契约；流不能发现同一声明背后偷偷改变的函数。外部副作用、额外全局 RNG、多worker预取不在精确恢复范围。

```python-fragment
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
stream = EpochBatchStream(lambda rng, epoch: rng.permutation(70).tolist(), 16,
                         source_contract={"dataset": "training-v1", "sampling": "permutation-v1"})
first = stream.next()
saved = stream.state_dict()
stream.load_state_dict(saved)  # 不多取一次样本；可交给已有 iteration checkpoint
```

`BestMetric(mode="min", tie="first")` 是独立标量选择器。`tie="last"` 接受相等的新候选；NaN/Inf 失败，`improves(value)` 不改变状态。评价公式和来源由调用方确定；一个选择器只比较同口径指标。先冻结真正受评的 raw/EMA/其他候选权重，writer 成功写入后才 `commit(value, step=..., source=...)`。`source` 为非空字符串，不要求只能为 raw/EMA。

```python-fragment
from copy import deepcopy
from ai4e_core.abilities.training.selection import BestMetric
selector = BestMetric(mode="min", tie="first")
# 位于现有验证回调内，model、metric、step、source、session 由当前案例提供：
if selector.improves(metric):
    selected = {"model": deepcopy(candidate_model.state_dict()), "step": step, "source": source}
    session.checkpoint("best", selected, namespace="train")
    selector.commit(metric, step=step, source=source)
# 局部 checkpoint 装配须同时保存 selector.state_dict() 和 selected 的独立快照。
# 先核对 selected 的 step/source 与选择状态一致，再恢复；不能用最后 raw 权重代替。
```

流状态可经现有 `capture_iteration/restore_iteration` 保存恢复。选择状态与最佳权重由本地对象配对，可通过 `train_model(state_bindings=...)` 的具名save/validate/load一起保存恢复；完整连接见[用户状态](../user-components/checkpoint-state.md)。不要将变化中的选优状态塞进要求静态兼容的 `algorithm_state`。独立工具不改变现有 epoch 训练选优规则，也不提供早停或调度器自动决策。

## 独立周期与状态连接

`checkpoint_every` 和 `evaluate_every` 分别按有效更新触发；同一步先验证再保存。恢复前预检用户状态与固定合同，失败明确报告。可复制变体见 `case:recipe_extensions.tail_batch` 和 `case:recipe_extensions.research_state`。

## 继续阅读

[接入细节](../user-components/optimizer-and-scheduler.md) · [帮助首页](../index.md)
