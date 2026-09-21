<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "让 infer 执行预测、评价和固定结果写出，post 只消费结果。", "tasks": ["编写用户组件", "组件调用证明"], "title": "推理组件", "topic_id": "user-component:inference"} -->
# 推理组件

推理组件明确设备、批次、随机种子和输出字段。预测保存后登记数据身份、检查点摘要和样本列表。

新流程不得让 post 在结果缺失时静默重跑模型。随机生成式推理需要保存采样配置和足以复核的来源。

## 标准职责

一个可独立运行的 infer 应按顺序完成：解析固定 preparation 与 checkpoint、构建相同模型、严格核对训练合同、加载权重、执行预测、转回声明的物理状态、计算允许在 infer 阶段完成的评价、保存逐样本结果、发布完整结果清单。

输入通常来自：

```yaml
inputs:
  infer:
    dataset: /absolute/data/manifest.json
    preparation: /absolute/prepared/preparation.json
    checkpoint: /absolute/run/checkpoints/last.pt
```

路径键以所选 standalone 为准；不要把旧案例的 `post.checkpoint` 或 `train.resume` 套到新合同上。

## 添加派生预测字段

`recipe_extensions.inference_fields` 展示纯函数扩展：

```python
import torch


def absolute_error(prediction: torch.Tensor, truth: torch.Tensor) -> torch.Tensor:
    if prediction.shape != truth.shape:
        raise ValueError("预测和真值的实体与分量必须一致")
    difference = prediction - truth
    return torch.linalg.vector_norm(difference, dim=-1, keepdim=True)
```

把函数接在模型预测和保存之间，并为新字段登记名称、实体身份、单位、分量和状态。误差来自物理场时沿用原物理单位；相对误差才是无量纲。

## 添加评价函数

`recipe_extensions.inference_metrics` 的评价函数接收实际物理数组、字段选择和指标声明，再复用公开评价能力：

```python
from ai4e_core.applications.aero_cfd.infer.evaluation import evaluate_sample


def physical_metrics(item, selections, metrics):
    rows = evaluate_sample(item, selections, metrics)
    for row in rows:
        row["algorithm"] = "user-physical-metrics-v1"
    return rows
```

阶段报告和结果清单必须保存评价算法身份。更换公式、分量选择、split 或归约时，旧指标不可直接比较。

## 结果清单

完整结果至少需要：状态、checkpoint 路径和摘要、数据/preparation 身份、样本 ID、逐样本文件与摘要、预测字段语义、实际推理参数和聚合指标。逐样本写出中途失败时保留 `partial_failure`，但不得发布完整成功清单。

## 验证

1. 用固定 checkpoint 和固定样本重复 infer，确定性模式应逐值一致。
2. 随机模式保存 seed、采样器、步数和调度，并按协议比较统计结果。
3. 改变 checkpoint 字节、模型来源或 preparation 身份时严格拒绝。
4. 读回结果清单及每个数据文件，重新计算至少一个指标。
5. 单独运行 post，证明它只依赖固定结果，不加载模型或检查点。

推理脚本返回 0、结果文件存在或能画图，只证明部分接线；还需要清单完整性、内容摘要、身份和读回验证。
