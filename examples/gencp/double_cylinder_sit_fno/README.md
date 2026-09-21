# gencp.double_cylinder_sit_fno

这是 Dojo 的可复制研究案例。

## 统一案例契约

- `example_contract_version=1`，`recipe_contract_version=1`；本目录是可在仓库外复制的完整 standalone。
- 阶段顺序由 `pipeline.py` 的普通 Python 表达，YAML 只提供参数、路径和能力选择。每个阶段脚本都通过公开 `ai4e_core.run.launch` 启动。
- 从目录外运行时使用 `python /path/to/double_cylinder_sit_fno/pipeline.py`，单阶段可直接运行同目录阶段脚本；配置中的 `inputs.*`、`run_root` 和 `data_root` 是唯一交接路径。
- 需要代码快照、资产、后台运行、停止、恢复或比较时，把同一目录交给 `ai4e_task` Python API；Task 不复制训练循环，也不要求 `task-entry.json`。
- 修改网络、损失、字段、采样、优化器、调度器或 post 后，必须从阶段报告、配置快照、检查点、预测、指标和 post 结果证明新组件实际被调用。
- 恢复要区分重新初始化和完整状态恢复；结构、数据身份或更新策略变化可能使原检查点失效。smoke 只证明流程接线、参数生效和产物交接，不构成精度或论文复现结论。
## 输入、阶段与产物

- 模型：`GenCP`；数据集：`double_cylinder_sit`；依赖：`ai4e-core`、`ai4e-contrib`，以及配置中声明的可选模型依赖。
- 阶段顺序：`rawprep → trainprep → train → single → infer → post`。单阶段入口是同名 `.py` 文件；参数覆盖使用 `--set`，不通过隐藏任务文件传参。
- 外部输入放在 `inputs.<stage>.<name>`；运行摘要、阶段报告、检查点、预测、指标和 post 派生结果分别从 `run_root`/`data_root` 的固定清单读回。
- 恢复使用阶段 README 和配置声明的 `inputs.*.resume` 或 `checkpoint` 键；模型结构、数据身份、采样或更新策略改变时先做兼容性检查。
- 仅凭文件存在、导入成功或短训退出不能宣称科学精度；smoke 证据与论文级结论分开记录。

## Agent Help Center

本目录是 `完整案例`。Agent 先读取帮助主题 `case:gencp.double_cylinder_sit_fno`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:gencp.double_cylinder_sit_fno")["content"])
```
