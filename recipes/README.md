# 可复制模板

Recipe 的逐阶段函数、源码位置、关联 standalone 和使用边界统一收录在 [`docs/agent-help/recipes`](../docs/agent-help/recipes)。Recipe 是仓库内维护源；研究 Agent 应从可复制 standalone 开始，并通过 Agent Help Center 查询 ability、application 和 Task 的现行签名。

本目录不安装、不成为公共 Python 依赖。当前入口见 [aero_cfd](aero_cfd/README.md)。


## 按领域选择现行模板

- [外流 CFD](aero_cfd/README.md)：AB-UPT、Transolver-3，准备/训练/推理/固定结果后处理。
- [参数化 PDE](parametric_pde/README.md)：PI-BSNet 生成、准备与物理训练。
- [耦合物理场](gencp/README.md)：独立场训练与固定权重组合。
- [控制轨迹](safediffcon/README.md)：预训练、后训练、适配与响应。
- [时空预测](wdno/README.md)：小波准备、更新训练与固定结果。
- [MeshGraphNets / CylinderFlow](meshgraphnet/README.md)：固定二维网格图预测、rollout 与轨迹评价。

开始研究前从[任务导航](../.context/tasks/research.md)定位最小修改和验证集合。模板是完整目录，扩展覆盖集需按其 README 覆盖到完整模板；不用为共享循环内部变化迁移原研究脚本。
# 可复制研究模板

`meshgraphnet/` 提供固定二维网格 CylinderFlow 的 MeshGraphNet 时空预测流程。模板按
`rawprep → trainprep → train → infer → post` 显式组织，使用 core 的通用图/轨迹能力和
contrib 的模型/数据连接；Task 从同一 `pipeline.py` 和 `config.yaml` 发现入口。
