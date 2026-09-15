# reportDesigner 产品需求入口

业务范围：报告内容、布局、拖拽、历史操作、草稿和乐观锁编排；与报告中心管理保持独立边界。

引用验收：素材库必须来自统一运行库中的已保存 Visualization；每个引用冻结 artifact、visualization、Spec 版本和内容哈希。

需求变化同步 [模块文件索引](../../.context/modules/reportDesigner.md)、模块/前端/E2E 测试和 [`CHANGELOG.md`](CHANGELOG.md)。

## 项目任务可视化交接（2026-09-14）

报告素材引用固定资产、配置修订、摘要和视口；后续配置修改或增加导出不影响已冻结报告。原报告编排能力保留，本期不扩展平台报告产品流程。

### 固定任务可视化引用

报告素材库在有context时查询当前任务配置资产。新增引用冻结project_id、task_id、visualization_id、revision、content_hash和view；领域校验拒绝非正整数修订，原SQLite引用格式继续读。导出与重试显式传入当前context，不把context或Trame URL写入文档。对应test_report_designer.py和test_vis_exports.py。
