# ai4e-server 模块索引

本机 API、任务公开门面代理、原始处理映射和报告存储。

## 实际目录与文件

- `packages/ai4e-server/README.md`：工程配置、样式或使用说明。
- `packages/ai4e-server/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/__main__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/bootstrap/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/bootstrap/app.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/bootstrap/dependencies.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/bootstrap/settings.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/infrastructure/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/infrastructure/content_access.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/infrastructure/persistence.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/assets/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/assets/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/capabilities/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/capabilities/aero_cfd.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/capabilities/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/comparisons/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/comparisons/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/executions/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/executions/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/lineage/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/lineage/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/previews/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/previews/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/previews/worker_adapter.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/projects/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/projects/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/projects/application.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/application.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/domain.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/recipe_mapping.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/domain.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/tasks/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/tasks/api.py`：任务创建、派生与显式登记的四组案例列表，返回 `id`/`name`/`dataset_id`/`model_id`/`binding_mode`，不从前缀推断。
- `packages/ai4e-server/pyproject.toml`：工程配置、样式或使用说明。

- `packages/ai4e-server/modules/tasks/dataset.py`：ShapeNet目录与NASA多根文件绑定、动态状态及配置修订；缺 components 的历史外流任务按模板默认目录或 NASA 文件键识别；公开门面由tasks导出。
- `tests/integration/test_web_dataset_binding.py`：四案例与来源范围/恢复测试；`test_web_binding_real.py`：真实绑定至处理预览。

## 文档与验收

- `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 19 节：唯一平台架构。
- `docs/adr/0004-web-server-runtime.md`、`docs/adr/0005-preview-worker.md`：栈、运行和预览进程。
- `.context/mvp/web-rawprep-acceptance.md`：实际验收与未交付范围。
- `docs/PRD/ai4e-server/modules/PRD.md`：现行业务与产品范围。

## 并行工作区接入

- `modules/stages/api.py`：五段配置修订、独立检查、阶段提交及固定产物候选。
- `modules/visualization/application.py`：受控资产、串行转换、幂等、超时、取消和重启核对。
- `modules/visualization/api.py`：资产内容、辅助操作事件与场景接口。
- `modules/visualization/scenes.py`：场景身份、视图引用和联动门禁。
- `infrastructure/persistence.py`：服务记录和场景修订原子比较保存。
- `tests/integration/test_web_platform_operations.py`：固定内容、场景冲突、真实文本进程、符号链接及重启行为。

- `infrastructure/transport.py`：标准JSON非有限统计为空，保留原始产物与运行状态；产品说明 `docs/PRD/ai4e-server/infrastructure/PRD.md`。

`modules/tasks/api.py` 同时提供修订保护的数据来源文件绑定；NASA 三个源文件允许不同已登记目录。`docs/PRD/ai4e-server/infrastructure/PRD.md` 记录服务持久化、受控访问和非有限数传输规则。

`modules/stages/api.py` 仅做传输适配；`stages/application.py` 捕获配置修订、解析固定输入并调用 task，`stages/domain.py` 集中阶段顺序、试跑、只读统计和阶段输入选择规则。跨可视化上下文通过 `visualization/__init__.py` 公开门面。

`modules/lineage/api.py` 的版本详情使用 task `read_version_details`，不读取任务内部数据库。可视化相同协议/来源修订/选项共享转换；每个消费方有独立订阅，取消最后订阅才终止，旧不带订阅取消保留明确整体停止语义。
