# AB-UPT MVP1

## 当前交付

本期五类业务、AB-UPT 训练、post 锚点推理与完整网格回贴已实现，逐项测试结果见 [验收记录](abupt-acceptance.md)。云图和报告仍在后续范围，不能将本期训练闭环等同于全部产品愿景。

rawprep 形成公共物理数据，trainprep 按项目准备输入，model 定义网络及学习目标，train 执行训练与恢复，post 装配锚点评估保存、可选点云与完整网格回贴。正式入口为根 recipes/aero_cfd 的 datapre.py、trainprep.py、train.py、post.py 和 pipeline.py，统一使用 session.launch；默认执行 datapre → trainprep → train → post。

## 源码与测试定位

- `packages/ai4e-core/applications/aero_cfd/`：五类业务；旧 pre/ 已迁出，train/standard.py 占位已删除。
- `packages/ai4e-core/abilities/`：变换、采样、前馈与位置编码、监督、收批、更新、评估、检查点、推理重建、锚点点云与完整网格导出。
- `tests/integration/test_post_inference.py`：独立后处理锚点评估、保存与点云。
- `tests/integration/test_post_mesh.py`：完整网格回贴与门禁验收。
- `packages/ai4e-contrib/ability/model/abupt/`：锁定来源的正式网络、内部模块、输入组织及收批；README/LICENSE/source.json 记录来源。
- `packages/ai4e-spec/components/model.py`：最小模型构造与要求协议，不依赖数值库。
- `packages/ai4e-core/run/training.py`：现有会话的公开训练桥接，不拥有另一套启动生命周期。
- `tests/contract/test_model_components.py`：安装资源与依赖方向。
- `tests/integration/test_abupt_components.py`：提炼前后输出、梯度和状态键等价。
- `tests/integration/test_train_abupt_real.py`：正式网络小配置拟合及轮次恢复。
- `tests/integration/test_train_recipe.py`：复制案例、真实脚本训练、pipeline 续训、只读和检查模式。
- 其他 A–H 测试节点集中在验收记录，避免维护两份清单。

## 已解决的安装问题

Dojo 与 Noether 使用不同虚拟环境，前者已有 Torch 并不保证隔离构建环境可见 Torch。两个图扩展按唯一清单配置使用本环境 Torch 构建。官方文件域 DNS 失败后使用已配置的阿里云镜像完成安装，PyG 按原模型要求固定 2.6.1；uv.lock 已更新，正常 uv sync --locked --all-packages --all-extras 可用。没有用替身替代正式网络。

## 验收边界

CPU 正式网络使用合法小配置，不声明生产规模训练或与 Noether 训练轨迹完全等价。拟合损失须在最多 1000 次更新内降至初始值 10% 以下；连续两轮和一轮后恢复的参数满足 rtol=1e-5、atol=1e-6。三个通用组件与锁定源实现比较。CUDA 混合精度仅验证可控缩放器的协议和跳步逻辑，不声称本机运行了 CUDA。

已交付 Lion、公开学习率调度、重复评估、梯度累积、源码快照、中断收尾与完整网格回贴。完整 FieldSpec/Sample、缓存、云图和报告仍为后续。外部 AB-UPT/Noether 仓库仅作只读证据，不是正式运行依赖。contrib 网络与 Noether 领域封装接口对齐、权重不等价。

## 多域输入与缓存查询

多域 AB-UPT 使用结构版本 2：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。

新案例配置使用 `model.data_specs`、`model.supervision`、`trainprep`、`sampling.domains`。`post.py` 经现有会话执行，显式设置 `post.checkpoint`，默认只处理 `post.sample_indices=[0]`，块长 `post.query_chunk_size=1024`；查询产物写在数据目录 `predictions/mesh_vtk/`。默认 pipeline 仍只 pre。旧五键入口和旧模型检查点已移除。
