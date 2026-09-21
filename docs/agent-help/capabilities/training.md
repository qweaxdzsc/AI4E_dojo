<!-- dojo-help: {"topic_id": "capability:training", "title": "训练、优化与恢复", "kind": "tutorial", "layer": "capability", "domain": "training", "summary": "已有模型接入训练循环、调度、梯度累积、检查点及恢复", "tasks": ["已有 PyTorch 模型和 DataLoader 如何复用训练循环", "训练循环", "训练恢复", "优化器", "DataLoader"], "symbols": ["ai4e_core.applications.base.iteration_training.train_model", "ai4e_core.abilities.training.iterations.fit_iterations", "ai4e_core.abilities.training.iteration_stream.IterationStream", "ai4e_core.abilities.training.loop.fit"], "navigation_order": 5} -->
# 训练、优化与恢复

**已有网络和损失时，先检查 train_model 是否可接入，不必复制完整物理案例。** 它接收 model、optimizer、可恢复 stream、batch(ids) 和 objective(model,batch)，负责迭代、停止、检查点及恢复；返回 checkpoint、updates、loss、status 和 history。以下示例直接运行 2 次更新，再用同一合同恢复到累计 4 次。

IterationStream 保存顺序、游标和 RNG；已有 Dataset 可用 batch(ids) 读取并搬到设备。普通 DataLoader 不能直接当作有 next/state_dict/load_state 的 stream；复杂采样器需适配可恢复状态，或选择 epoch 路线的 training.loop.fit 并阅读其合同。已有训练循环只需局部工具时可继续保留，不强制迁移。

优化器、调度器、EMA、梯度累积和自定义 update 均为显式选项；自定义 update 不支持叠加默认累积/scaler。恢复的 updates 是累计总目标。不能把只加载权重称为完整恢复；研究改变数据流或优化策略时更新 contract 并拒绝不相容状态。

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
            namespace="train", resume=resume)
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

## 继续阅读

[接入细节](../user-components/optimizer-and-scheduler.md) · [帮助首页](../index.md)
