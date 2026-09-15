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
- `packages/ai4e-server/modules/capabilities/__init__.py`：官方模型、起步案例与预设门面。
- `packages/ai4e-server/modules/capabilities/model_cases.py`：两个官方模型与五个起步 example。
- `packages/ai4e-server/modules/capabilities/model_presets.py`：项目共享模型配置预设。
- `packages/ai4e-server/modules/capabilities/trace_source.py`：结构跟踪最近可用物理来源。
- `packages/ai4e-server/modules/capabilities/aero_cfd.py`：登记模板与任务文件集合检查；`recipe_profile.py` 比较 Python 语法/入口 JSON，有限登记已核验的旧配置入口。历史夹具为 `tests/fixtures/rawprep_legacy/configuration.py`，回归入口 `test_web_recipe_compatibility.py`。
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
- `packages/ai4e-server/modules/datasets/`：工作区已处理数据集列表、补登记与数据准备候选项；列表与候选项按登记时间倒序，不扫描 contrib。
- `packages/ai4e-server/modules/rawprep/api.py`：请求、领域规则或业务视图；保存 `dataset.processed_name`，正式执行预检名称；ShapeNet 新建任务描述回 VTKHDF 打开。
- `packages/ai4e-server/modules/rawprep/application.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/domain.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/rawprep/recipe_mapping.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/api.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/reports/domain.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/tasks/__init__.py`：请求、领域规则或业务视图。
- `packages/ai4e-server/modules/tasks/api.py`：任务创建、派生与显式登记的五组起步案例列表，返回 `id`/`name`/`dataset_id`/`model_id`/`variant`/`binding_mode`，不从前缀推断。
- `packages/ai4e-server/pyproject.toml`：工程配置、样式或使用说明。

- `packages/ai4e-server/modules/tasks/dataset.py`：公开数据集目录、本机完整副本识别，以及一次保存数据组件、处理默认和受控路径；旧 `sources` 修订保留。缺 components 的历史外流任务按模板默认目录或 NASA 文件键识别；公开门面由tasks导出。
- `packages/ai4e-server/modules/tasks/api.py`：`GET tasks/{id}/datasets` 列出公开数据集；`PUT tasks/{id}/dataset` 可按副本或受控来源保存。
- `tests/integration/test_web_dataset_binding.py`：五案例、公开目录换绑、跨数据集预设拒绝与模型不兼容拒绝；`test_web_binding_real.py`：真实副本识别及绑定至处理预览。

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

- `infrastructure/transport.py`：标准JSON非有限统计为空，保留原始产物与运行状态；已知业务码映射中文 `error.message`；产品说明 `docs/PRD/ai4e-server/infrastructure/PRD.md`。

`modules/tasks/api.py` 同时提供修订保护的数据来源文件绑定；NASA 三个源文件允许不同已登记目录。`docs/PRD/ai4e-server/infrastructure/PRD.md` 记录服务持久化、受控访问和非有限数传输规则。

`modules/stages/api.py` 仅做传输适配；`stages/application.py` 捕获配置修订、解析固定输入并调用 task，根外且不存在的模板清单占位视为未绑定；`stages/domain.py` 集中阶段顺序、试跑、只读统计、字段匹配和阶段输入选择规则。跨可视化上下文通过 `visualization/__init__.py` 公开门面。

`modules/lineage/api.py` 的版本详情使用 task `read_version_details`，不读取任务内部数据库。可视化相同协议/来源修订/选项共享转换；每个消费方有独立订阅，取消最后订阅才终止，旧不带订阅取消保留明确整体停止语义。

显式 Recipe 扩展验收：标准 `modules/stages` 配置工作台局部保存保留未编辑的用户扩展键和字段列表，不新增通用能力编辑页面。旧专用 rawprep 表单继续要求原模板映射；`tests/integration/test_web_recipe_compatibility.py` 分别核验映射门禁和标准工作台参数保留。证据见 `.context/mvp/recipe-explicit-acceptance.md`。

## 平台一致性接口与验证

- `modules/stages/application.py`：配置与受控输入同修订保存，能力枚举适配、检查修订失效、固定阶段文件范围；阶段文件条目带预览用受控根与相对路径；数据准备附带字段匹配清单、分片默认值和样本名单，保存时校验域、张量形状、执行范围及分片数量；`train.manifest` 候选项同一文件只保留平台名称，不并列任务历史。
- `modules/stages/__init__.py`：向任务上下文公开阶段摘要，列表与工作台共用。
- `modules/stages/api.py`：`stage-summary`、`stage-files`（明确 run_id 或 asset_id+revision）与兼容配置保存接口。
- `modules/visualization/application.py`：辅助检查记录保留任务、阶段、输入、修订及创建时间；查询失效不改历史终态。
- `modules/executions/api.py`：完整原始日志下载；`infrastructure/transport.py`：兼容 detail 的结构化错误。
- `tests/integration/test_web_stage_consistency.py`：真实状态、检查失效、草稿资产范围、相对绑定及同修订保存。
- 圈定回归：`uv run --no-sync pytest tests/integration/test_web_stage_consistency.py tests/integration/test_web_platform_operations.py tests/integration/test_web_project_task.py tests/integration/test_web_runtime.py`。新安装须核对源码加载位置。

