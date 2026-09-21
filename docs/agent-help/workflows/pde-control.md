<!-- dojo-help: {"case_ids": ["safediffcon.burgers"], "domain": "pde-control", "kind": "workflow", "layer": "workflow", "summary": "从 safediffcon.burgers 完成 direct-core、组件变体、Task 和证据读回。", "tasks": ["选择案例", "直接运行", "组件变体", "Task 托管", "证据读回"], "title": "控制轨迹研究流程", "topic_id": "workflow:pde-control"} -->
# 控制轨迹研究流程

本流程以 SafeDiffCon Burgers 为起点，覆盖预训练、校准/后训练、控制条件推理和固定结果分析。Tokamak 是另一个独立 standalone，不能只替换数据路径沿用 Burgers 物理合同。

## 1. 选择案例

```python
import ai4e_task as task
case_id = 'safediffcon.burgers'
print(task.search_help("SafeDiffCon control posttrain", limit=10))
print(task.read_help_topic("case:" + case_id)["content"])
assert task.check_example(case_id)["ok"]
task.copy_example(case_id, "./study-case")
```

## 2. 核对控制数据

阶段顺序是 `rawprep → trainprep → train → posttrain → infer → post`。核对状态轨迹、控制轨迹、目标、时间轴、归一化、训练/验证/测试分片和控制边界。缩小 smoke 仍使用真实字段和阶段入口。

## 3. 阅读训练与控制阶段

`train` 生成预训练权重；`posttrain` 消费固定 preparation 与预训练 checkpoint，执行声明轮次的校准/后训练；`infer` 消费最终 checkpoint 生成控制轨迹与响应；`post` 只分析固定结果。预训练与 posttrain checkpoint 必须分开登记。

## 4. direct-core 基线

从案例目录外执行 pipeline。先用 quick 配置或缩小预算验证连接，但记录每个阶段的实际 epoch/update、采样步数和控制目标。读回 preparation、预训练 checkpoint、posttrain 两轮 checkpoint、q/校准状态、控制预测、真实响应、指标和分析文件。

## 5. 修改控制变体

可修改网络、控制目标、引导损失、校准规则、扩散采样器或 post 指标。`recipe_extensions.safediffcon` 提供覆盖参考。修改后保留预训练、posttrain 和 infer 的来源边界；不能把最终权重冒充预训练来源。

## 6. 证明变体被调用

最终配置记录目标和采样参数；阶段报告记录组件身份、控制权重、q 值、轮次和实际调用；checkpoint contract 区分 pretrain/posttrain；结果清单绑定控制轨迹、响应、样本和 checkpoint 摘要。还要证明自定义目标进入梯度或采样更新。

## 7. 独立 infer 与 post

独立 infer 显式绑定 preparation 与最终 posttrain checkpoint。保存控制输入、预测状态、必要的真实/模拟响应、随机采样协议和内容摘要。独立 post 只读这些结果，不能重新做扩散采样或外部求解。

## 8. Task 托管


用 `new_task` 托管同一复制目录。按阶段提交时，每次将固定产物写入 `inputs.<stage>.<name>`；使用 `read_configuration` 和带 revision 的保存 API。Task 的 succeeded 需要结合 core summary 和结果清单判断。

## 9. 恢复和比较

预训练恢复与 posttrain 恢复分别核对模型、optimizer/调度、准备身份和阶段状态。改变控制目标、采样协议或校准规则后从头执行受影响阶段。比较运行时固定控制目标、时间范围、样本、响应定义和指标语义。

## 10. 结论边界

短训证明参数进入运行、组件被调用、状态可保存恢复、预测和 post 可交接。学习效果需要预先声明的指标和多轮结果；论文级结论还需要论文数据、协议、预算和统计对照。
