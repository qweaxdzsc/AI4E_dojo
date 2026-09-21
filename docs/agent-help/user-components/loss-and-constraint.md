<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "把监督、物理或控制目标作为显式普通函数注入训练步骤。", "tasks": ["编写用户组件", "组件调用证明"], "title": "编写损失与约束", "topic_id": "user-component:loss"} -->
# 编写损失与约束

损失函数明确接收预测、真值及所需物理上下文，返回训练步骤实际消费的标量或命名项。不要通过私有训练会话取数据。

证明损失被调用时记录全限定身份、权重、调用次数和分项值；还要证明该值进入反向更新。改变归约或物理字段会破坏旧指标和恢复可比性。

## 两种常见接口

第一种是纯目标函数，由已有训练步骤调用：

```python
# objectives.py
import torch


def relative_mse(prediction: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    if prediction.shape != target.shape:
        raise ValueError("prediction 和 target 形状必须一致")
    denominator = target.square().mean().clamp_min(1e-12)
    return (prediction - target).square().mean() / denominator
```

第二种是局部训练步骤。参数化 PDE 的公开训练 application 允许 `train.step` 指向普通函数；该函数接收 `network` 和一个已准备实例，返回实际用于反向的 `loss` 及可选命名分项。先阅读基模型 `step` 和准备数据结构，再复制并修改需要的部分。

```python
# research_steps.py
def custom_step(network, prepared):
    # 这里必须按所选 standalone 的准备合同计算 prediction 与 residual。
    data = prepared["sample"]
    prediction = network(data["coordinates"])
    supervised = (prediction - data["u"]).square().mean()
    return {"loss": supervised, "losses": {"supervised": supervised.detach()}}
```

对应配置形态：

```yaml
train:
  step: research_steps.custom_step
```

上面的 batch 键只是接口骨架，必须以所选案例的真实准备结构为准。可用 `describe_help_symbol` 查询基模型 `step`，再读取该符号关联的 standalone。

## 物理约束

物理约束要同时声明：使用的物理字段及单位、导数或拓扑来源、采样域、边界/初值条件、损失公式、归约方式和权重。约束函数可以保持纯计算，领域 application 负责把准备数据和配置传给它。

参数化 PDE 可搜索：

```python
import ai4e_task as task

for query in ("residual_loss", "boundary_residual", "periodic_points"):
    print(query, [h["topic_id"] for h in task.search_help(query, limit=5)])
```

## 验证清单

1. 用手工小张量验证标量、形状、dtype、device 和有限性。
2. 将权重设为 0 和非 0，证明总损失与梯度按预期改变。
3. 在一次真实训练中记录每个命名项和总目标。
4. 比较更新前后参数，证明该目标进入 `backward` 和 optimizer step。
5. 读取检查点 contract，确认损失来源与归约语义已冻结。
6. 用相同固定输入完成连续训练与恢复对照。

同一个数值不代表同一个指标：字段、单位、split、归约、采样和数据身份任一变化都必须视为不同语义。短训损失下降只属于学习效果的初步证据，不能直接升级为精度或论文复现结论。