- `modules/tasks/templates.py`：按 example 原文件生成内容寻址的登记模板，附加任务入口声明；经 task 公开模板门面创建，NASA 三 H5 输入参与捕获，不替换历史任务脚本。
- `modules/capabilities/api.py`：公共阶段、文件格式与未开放能力；sources/outputs不再冒充跨数据集统一字段，具体字段读取任务目录。
- `stage-files` 按当前层返回清单声明的样本成员；`path` 展开下一层，`query` 按路径搜索。列举不登记资产。Zarr保持叶子，不拆内部文件。

- `infrastructure/content_access.py` 的 `revision` 统一文件/目录摘要；visualization.digest委托该函数，旧preview适配原样支持Zarr目录及分页缓存失效。`test_web_stage_consistency.py`覆盖真实Zarr分页、内容变化与链接拒绝。

- `stage-inputs`同时恢复YAML绑定的受控外部来源；无效绑定以ref=null和compatibility.invalid返回位置，消费者过滤不可选项并显示定位错误。

- `modules/visualization/application.py::archive_asset`打包受控目录到服务downloads缓存；`assets/{id}/content?download=true&revision=…`返回ZIP，新旧修订及符号链接门禁覆盖在一致性测试。

## 独立可视化任务交接

- `packages/ai4e-server/modules/visualization/bindings.py`：受控来源、task 存储与 Vis API 交接。
- `packages/ai4e-server/infrastructure/vis_client.py`：独立服务生命周期与 HTTP 客户端。
- `packages/ai4e-server/infrastructure/vis_proxy.py`：拒绝内部控制 API 的 HTTP/WS 代理。

## 声明驱动原始处理

原始处理描述及绑定来自 task 门面。rawprep 的 sample_scope 为新样本选择入口，旧 files 请求独立兼容；描述校验不在服务维护汽车字段常量。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

三维对象工作台：visualization 原公开门面增加会话内追加结果；宿主来源选择经项目身份校验后进入独立 Vis，保留既有会话和任务版本。浏览器验收 `tests/integration/viz_objects_browser.cjs`，交接测试 `tests/integration/test_viz_host_bindings.py`。

## 登记模型与换模保存

- `modules/capabilities/model_cases.py` 与公开门面：两个官方模型和五个起步 example，按当前数据集与变体解析默认值；任务创建与模板注册复用此登记。
- `modules/capabilities/model_presets.py`：导出项目共享 `kind=model_preset` 配置快照，同数据集列出与选用。
- `modules/capabilities/trace_source.py`：结构跟踪只读解析最近相容准备或正式清单，不回写任务绑定。
- `modules/stages/api.py`：model-options、model-presets 与 `target_model`/`target_preset`；`application.py` 装配原子替换、解除旧输入并在当次检查登记跟踪来源。阶段配置与模型选项透传检查门面的损失、采样能力，不在服务层另推断页面区块。
- 长期行为归 server 模块 PRD；`test_web_stage_consistency.py`、`test_task_configuration.py`、`test_web_dataset_binding.py` 核验换模、导出与自动跟踪；专项见 `mvp/model-picker-acceptance.md`。

## 独立推理服务（实施中）

- `modules/inference/api.py`：任务范围的 checkpoints、samples、check、batches 及 cancel/retry/recover/results HTTP 转换。
- `modules/inference/application.py`：调用 task 公开门面，合并同内容候选标签、核验 profile，将结果成员交给 visualization 公开登记。
- `modules/inference/domain.py`：轻量检查点与批次传输形状，移除工作路径及计算对象；`__init__.py`：公开路由装配。
- `bootstrap/app.py`：装配 inference 路由；`modules/stages` 和 `modules/tasks`：阶段摘要交接，不用页面位置替代运行状态。
- `modules/capabilities/recipe_profile.py`：核验模板内容；新 infer 与已知旧模板通过固定内容清单核验（36 份旧脚本），AS 原工作目录不改写，未知用户改动不可自动放行。
- 路径 `/api/v1/projects/{project}/tasks/{task}/inference`；样本查询 `checkpoint_id` 保留 `run_id:filename` 身份；重试正文使用 `idempotency_key`。后处理只接固定批次、运行、样本引用，结果文件带固定 ref。
- 长期产品说明：`docs/PRD/ai4e-server/modules/PRD.md` 第三章；`tests/integration/test_web_inference.py` 验证 HTTP、文件与请求契约；实际新服务证据及剩余测试由主任务补入 `.context/mvp/inference-acceptance.md`。

## 后处理三页签与固定结果评价

- `modules/post/{api,application,domain,__init__}.py`：评价目录与按层结果文件分开；列举不登记，导出仍固定引用。
- `bootstrap/app.py` 注册post，`modules/visualization/bindings.py`按来源修订和成员去重、串行追加。
- `test_web_post_results.py`、`test_web_post_metrics.py`、`test_viz_host_bindings.py`：授权、引用及来源追加回归。

验收导航：`.context/mvp/post-workspace-acceptance.md`。

## 推理工作台选择与统计

`modules/inference/{api,application,domain}.py`：类型化跨分片请求、目录/统计/导出。`modules/capabilities/recipe_profile.py`：固定旧原生infer兼容指纹。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。
