# Recipe / Task 统一约定实施验收

状态：实施中，尚未达到全计划验收。2026-09-17用户授权后，正式8000已成套重装并重启；首页任务各工作台步骤已转到公共 `inputs.*`、现行官方脚本与 version=2 准备。其余正式任务原件与完整计划项未收口。历史专项的成功不代替本轮公共配置迁移验收。

## 授权与边界

2026-09-17用户批准实施：统一公共配置与脚本约定，取消逐案例task-entry，Task管理缺失约定时局部功能不可用，保留自由脚本。Python决定流程，YAML选择范围和参数；算法留在ability/application。正式发布遵守当次批准门槛。

代码起点为 `recipe-task-conventions-results/baseline.json`，记录2362个文件摘要及初始脏工作区。不得重置或把其他会话已有模型、平台、Vis修改算作本轮新增。WDNO现有迁移成果保留；真实研究账本不重置。

## 已实现的公共交接

- 普通pipeline/config自动发现，inputs按阶段捕获；run_root/data_root分离。移除运行时task-entry读取和旧操作回填。缺领域连接只使该操作不可用。
- writer公开资产/指标索引；候选核验文件与全部依赖，指标来源改变不可比。进程成功、研究完成和科学结论分开。
- GenCP、PDE、控制、外流及已有WDNO接入新输入树；PDE infer与固定post拆分；复制扩展使用公开数据输出目录。领域专属正文保留。
- Task共享物理数据覆盖保留本次回退副本，失败恢复旧内容/来源；数据链接按内容核验，代码快照仍拒绝链接。
- 离线迁移事务保留原件/候选/日志，拒绝源码漂移，注入目录切换故障后能恢复。旧迁移公开入口必须提供原件摘要，不能凭导入或函数名覆盖代码。
- 批量推理检查通过贡献应用解释公共配置；固定检查点比较区分缺省null与科学声明。启动早期停止仅在持有真实子进程并核实SIGTERM退出时补停止收据，未知PID仍不能伪造终态。

## 真实计算与安装证据

产物根：`/Users/zonghui/work/project_simulation/dojo_train/recipe_task_conventions/`。当前测试进程通过 `/tmp/dojo-recipe-conventions-imports` 读源码，该方式不是安装验收。

- `gencp-final-source-v2/report.json`：六组全部通过直接脚本/Task的rawprep、独立准备、每场2次更新→固定总目标3次的恢复、单场生成、耦合生成和固定post；权重/优化器/调度/EMA/游标及预测数组逐值对照。单组本次149–207秒，报告seconds含此前记录的重试；工程短训练，不是论文精度。
- `nasa-final-source/report.json`：已随机选定NASA CRM/AB-UPT，真实两训练/两评价样本，完整处理/准备/2轮训练/1→2恢复/全点infer/post双入口通过，本次117.484秒；全部具名预测和分量指标读回比较。`nasa-budget.json` 已收拢8次尝试；7份报告实测合计465.43秒，第五次缺结束报告，保守按首尝试目录创建到最终成功报告的整段4833.71秒计账（含调试闲置，不冒充实测计算），剩余5966.29秒。
- `test_gencp_installation.py` 与固定公开基线实际构建wheel、安装到隔离目标、仓库外复制运行；条件替换、单场权重替换、速度派生保存/读回/消费及无权重post通过。与两个平台边界用例合计8 passed，日志 `logs/dojo-install-continued.log`。固定用户源码与摘要未改。
- PDE真实小数据生成/训练/推理后隐藏检查点的独立post通过。SafeDiffCon隔离参考环境小网络Task闭环本轮再次1 passed（19.29秒）；主环境缺其依赖，不安装主环境。
- WDNO在既有隔离环境回归17 passed、2 skipped、1停止竞态失败；修复Task后该失败项1 passed（0.54秒）。仅测试夹具，未重训原研究数据。跳过项不计为通过。

报告副本在 `recipe-task-conventions-results/`；选定日志在其 `logs/`。六组原失败记录保留：一次验证工具漏传配置修订号，中止后把已消耗时间计入重试账本，不能隐去。

## 管理、平台与迁移进度

