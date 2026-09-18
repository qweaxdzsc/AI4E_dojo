# Task 项目共享数据专项验收

实施日期：2026-09-16。Task 与平台主链、真实迁移、隔离双任务交接及圈定回归已通过。跳过用例不计通过。

## 实际交付

正式 rawprep 输出默认位于 `project/shared/datasets/<name>/content/`。名称必须显式填写；同名执行默认失败，Python `submit_run(overwrite=True)` 与 CLI `run --overwrite` 只授权本次覆盖。试跑与检查不发布共享数据。运行记录仍由 core writer 写入任务 runs；准备、归一化副本、训练与预测继续属于任务。

项目公开查询、绑定、迁移不依赖 Server。平台只汇聚已发布资源，按来源项目与共享身份登记，不以名称覆盖其他项目。当前共享引用与历史运行收据分开，同名重做不会回写旧任务、准备或检查点，也不会把新文件显示成旧运行的结果。

入口通过 shared_outputs/stage_inputs 声明输出归属与阶段依赖，未声明的自由入口保持原行为。官方冻结入口仅补本次有效声明，显式空声明不回填；不重写磁盘脚本。五例准备使用各自训练链对应的公开 physical 准备步骤，通用模板和扩展保持原 version=2 交接；没有修改参考算法或固定用户源码基线。

## 功能—文件—验收映射

### A：任务默认生产共享数据

- A1：`tasks/output_bindings.py`、`templates/{models,materialize}.py`、`storage/shared_datasets.py` 分配受控目录。`test_task_shared_execution.py` 覆盖空名、越界、未知占位符；合法声明真实子进程产出共享清单。
- A2：`tasks/{execution,worker}.py` 与官方入口分别绑定物理、准备、预测和运行根。共享执行专项、`test_task_recipe.py` 与实际 wheel 双任务用例验证保存位置及下游训练、推理。
- A3：`selected_inputs` 只跳过同次前序阶段提供的输入。共享执行专项覆盖顺序与独立准备；真实两任务将原网格路径设为不存在，仍完成准备及训练。
- A4：试跑分配任务私有目录；检查不撤下正式资源。专项比较操作前后的完整登记，平台原始处理回归验证检查和试跑交接。

### B：同名显式覆盖与发布门禁

- B1：`execution.py` 捕获单次覆盖许可及幂等指纹，CLI 透传；`worker.py` 再复核后开始写入。专项验证默认失败、CLI 显式覆盖、下一次恢复默认拒绝、同键不同覆盖意图冲突。
- B2：`storage/shared_datasets.py` 使用项目数据库中的独立生产占用，不在复制、计算和大文件摘要期间持有写事务。专项验证并发只有一个生产者、排队取消、启动失败、未知进程占用不被自动释放。
- B3：`worker.py` 与 `records.py` 核对运行收据并发布，失败/取消/强杀/不完整清单不能变为可用。重启补发布失败会持久化失败状态，后续查询不被旧成功收据复活。`test_task_shared_dataset_overwrite.py` 覆盖上述路径。

### C：跨任务消费与历史边界

- C1：`projects/datasets.py`、`tasks/{configuration,assets}.py` 按修订保存共享绑定。专项覆盖旧修订拒绝；实际 wheel 的第二任务在原网格不可见时完成准备、两轮训练及独立推理，读取新增 volume_speed 字段。
- C2：`create.py`、`projects/shared.py`、资产收集记录共享来源。默认派生保持共享引用，显式复制获得独立完整副本；归档生产者保留共享数据。`test_task_shared_datasets.py` 与既有资产/管理回归覆盖。
- C3：同项目和跨项目显式引用都解析同名当前内容；新准备读取覆盖后的新数组。旧配置保持原字节；实际 wheel 用例额外核对旧准备、真实检查点和推理索引字节不变。`artifacts.py`、`projects/datasets.py` 与 `versions/compare.py` 保持历史内容身份，不凭同名判为相同。

### D：平台联动

- D1：Server rawprep 透传覆盖许可，409 名称冲突映射中文；Web 复用覆盖对话框，取消不提交、确认只授权单次，提交时遇到新冲突可重新确认。`shared-datasets.spec.ts` 与 HTTP 原始处理回归通过。
- D2：`modules/datasets/registry.py` 聚合项目共享与旧登记；相同来源去重，不同项目同名可区分。`test_web_processed_datasets.py` 验证离线发布后补登记、倒序、去重和跨项目身份；页面不自动选择最新。
- D3：stages、trace_source 与原有受控文件访问读取共享清单。7999/5172 实际页面浏览 shapenet_car4、展开 train/param1；真实消费任务生成 TorchVista 并加载可见 SVG。HTTP 真实 rawprep→trainprep 用例同时校验下载、预览及物理数据读回。
- D4：`tasks/query.py` 区分共享可用与本任务原始处理成功，Server 查询只消费 Task 发布事实。平台项目任务、阶段状态及共享专项验证不伪造原始处理运行。

