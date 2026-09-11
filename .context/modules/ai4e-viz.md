# ai4e-viz 模块索引

## 模块边界

- 状态：独立静态比较与本机交互预览共存；整合工作区验收范围见本文末尾。
- 职责：读取稳定 run/report artifact，生成静态或交互视图。
- 允许依赖：`ai4e-spec` 和独立渲染库。
- 禁止依赖：`ai4e-core`、模型、Trainer、Dataset 实现。
- 计算边界：误差与守恒量等研究计算归 core；viz 可执行显示切片/裁切等通用 VTK 过滤，不计算研究差值。
- 结构原则：按稳定 artifact 的读取、渲染和组合能力聚合，不使用 DDD 或 Web 微领域目录。

## 目录索引

- `packages/ai4e-viz/`：包工程根兼 viz 源码根；由构建配置映射为 `ai4e_viz` 导入名。
- `packages/ai4e-viz/render/`：稳定 artifact 到单一图形/视图的渲染。
- `packages/ai4e-viz/compose/`：多个已渲染视图的布局与组合。

## 文档索引

- `packages/ai4e-viz/README.md`：包职责与依赖边界。
- `.context/modules/ai4e-viz.md`：本模块的目录与文档检索入口。
- `.context/mvp/abupt-mvp1.md`：MVP1 报告和可视产物所处阶段。
- `.cursor/rules/ai4e-algorithm-architecture.mdc`：本包的能力分层、高内聚低耦合与代码书写规范。
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`：需要理解 artifact 与可视化解耦原因时按需读取。

新增目录或文档时必须同步本索引。

## 物理数据跨模型实验

render/comparison.py：共色标表面、切面和曲线；compose/comparison.py：离线 HTML；pyproject.toml：仅 spec 和渲染依赖。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `docs/PRD/ai4e-viz/render/PRD.md`、`compose/PRD.md`：渲染和报告功能正文。

报告预算说明由源运行记录提供，HTML 不假定单轮；服务器报告操作见 `docs/aero-cfd-server-runbook.md`，回归见 `tests/integration/test_comparison_visualization.py`。

## 本机平台接入（2026-09-10）

- `packages/ai4e-viz/inspect/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/dispatch.py`：按扩展名分派 VTK/HDF5/PT/NPY/Zarr/文本检查。
- `packages/ai4e-viz/inspect/hdf5.py`：HDF5 字段目录与单数据集读取；VTKHDF 交给网格检查。
- `packages/ai4e-viz/inspect/mesh.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/tensor.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/inspect/text.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/mesh.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/tensor.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/preview/text.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/runtime/__init__.py`：真实文件检查、预览及独立执行。
- `packages/ai4e-viz/runtime/worker.py`：真实文件检查、预览及独立执行。
- `.context/mvp/web-rawprep-acceptance.md`：平台接入验收记录。

- `docs/PRD/ai4e-viz/inspect/PRD.md`：真实字段检查业务。

- `docs/PRD/ai4e-viz/preview/PRD.md`：分页与基础三维预览业务。

- `docs/PRD/ai4e-viz/runtime/PRD.md`：独立进程请求和失败边界。

## 整合工作区实现切片

- `pipeline/execute.py`：表面、平面切片/裁切、阈值、等值的有序 VTK 显示管线；保留源实体身份，生成点明确标记。
- `serialization/geometry.py`：独立几何、拓扑、字段与映射二进制输出；128 MiB 门禁和 manifest 最后提交。
- `preview/fields.py`：完整字段有效值统计和直方图。
- `preview/tensor.py`：指定行列轴及剩余轴索引的分页，不隐式压平高维数组。
- `runtime/worker.py`：旧单 JSON 与新 NDJSON 协议兼容。
- `tests/integration/test_viz_pipeline.py`：真实体切片和二进制交接；其他完整工作区验收由总体验收记录跟踪。
- `docs/PRD/ai4e-viz/pipeline/PRD.md`、`serialization/PRD.md`：过滤和显示交付。
- `tests/integration/test_viz_extended.py`：解析场等值与裁切、向量范围/无效值、真实 Zarr、块选择和拒绝路径。
- Web `modules/visualization`：统一查看器；`infrastructure/rendering/vtk/Viewport.tsx`：资源生命周期与纯显示属性。完整前端索引由主 Agent 统一维护。
- 已通过 20 项圈定 Python 用例，以及真实 ShapeNet/NASA 文件的服务登记→转换→二进制→浏览器、多窗口、阈值、服务场景持久化和恢复自动化。上述不代表所有原型视觉状态已验收。

- `pipeline/tensor_points.py`：受信任显式几何声明到点云，保留独立整数身份；不猜拓扑。
- `.context/mvp/web-visualization-acceptance.md`：可视化切片已测范围与未交付项。
- `.context/mvp/web-visualization-results/`：两真实数据源自动化报告与实际渲染图片。

- 浏览器 `visualization-safety.spec.ts`：窗口预算隔离和单元字段大整数身份拾取；`visualization-views.spec.ts` 包含真实 WebGL context-loss 恢复。

- 浏览器 `visualization-difference.spec.ts`：正式 NASA 双模型差值受控引用到真实点云显示及截图，固定内容修订。

- 浏览器 `visualization-export.spec.ts`：正式 HTTP post 导出 NASA 网格固定资产，原拓扑、预测/真值和原身份交接；具体执行结果见切片验收记录。
- 浏览器 `visualization-subscriptions.spec.ts`：传输协议夹具验证取消仅释放本调用的订阅，并覆盖旧无订阅字段服务；后端共享进程真实隔离由平台验收。

- 浏览器 `visualization-camera.spec.ts`：完整固定源身份、显式同坐标声明、恢复联动重校验；真实服务解析VTK夹具和实际NASA未知单位拒绝分别验收。