- 公共边界/迁移/任务契约合计30项圈定测试通过；离线切换故障、应用前后漂移保护均覆盖。前一轮共享15项、任务管理16项通过，仍需最终受影响集合重跑。
- 平台原三个剩余用例3 passed。后续配置交接/数据绑定等38 passed、1 skipped、2失败，其中缺领域操作按新边界明确不可用、测试旧输入断言已修正；修正用例经安装组合测试通过。
- 浏览器配置合成/换模/阶段夹具初跑13 passed、8失败；公共绑定迁移后阶段11 passed、1失败，最后检查点绑定修正后该项1 passed。前端build通过。以上是隔离5172及明确接口夹具，不代表正式服务和完整安装平台验收。
- `migration-rehearsal/report.json`：九个实际历史任务仅复制recipe后演练；配置检查与逐字节回滚全部通过，保留审计钩子前缀与原训练观察选择。尚未逐个实跑迁移后的训练/恢复，不能称全部任务已经迁移。候选指向新版准备；旧准备的重新生成边界单独列出。正式原件摘要不变。
- 批量推理冻结交接已修复：原生锚点推理消费准备中的归一化、分片和组件，不重新读统计。两检查点、跨分片、失败重试和取消实际用例2 passed（127.98秒）；独立推理选定准备不消费别的阶段遗留清单，最终补跑中。
- 保留Transolver原领域正文新增普通Task双入口测试，固定相同CPU线程后权重逐值一致、预测与独立post通过，1 passed（27.04秒）。其version=1准备仍不满足平台现行门禁，此结果不是新版平台Transolver验收。
- 五个外流案例与未改写的原数值工作流对照、恢复5 passed（96.39秒）；原锚点预测/网格/随机性和训练recipe共31 passed（200.85秒）。夹具显式准备再训练、跟踪本次输出；固定公开源码及摘要不改。
- 仓库外字段/采样/自定义目标与变换扩展12 passed（79.47秒）；发现并修正残留旧输入及输出路径，纯配置转换可在会话外调用，实际执行显式绑定会话输出。
- 迁移、公共约定与基础管理25 passed；项目共享/资产16 passed；后续新依赖保护和文档29 passed。迁移CLI可prepare/inspect/apply/rollback；复制候选中途故障能逐字节回滚。
- 安装、固定公开基线、Task配置、操作提供者及平台配置/数据绑定组合76 passed、1 skipped（536.10秒），包含实际隔离wheel与HTTP TestClient。跳过不计通过；这是源码迭代期间结果，最新补改后的GenCP安装与推理回归另记，仍不代表真实浏览器或正式服务发布。


## 本次续接完成的验收（2026-09-17）

- Transolver 逐样本物理准备增加独立身份的 version=2，冻结归一化、输入来源、准备函数和分片；保留 Python v1恢复，平台不把v1直接升级。五案例原工作流/恢复及 Transolver 双入口/真实批量推理共7项通过，后续显式失效输入保护组合18项通过；预测、恢复参数逐值一致。平台结构消费回归4项通过。
- 自动官方包装迁移改为按当前数据集、模型和变体选择案例；文件替换失败恢复原件。迁移/配置22项通过；旧预测post拆分转换保留参数与固定权重，专门转换测试9项通过。同次训练的last/latest由上游交接；独立权重标签须明确固定文件，不能当成路径。
- 数组发布者可声明自包含目录；公共共享和fork完整复制目录与依赖，科学文件不重写。真实Task产生数组→共享→新任务→fork→删除原目录后读回通过，项目移动与篡改拒绝也通过；泛用未声明外部依赖仍明确拒绝复制。管理层不解释领域数组格式。
- SafeDiffCon Task闭环6项通过；WDNO公共配置与Task18项通过、2项环境跳过；均为交接夹具，不重训历史研究基线。控制指标与GenCP真值身份登记按固定真值、样本、物理帧比较，不因预测值变化误判不可比。
- 公共索引/共享与文档25项通过；最后发现的旧共享迁移和固定后处理消费者改用现行入口，15项通过。历史物理数据迁移测试仍执行实际本地产物生成，不能通过恢复读取task-entry让用例通过。
- 平台配置/交接60项通过、1项环境跳过；隔离5172浏览器配置合成、阶段状态和日志18项通过。这是浏览器夹具与HTTP TestClient证据，仍不冒充最终安装版正式全链路。
- 九个历史任务副本全部完成真实原数据小样本准备、两轮训练、第一轮→第二轮恢复、预测和独立post。原生及逐样本物理流程分别保留；仅验收副本缩小网络/样本。全部权重、优化器、EMA、调度、随机状态及训练合同逐值一致，配置中的运行位置/恢复引用另记。原有隔离审计钩子保留。证据 `migration-execution-v3.json`、`migration-resume-state-v3.json`。最初演练错误使用未支持的检查点标签，9次失败原样计入 `migration-execution-failed-v2.json`；随后使用公开namespace保存中间状态，未改科学算法。
- 最后一次实际wheel/固定公开用户基线/Task仓外字段扩展/GenCP扩展组合7项通过（31.52秒），未修改固定基线摘要；选定修改范围ruff通过。日志 `dojo-public-install-final-v3.log`、`dojo-lint-final-v4.log`。
- 已准备九份正式迁移候选及逐文件回滚包，沿用正式配置的训练预算、科学参数和已选路径；不把小样本验收配置发布。位置 `dojo_train/recipe_task_conventions/release-20260917-v2/`，状态 prepared_not_applied；此前 release-candidate 已过期。