### E：指定项目迁移

- E1：`projects/dataset_migration.py` 只选择正式成功 rawprep，排除试跑；预览不创建迁移副本。迁移专项与真实 migration-plan.json 记录候选。
- E2：复制完整物理成员、网格、实体身份和外部统计，只修改副本清单路径。逐文件 SHA256 报告及 Python audit 隔离的双任务验证副本独立可消费。
- E3：迁移中断使资源不可用；同名须显式覆盖；副本损坏不能被误判为幂等成功。迁移专项覆盖这些错误路径；真实 migration-repeat.json 再次完整核验后返回 already_migrated。

### F：扩展、安装与治理

- F1：`test_task_shared_dataset_installation.py` 构建实际 wheel，在仓库外复制 field_mapping、调整参数和插入字段能力；另一任务通过共享数据准备、训练及推理。自由连接与五例等价回归另行覆盖原契约。
- F2：更新 AGENTS、Task/Recipe/Server/Web/context 规则、唯一架构、模块索引及对应 PRD；修正所有权和同名覆盖的现行说明。历史验收产物、lessons 与固定源码摘要不改。文档、公开 API 基线与安装回归圈定验证。

## 指定项目与实跑证据

项目目录：`/Users/zonghui/work/project_simulation/dojo_train/platform/projects/f644f908bfde4eb4a5bea65ad97e457a`。平台项目 ID 为 `7142b2dc062e4808a1686795076b8028`，不等于目录名。

来源任务 `9c1dac251856411d9091d8d1cc60bc3e`，正式运行 `50b04c2d16de4d25b9603eceba7d2790`。共享名称 shapenet_car4，共 889 样本（789 train、100 test）。新清单为 `shared/datasets/shapenet_car4/content/manifest.json`。

证据目录：[task-shared-datasets-results](task-shared-datasets-results/)。

- `baseline-status.txt`：实施前已有的未提交改动，未清理或回退。
- `migration-plan.json`、`migration-result.json`、`shapenet_car4-file-checksums.json`：原目录 9,780 文件不变，9,779 非清单成员逐文件 SHA256 一致，新清单修正路径并复制外部统计。
- `migration-repeat.json`、`migration-repeat.log`：最终副本再次完整校验，重复迁移复用，不重复复制。
- `real-two-consumers.json`、`isolated-consumption.log`：两任务 `f540a1f563f8419ba2adf8dbe47e1cb4` / `e0086a31a4b04da0a466c295c44d6cd6` 分别准备、CPU 单轮短训和独立推理。每任务 1 train + 1 test、AB-UPT dim=24；原始网格不可用，并通过 audit hook 禁止访问旧生产任务 data。
- `browser-artifacts/model-inspection-正式模型检查操作到沙箱图形渲染/real-torchvista.png`：最终真实结构跟踪页面。
- `installed-snapshot.json`、`final-source-check.json`：独立验收 wheel 的内容摘要、安装位置及最终源码核对；同期工作区的配置合成变更使用补充 wheel 验证。测试清单见 `test-scope.json`。

早期调试失败、未通过的中间回归均保留日志，不当作最终通过证据。成功与失败的验证任务不删除历史运行记录。

## 最终圈定结果

