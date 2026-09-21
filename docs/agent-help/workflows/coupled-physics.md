<!-- dojo-help: {"case_ids": ["gencp.turek_hron_cno"], "domain": "coupled-physics", "kind": "workflow", "layer": "workflow", "summary": "从 gencp.turek_hron_cno 完成 direct-core、组件变体、Task 和证据读回。", "tasks": ["选择案例", "直接运行", "组件变体", "Task 托管", "证据读回"], "title": "耦合物理场研究流程", "topic_id": "workflow:coupled-physics"} -->
# 耦合物理场研究流程

本流程以 GenCP Turek-Hron CNO 为起点，适用于流固场绑定、逐场网络、时间积分和同步/顺序耦合研究。不同几何案例和 CNO/SiT-FNO 都有独立 standalone。

## 1. 选择精确案例

```python
import ai4e_task as task
case_id = 'gencp.turek_hron_cno'
print(task.search_help("GenCP Turek Hron CNO coupled fields", limit=10))
print(task.read_help_topic("case:" + case_id)["content"])
assert task.check_example(case_id)["ok"]
task.copy_example(case_id, "./study-case")
```

## 2. 核对来源配置

阅读 `source-config.yaml` 与 `config.yaml`。前者记录原算法/案例来源参数，后者是当前 Dojo 可运行配置。核对 fluid/structure 场、条件量、网格/掩码、物理时间、训练窗口和测试序列，不把缩小预算写回参考来源。

## 3. 阅读阶段连接

阶段顺序是 `rawprep → trainprep → train → single → infer → post`。`single` 用于单场验证，完整 infer 才执行多场耦合滚动。阅读 `train.py` 的逐场训练顺序、`single.py` 的固定场验证、`infer.py` 的积分与耦合 step、`post.py` 的固定结果分析。

## 4. direct-core 基线

从案例目录外运行 `pipeline.py`。先缩小字段样本、epoch 和 rollout，但保留真实场绑定和积分入口。读回每个场的 preparation、checkpoint、single 结果、耦合预测清单、物理时间/样本身份、指标和 post 派生结果。

## 5. 修改真实组件

可修改模型构造器、逐场目标、条件编码、积分 step、耦合更新顺序或 post 派生量。`recipe_extensions.gencp` 提供参考变体；物化后检查覆盖文件与 `base_case`，不要直接运行扩展目录。

搜索现行耦合能力：

```python
for query in ("sequential_euler_step", "fsi_synchronous_step", "coupled rollout"):
    print(query, [h["topic_id"] for h in task.search_help(query, limit=10)])
```

## 6. 证明调用和交接

对每个场记录组件身份、权重组、输入条件和 checkpoint；对积分记录步长、步数、物理时间与 step 身份；对耦合记录更新顺序和交换字段。逐场数组必须保留样本、时间和字段身份。只证明单场网络运行不能证明完整耦合流程。

## 7. 独立 infer 和 post

独立 infer 显式绑定全部场的固定 checkpoint 和 preparation，输出每场 NPY、摘要、时间轴、权重组和耦合来源。post 只消费完整结果清单，计算 mask/SDF 派生、指标和图，不重新推进求解器。

## 8. Task 托管


把同一案例目录传给 `new_task`，用 `submit_run`/`wait_run` 分阶段运行。Task 捕获当次代码和配置，但不生成逐场训练逻辑。需要编辑时使用带 revision 的配置 API；每次运行明确绑定前一阶段固定产物。

## 9. 恢复与分支比较

恢复要同时匹配各场 preparation、模型来源、训练合同和场顺序。只加载部分场权重属于初始化或派生研究，不是完整恢复。用 `fork_task` 分离积分或耦合变体；只有数据、物理时间、场定义和指标语义相同才比较数值。

## 10. 结论边界

短训证明参数进入运行、组件被调用、状态可保存恢复、预测和 post 可交接。学习效果需要预先声明的指标和多轮结果；论文级结论还需要论文数据、协议、预算和统计对照。