## 尚未完成的计划项

1. 发布候选已核验源码和九任务原件无漂移，最后文档/迁移17项通过；已向用户请求当次授权。最终发布包的正式安装、受影响进程更新及 Agent 在8000/5173执行完整冒烟；需本次明确授权，前一轮其他会话的安装不等于本次最新代码已生效。隔离7999目前是早期配置合成服务，不把它当作新版。
2. 九份正式迁移候选尚未应用；应用前再次检查源码漂移，原版本/运行/检查点保持原字节。旧v1准备在Python按原合同可消费，平台继续明确要求重新准备，不通过修改版本号伪造兼容。
3. 部分任意外部依赖资产未声明自包含时只支持引用，不自动猜测或改写领域文件；这是明确支持边界，不声称所有历史清单可便携复制。

## 正式入口更新（2026-09-17）

用户授权「按照新的约定来更新」后执行，不是整体计划验收通过。

- 入口：`http://127.0.0.1:8000`（`uv run --no-sync python -m ai4e_server --root .../dojo_train/platform --port 8000`），前端 `http://127.0.0.1:5173`。
- 重装：`uv sync --group dev --group visualization --reinstall-package` spec/core/contrib/task/server。安装 `RunContext` 现含 `stage_outputs`。
- 首页任务 `9c1dac251856411d9091d8d1cc60bc3e` 先用 `convert_aero` 去掉 `dataset.root`/`paths`；随后补齐全阶段：`pipeline.stages` 为 rawprep/trainprep/train/infer/post，`inputs.train.preparation`/`inputs.infer.preparation` 指向现行 version=2 准备 `0dbf033d`，`inputs.trainprep.dataset` 绑定该准备冻结的本地清单 `50b04c2d`。不可用共享名 `shapenet_car` 不回填。脚本换成现行 `recipes/aero_cfd`（无额外顶层函数）。原件：`/Users/zonghui/work/project_simulation/dojo_train/recipe_task_conventions/official-8000-update-20260917/`。
- 平台：检查只替换核验摘要的旧包装；原始处理覆盖 `inputs.rawprep.source`；保存后任务入口跟随当前 `config.yaml`；失败且空日志展示 `run.error`。
- 冒烟见下方「全阶段更新」；未提交 889 样本正式执行，未开正式训练。

## 全阶段更新（2026-09-17）

用户要求工作台各步（原始处理、数据准备、模型设置、训练设置、训练运行、推理、后处理）都跟到现行 Recipe/Task 约定后执行。Experience 查询 `receipt_51f9592b9fc44596a45b0bd75cf95bec`、`receipt_3fdd88c3d61248b0a51968ac48632390`，无覆盖本任务的已批准技术条目。