- Task、平台、公开 API、文档主回归：`accepted-isolated-final.log`，146 passed、2 skipped。
- 安装：`accepted-final-installation.log`，2 passed；补充真实历史文件不变断言后的 `accepted-frozen-installation.log`，1 passed（同一安装用例复跑，不重复累计）。
- 迁移错误及共享派生边界：`accepted-boundaries.log`，6 passed（其中 1 项为新增迁移失败用例，其余是已圈定用例复跑）。
- 最后文档及平台登记：`accepted-final-documents-registry.log`，25 passed（复跑）。
- 数据/模型回归：`accepted-final-data-model.log`，130 passed；含五例显式流程等价、物理清单、准备/归一化、恢复、独立推理/后处理及复制扩展。
- 同期配置联动：`accepted-configuration-link-final.log`，22 passed、1 deselected；排除项是该专题自己的五例大数据验收，不冒充本轮执行。配置合成最终补丁保留扩展参数。
- PDE 边界：`accepted-pde-boundary.log`，6 passed；五个生成器独立生产和数值读回未被共享规则适配。
- 机器可读汇总见 `final-results.json`；补充复跑不重复累计通过数。
- 页面：`accepted-final-browser.log`，19 passed、2 skipped，含真实共享浏览与模型结构跟踪。
- Web 构建、架构检查、契约生成：`web-build-final.log`、`web-architecture-final.log`、`contracts-final.log`，均成功。
- 本次 Python 文件静态检查与格式检查：`ruff-final.log`、`format-check.log`，通过。全工作区 diff-check 中其余模块既有文档尾部空行未擅自改写，见 `diff-check.log`。

运行方式：Python 使用 `uv run pytest`；为避免其他会话重装影响，本轮最终使用 `uv run --no-sync /tmp/dojo-shared-final-env/bin/python -m pytest <test-scope.json 中圈定文件> -q --tb=short`。安装专项自身创建新环境并安装实际 wheel；配置联动补充用独立 link 环境。浏览器使用 `DOJO_WEB_URL=http://127.0.0.1:5172`，指定上面的平台项目 ID 和真实消费任务 ID，运行清单中的五个 Playwright 文件；输出单独保存，避免其他浏览器用例覆盖证据。Agent 仅重启自己的 7999 测试后端，未操作正式 8000/5173。

## 验证边界

Python 和浏览器各跳过的两项是未启用专门环境的真实 AB-UPT/NASA 换模用例，不计通过；已完成本次共享来源的真实 TorchVista 验证。889 样本迁移涵盖完整文件，但训练只用小模型与短预算证明工程交接，不表示生产精度，也未进行 GPU 完整训练。覆盖不保留旧物理修订，历史准备/检查点仍可能按原冻结契约拒绝继续消费；这不会触发自动重算或改写历史任务。

## 既有平台登记追加迁移（2026-09-16）

用户截图中的旧登记 shapenet_car、shapenet_car2、shapenet_car3 已按各自实际指向的正式运行迁入项目 `4753032f34914c339c311ea02cd4bcb5` 的 shared/datasets，对应平台项目 ID `34f74688805f4d4e815885da04a081d2`（名称 abc）。原登记名称和运行冻结配置名存在不一致，因此使用新增可选 sources 参数明确配对，没有用最新同名运行替换用户选中的历史内容。

- shapenet_car：来源 a911df4e0eaa4498b5a0492f64b2c443，1 样本，8 个非清单文件 SHA256 一致。
- shapenet_car2：来源 5c33894b8ef644be897ea6c16477ca1d，889 样本，7,112 个非清单文件 SHA256 一致。
- shapenet_car3：来源 407ffce3b4154938bdaad9b2bfa5d54b，889 样本，7,112 个非清单文件 SHA256 一致。

三份原目录全文件校验未变；新副本修正清单路径并复制统计依赖。每份共享清单均在 audit hook 禁止旧任务数据访问的条件下读取非空分片的首个真实样本，字段形状记录在报告中。再执行精确迁移全部返回 already_migrated。只复制和读回，没有重新处理原始数据或启动训练。

正式 8000 的公开 datasets 查询已核验：平台当前五项数据均带 shared_asset_id 且 available；已迁移的旧平台登记按来源去重隐藏，两个项目的同名 shapenet_car 分别保留。原有 shapenet_car（889 样本）和 shapenet_car4（889 样本）早已位于另一项目 shared，本次未覆盖。截图的 50b04c2d/manifest.json 是 shapenet_car4 的历史运行入口，历史文件仍保留。

证据：`registered-migration-plan.json`、`registered-migration-result.json`、`*-registered-checksums.json`、`registered-migration-repeat.json`、`registered-migration-platform.json` 与 `registered-migration.log`，均位于本专项 results 目录。

代码改动限 Task 迁移公开操作增加可选 sources 映射；未提供时维持原行为，显式空映射不迁移，非法/试跑来源整体拒绝。AGENTS、README、项目 PRD、模块与根索引同步。`uv run pytest tests/integration/test_task_shared_dataset_migration.py -q`：3 passed；圈定共享、文档和平台登记回归 24 passed（`registered-migration-tests.log`、`registered-migration-regression.log`），本次修改文件 ruff 检查通过。
