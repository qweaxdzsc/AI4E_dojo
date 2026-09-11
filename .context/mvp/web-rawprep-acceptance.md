# Dojo Web / Server 首期验收

日期：2026-09-10。范围：本机单用户，复用现有 aero_cfd recipe。

## 已验证的业务链路

真实 Chrome 页面创建项目、任务，读取配置并启用 VTKHDF，选择真实 ShapeNet-Car 完整表面/体积文件，调用服务映射和原 `task.submit_run`，运行原 `pipeline.py` 的 rawprep 阶段，生成真实 PT/VTKHDF、日志和清单。页面打开网格并切换压力场，刷新后进入结果目录，报告保存后刷新仍存在。

同一次浏览器运行生成的 manifest 随后交给现有 `trainprep.dataset.open_manifest_sample` 和 `prepare_physical_sample`：表面 3586 点、过滤后体积 28504 点；压力按原始实体 ID 对照误差为 0，显式准备规则生成的表面 SDF 全零。不是使用前端示例数据，也不是另一次模拟运行替代页面结果。

- [浏览器运行与交接证据](web-rawprep-results/browser-handoff.json)：运行、任务、代码摘要、manifest 位置和各字段形状。
- [真实三维压力场](web-rawprep-results/mesh.png)。
- [三栏与真实执行日志](web-rawprep-results/workbench.png)。

原始输入来自本机已有数据集的一份真实样本，复制到独立验收目录。此结果不代表全量数据集处理、完整数据准备阶段执行或正式训练验收；本期交接检查覆盖现有准备读取及显式物理字段准备。

## 保护范围与最小任务修复

本轮开始和结束对照的 210 个 recipe/core/contrib 文件摘要均未变化。仓库中原本已有其他工作改动，未覆盖或回滚这些改动。task 的 execution.py、worker.py、模板展开和比较实现保持不变。

实际发现：默认模板 `/shared/raw/shapenet_car` 不存在时，new_task 无法创建。只修改 task 创建捕获路径，允许新任务保留待绑定输入；继承资产仍校验，submit_run 严格捕获保持原行为。配置保存、编辑和归档使用任务公开操作，不创建第二份执行方案或调度器。

## 验收入口

后端与任务相关测试：

```bash
UV_OFFLINE=true uv run pytest tests/integration/test_web_project_task.py tests/integration/test_web_rawprep.py tests/integration/test_web_rawprep_handoff.py tests/integration/test_web_recipe_compatibility.py tests/integration/test_web_research_records.py tests/integration/test_web_runtime.py tests/integration/test_web_architecture.py tests/integration/test_viz_file_preview.py tests/integration/test_task_configuration.py tests/integration/test_task_management.py tests/integration/test_task_execution.py tests/integration/test_task_contracts.py tests/integration/test_task_documents.py tests/integration/test_task_installation.py tests/integration/test_recipe_configuration.py tests/integration/test_web_design_documents.py
```

后端圈定 48 项用例全部通过（18.42 秒、无跳过）；结果见 [JUnit 记录](web-rawprep-results/backend.xml)。

前端类型检查与构建、微领域公开门面检查已通过。Chrome 三条浏览器用例通过（13.3 秒）：六页签/八步与未开放状态；项目搜索编辑归档恢复及任务派生；字段联动取消、文件数量、完整样本拒绝、真实执行、场切换、结果目录、生成 manifest/PT 预览和报告恢复。原始处理用例在补齐生成 PT 预览后单独重跑通过（10.9 秒）。测试与浏览器只操作独立验收项目。

运行恢复测试核对服务实例重建后仍查询同一运行，等待工作进程已启动后停止并读取终态 SSE。若进程尚未建立完成收据就被外部终止，原 task 返回 unknown；页面保持待核对，不误报 stopped，也不自动重跑。安装检查使用现有缓存离线构建和仓库外安装；最初网络受限构建失败，离线重跑通过。

## 首期差异与限制

1. 原始处理界面只适配现有 ShapeNet-Car 默认字段和具名输出，表面/体积各一条配置。单元场可检查和预览，但不可作为该案例的提取输出。任意多字段打包、输出重命名、自定义 manifest 和已改写任务脚本明确拒绝，不修改算法来兼容。
2. 比较为创建快照/工作目录/固定运行的文件差异与既有指标表；没有趋势和三维多窗口比较。版本树为基础血缘和节点记录。报告为文字与固定运行证据，没有可视化资产排版、发布审批或导出。
3. 文本与 CSV、NPY/PT、VTK/VTP/VTU/VTKHDF 提供基础检查/预览。张量按首维分页（最多 200 行、64 列），不是任意维度切片编辑器。网格最多 250000 点；大文件仍需工作进程内存，预览超时 90 秒。Zarr、高级切片、插值和重建未提供。
4. 预览与检查在独立进程中运行，但请求通过 HTTP 线程等待结果，未实现持久化预览作业队列。文件刷新与查询为一级目录。原始文件不复制成不可变全集；外部改文件仍可能导致执行失败，运行收据为状态依据。
5. 批量运行及其他七个工作台阶段明确未开放；没有远程多用户、权限系统或资源调度。

## 启动与数据位置

使用 `packages/ai4e-server/README.md` 和 `packages/ai4e-web/README.md`。当前验收服务 root 为 `/private/tmp/dojo-web-acceptance/platform`，仅含验收项目；临时目录可能被系统清理，长期使用请另指定持久目录。正式源码与验收截图、数值证据保存在仓库。