- 平台：检查只替换核验摘要的旧包装；原始处理覆盖 `inputs.rawprep.source`；保存后入口跟随当前 `config.yaml` 并丢掉旧资产键；失败且空日志展示 `run.error`。
- 首页任务脚本换成现行 `recipes/aero_cfd`（无额外顶层函数）；`pipeline.stages` 为 rawprep/trainprep/train/infer/post；准备与推理准备指向 version=2 `0dbf033d`；数据准备绑定该准备冻结的本地清单 `50b04c2d`。原件在 `official-8000-update-20260917/all-stages-recipe/`。
- 重装：`uv sync --group dev --group visualization --reinstall-package ai4e-task --reinstall-package ai4e-server`。正式 8000 已是重装后进程（16:11 启动）；5173 读源码。
- 圈定：`test_task_configuration` / `test_task_contracts` / `test_web_dataset_binding` / `test_web_rawprep` 40 passed；`test_web_stage_consistency` + 配置交接 68 passed、3 skipped，换模身份断言已改为入口跟随当前 `components`；`e2e/execution-log.spec.ts` 3 passed。
- 正式 5173/8000 冒烟：各步 GET configuration/stage-inputs/stage-summary 200；六阶段 `mode=check` 与 `model-inspections` 200，不再出现 `migration_verified_sources_required`。页面打开原始处理、数据准备、模型设置、训练设置、训练运行、推理、后处理均无 HTTP 500。训练运行历史失败日志可见 `[ERROR] SystemExit: 1` 与「准备声明已变化」。原始处理校验仍提示同名共享 `shapenet_car` 需覆盖。推理无检查点，后处理无固定结果。未提交 889 样本执行，未开训。
- 未决：共享名 `shapenet_car` 内容仍空，原始处理同名覆盖提示仍在；现行配置与 `0dbf033d` 准备的归一化摘要不一致，开训/结构跟踪前须按现行数据准备重新生成；后处理检查仍可能报内部旧键 `post.checkpoint`；其余正式任务未迁。数据准备已选本地 `50b04c2d`，目录里空的 `shapenet_car` 不再报「已绑定来源不可用」。

## 收口复核（2026-09-17）

用户要求根据全阶段改动查剩余问题、补文档、验证并发布。Experience `receipt_236708b7230d4d748bf7c42bf753c291`、`receipt_f05d2fbb22674e5a9552bcb30617236d`，仅 Ethos 消息节奏。

- 剩余问题：数据准备把目录里空的 `shapenet_car` 当成「已绑定来源不可用」；`test_web_processed_datasets` / 整合流水线仍断言旧键；AGENTS/index/core PRD 仍写正式入口未更新或 `train.manifest` 为公开交接；`.venv` 的 task/server 落后于源码（迁移不按案例、失败不回滚）。
- 页面：`unavailableBindingItems` 只对当前失效绑定报警。`e2e/stage-consistency.spec.ts` 新增「目录里失效共享名不覆盖已选本地清单」，3 条相关 e2e 通过。
- 测试：平台数据集绑定改为 `inputs.trainprep.dataset`；整合流水线补 infer，断言改为 `inputs.*`。
- 文档：AGENTS 第 5 段与 `.context/index.md` 改为正式入口已在同日约定更新中重装；core 应用 PRD / 模块索引写明公开 `inputs.*` 与内部旧键；templates PRD 写 `recipe_entry`；recipes PRD 默认阶段含 infer；web PRD/模块索引写明空共享名不冒充已绑定。
- 圈定：`test_web_processed_datasets`、`test_task_configuration`、`test_web_stage_consistency`、`test_web_dataset_binding` 与文档测试合计 128 passed / 2 skipped；重装前 4 条迁移因安装副本落后失败，`uv sync --group dev --group visualization --reinstall-package ai4e-task --reinstall-package ai4e-server` 后 `test_official_migration_failure_restores_all_replaced_files` 与 3 条案例迁移 4 passed。`test_task_documents` 单独重跑 1 passed。
- 发布：正式 8000 已停旧进程并按原参数重启，pid 82073，16:48:34 启动；5173 仍读源码。入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`。
- 正式冒烟：六阶段 configuration / stage-inputs 200；选中本地 `50b04c2d`，空 `shapenet_car` 为未选中 invalid。5173 打开原始处理、数据准备、模型、训练设置、训练运行、推理、后处理无 HTTP 500。数据准备页已选 `50b04c2d / manifest.json`，无「已绑定来源不可用」，字段匹配与 889 样本可见；截图 `.context/mvp/recipe-task-conventions-results/official-trainprep-no-false-alarm.png`。未提交 889 样本执行，未开训。
- 检查终态（不作为页面验收通过）：rawprep check 成功；trainprep/model/train/infer/trace 报「准备归一化摘要不一致」；post 报 `post.checkpoint: 阶段 post 需要已有固定产物`。

## 正式工作区清理（2026-09-17）

用户要求只测一个项目：删除旧准备，项目只留首页一份；原数据不删；只把平台共享处理好的数据迁到新消费键。

- 保留：项目 `7142b2dc062e4808a1686795076b8028`（磁盘 `f644f908bfde4eb4a5bea65ad97e457a`）、任务 `9c1dac251856411d9091d8d1cc60bc3e`。
- 迁移：abc 可用共享 `shapenet_car`（1 样本）、`shapenet_car2`/`shapenet_car3`（各 889）复制进首页；`shapenet_car4` 只改 `consumer_binding=inputs.trainprep.dataset`。失败空共享 `shapenet_car` 被覆盖。
- 删除：首页 4 份准备运行、7 个 shared-consumer 残留任务、abc 项目目录；`server.sqlite` 注销 abc 与真实 CFD 项目行。真实 CFD 磁盘与 `/Users/zonghui/work/datasets` 未动。
- 任务配置已去掉 `inputs.train.preparation` / `inputs.infer.preparation`；`inputs.rawprep.source` 仍指向 ShapeNet 原数据。
- 正式 8000 已按原参数重启。5173 项目管理只见首页项目、任务表只见该任务；数据准备下拉为 4 个平台共享加 1 条历史任务清单 `50b04c2d / manifest.json`，无「已绑定来源不可用」。原始处理仍提示同名 `shapenet_car` 覆盖。未提交 889 处理，未开训。
- 记录：`.context/mvp/recipe-task-conventions-results/cleanup-platform-workspace.json`。
- 2026-09-17 17:56 用户授权后重装 `ai4e-core` 并重启正式 8000：安装副本 `publish_dataset` 已接受 `session`。889 样本因上次发布失败已回滚，需用户对 `shapenet_car` 覆盖后重跑原始处理。
- 2026-09-17 18:41 用户授权后重装 `ai4e-core`/`ai4e-contrib` 并重启正式 8000（pid 95113）。首页任务模型页生成中等体量 TorchVista 图：加载文案「正在生成中等体量模型结构…」可见；操作 `2f7dd819…` / `5df40292…` 成功，`graph_view=compressed_modules`，71 个模块节点（旧图 2682），约 36 秒出图。入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`。证据：`recipe-task-conventions-results/model-graph-official-smoke.json`、`model-graph-loading.png`、`model-graph-medium.png`。

## 已记录的错误和经验

案例目录不能用通用脚本整套覆盖；从来源哈希恢复了35份脚本。固定总训练预算，用执行片段验证恢复；不通过改变调度目标伪造恢复通过。公共路径迁移必须核到只读检查、冻结声明、资产比较和安装后的复制入口。详细事实和候选流程追加在 `.context/model-integration-learning.md`，不自动给通用skill增加个案限制。

## Experience

此前查询receipt `receipt_723be72e5440403786bef8b62a9f0bb0`，无本迁移相关已批准技术资产。本轮正式入口更新另查 `receipt_67d8403d93474fed9a6a47838cd96d1d`、`receipt_bca850eea5e941d69537a661783deb94`，无覆盖安装副本与 rawprep 现场的已批准技术条目。收口复核另查 `receipt_236708b7230d4d748bf7c42bf753c291`、`receipt_f05d2fbb22674e5a9552bcb30617236d`，仅 Ethos 消息节奏，无覆盖本任务的已批准技术条目。工作区清理另查 `receipt_808472f185e94f8893bd05e80c233df0`，无相关已批准条目。模型结构发布另查 `receipt_dc70a73116924986b8702084fa16d716`，无相关已批准条目。未归档会话。源码与本轮实际记录优先。
