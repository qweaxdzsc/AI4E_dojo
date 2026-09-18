# 后处理工作台验收（2026-09-15）

现行后处理只展示「结果文件 / 三维物理场可视化」，默认结果文件；旧 `tab=metrics` 落到结果文件。指标表与图表在推理页，后处理不再设指标页签。2026-09-18：三维页相对原 820px 至少加高 40%（阶段窗口 ≥1148px）并尽量铺满剩余视口，宿主去掉「打开已保存配置」下拉；重开配置仍走工作台文件菜单。正式 5173→8000 对照任务「测试0918」三维页实测阶段 1148px、iframe 1086px、无宿主下拉。证据 `official-20260918-post-vis-taller.png`。圈定 `e2e/post-session.spec.ts`。下文 2026-09-15 至 09-17 的三页签证据按当时范围保留。长期功能正文见 Web、core abilities/applications、task tasks/storage 和 server modules 的现行 PRD；本文只记录验收范围及证据。

## 布局交互

- 默认指标页；批次、样本和物理量筛选属于指标页，结果文件默认覆盖任务全部批次。
- 结果文件使用共享树形表和可拖动的左右预览区；原始处理产物树使用同一组件。窄容器保留列宽并横向滚动，操作不被裁掉。
- 历史 `PostWorkspace` 保留原调用签名，转入统一三页签，不再显示独立图表导航。
- `post-workspace.spec.ts` 在1440/1920验证现行两个Tab、选择互不干扰；`post-session.spec.ts` 验证三维页至少 1148px、宿主无「打开已保存配置」、iframe 贴合且整页不锁死滚动。文件与会话浏览器测试另行验证。原始处理三条回归与预览弹窗一条通过。

## 指标计算与导出

- 固定结果逐样本加载，core计算相对L2、RMSE、MSE、MAE、R²。向量分量与模长分开；零真值范数、恒定真值返回不可定义原因，非有限值/错误实体/修订变化不能冒充成功。
- 缺旧指标记录时，隔离进程使用FakeTensorMode读张量头部确认分量，存储为meta、不载入场数组。缺真值或无有效声明保留文件浏览并显示不能评价的原因。
- 评价请求具有固定来源修订、指标配置和算法版本；新增评价运行由RunWriter记录，数据和CSV/JSON在任务 `data/post/<评价ID>`，没有新增任务版本或覆盖旧推理结果。
- 独立进程实测两批次×两checkpoint×两样本的8行评价；解析数组逐项核验五项指标，部分失败、取消保留已提交行、幂等及输入哈希不变通过。
- CSV/JSON支持选中行与全部结果；页面搜索导出传完整匹配行身份，表格分页不决定导出范围。
- 真实CFD八份固定结果直接接口计算五项指标成功。示例3586实体压力场：MSE=2200.62468431049，RMSE=46.91081628271341，MAE=31.620842017268693，相对L2=0.7465849411457621，R²=-0.06960770971958063。这是已有短训模型的结果消费验收，不是生产模型精度声明。

## 文件预览与追加

- 文件来自推理清单、已提交样本及受控历史运行目录，名称相同的文件保留独立来源/修订身份。损坏批次、失效成员及登记期间变化的文件单独报错，其他分支仍可用。
- 浏览器已验证文本预览、真实CFD网格紧凑预览、单个/批量加入以及目录搜索保留祖先。预览只创建单文件视口，不添加主工作台对象。
- Server核对可信来源、成员和修订；重复追加不复制对象。Vis按整个来源请求暂存装配，成功后提交；失败保持原场景。原来源绑定回归包含异项目拒绝、追加与重复请求。

## 三维会话保持

- iframe按稳定任务身份创建，只有拿到会话地址后才渲染；Tab可见性不参与会话重建。首次访问懒加载，离开页面/切换任务关闭；显式打开配置先关闭再按新session_id替换iframe文档。否则仅hash地址变化可能让旧React文档将新上下文与旧会话ID拼接；新增同页hash重开与满员重试回归覆盖此问题。已可见时重复通知不派发 resize；轨道回写不重读网格。连点切面只留一份未应用草稿。对象树显隐只改已有 actor。
- 真实浏览器连续十次切换三个Tab，原会话ID、iframe地址、相机和处理管线不变。
- 真实浏览器检查内层Trame高度超过外层iframe的90%且大于600px，防止仅canvas可见却把工作台裁成150px。嵌入页面使用iframe视口高度跨过自动高度包装层。
- 新建切面并将未应用原点X设为0.125；切Tab、追加第二结果及隐藏一轮30秒心跳后仍保留草稿。
- 保存前明确丢弃草稿，输入资产名称保存；通过菜单重新打开，来源、管线和视图逐项一致。页面退出后旧会话心跳返回失效状态。
- 两个真实工作进程的隔离、非法配置不替换旧画面、隐藏/返回以及心跳延长回收时间通过。回收阈值用时间戳推进模拟验证；未将30秒隐藏实测称为真实等待15分钟。
- 本期仍只保留Tab内会话。刷新或离开页面后的恢复依靠显式保存配置，不新增自动保存草稿。

## 圈定执行

后端28项通过（含实际安装副本外部调用、独立评价及CSV导出）：

```bash
uv run --no-sync pytest tests/integration/test_post_result_metrics.py tests/integration/test_task_post_metrics.py tests/integration/test_task_post_results.py tests/integration/test_web_post_metrics.py tests/integration/test_web_post_results.py tests/integration/test_post_installation.py tests/integration/test_web_inference.py tests/integration/test_viz_host_bindings.py -q
```

Vis真实双会话1项通过：

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules/test_phys_session.py -q
```

`--import-mode=importlib` 避免pytest把Vis包根加入子进程搜索路径后，其历史 `inspect/` 目录遮蔽Python标准库。普通pytest导入模式的失败不是会话计算成功证据。

Web9项通过：

```bash
npm run --prefix packages/ai4e-web test:e2e -- post-workspace.spec.ts post-files.spec.ts post-session.spec.ts rawprep-consistency.spec.ts preview-dialog.spec.ts
```

真实CFD浏览器1项通过（实际网格、指标CSV下载、追加、草稿/相机保持、心跳及保存重开）：

```bash
DOJO_WEB_URL=http://127.0.0.1:8011 \
DOJO_POST_CONTEXT=/Users/zonghui/work/project_simulation/dojo_train/infer-acceptance/real-cfd/context.json \
DOJO_POST_EVIDENCE=/Users/zonghui/work/project_simulation/dojo_train/post-workspace-acceptance \
npm run --prefix packages/ai4e-web test:e2e -- post-real.spec.ts
```

固定推理结果与Web架构额外9项圈定回归通过：`test_infer_results.py`、`test_web_architecture.py`。

前端构建、微领域边界检查、圈定Python静态检查单独通过，不代替以上计算与浏览器结果。OpenAPI类型已重新生成。原Vite组件挂载测试需要5173开发服务，不能在8011静态构建服务上请求 `/node_modules/.vite/`。

实际wheel重新构建安装core/task/server/viz；安装验收子进程从仓库外调用task公开提交/查询/导出，检查加载位置为site-packages，数据在目标任务，外部工作目录未出现输出。未用import成功代替工作进程验收。

## 证据与使用入口

证据根目录：`/Users/zonghui/work/project_simulation/dojo_train/post-workspace-acceptance/`。

- `real-metrics.json`：真实8份结果的五项指标。
- `metrics.csv`：浏览器实际下载。
- `metrics-1920.png`、`files-1440.png`、`files-1920.png`、`trame-1440.png`：真实布局和网格截图。
- `session-evidence.json`：切换前后及追加的场景快照与浏览器错误记录。
- `save-reopen.json`：保存名称及重开会话快照。
- `services.json`、`live-server.log`、`verification-server.log`：本机服务参数与运行记录。
- `live-route.json`、`live-browser.json`、`live-post-1440.png`：现有5173日常任务页面及三个Tab实测。
- `final-evidence/`：28项圈定后端用例的实际夹具与输出。
- `visibility-final/`：真实双会话夹具。

日常入口继续为 `http://127.0.0.1:5173` 的项目→任务工作台→后处理；8000服务已更新，保留原平台目录与三个数据根。原abc任务若没有推理结果显示空态，不填演示数据。真实CFD验证项目独立放在8011服务，以免向日常项目添加验收数据。

未扩大声明：此次没有重测Linux阴影、生产规模CFD精度或整仓功能；这些不属于本次后处理页面改动。已验证的旧功能只按圈定回归范围记录。

## 参考图 UI 优化复验（2026-09-15）

本轮以用户提供的 `docs/任务工作台-后处理-指标.png`、`docs/任务工作台-后处理-结果文件.png` 为布局参考，保留已确认的三个Tab及九步外壳，不使用图片中的示意物理量、模型版本或数值。

- 指标：内联筛选与计算/导出按钮，浅蓝状态带、38px细网格行、固定身份列宽、分页计数分布；窄容器分两行配置。切Tab关闭导出菜单，旧计算范围仍明确保留。
- 文件：40/60可调分区，文件标题右侧批量加入；勾选独立成列，目录图标与缩进统一。窄容器优先保留文件名和操作，次要时间/大小列按宽度隐藏。
- 预览：紧凑着色控件、加宽字段菜单、全高度真实网格、底部放大及下载。修复中间包装层使画布只占260px的问题。
- 主工作台：保持原Trame和稳定会话，没有新增外围物理控件。

本轮实际执行：

```bash
npm run --prefix packages/ai4e-web test:e2e -- post-ui.spec.ts post-files.spec.ts post-session.spec.ts post-workspace.spec.ts rawprep-consistency.spec.ts
```

10项通过，含1440/1920布局、表格行高、左右比例、勾选列对齐、浮层隐藏、预览放大、会话保持和原始处理回归。`test_web_design_documents.py` 12项通过；Web构建及微领域检查通过，构建仍有既有大bundle提示。

真实CFD `post-real.spec.ts` 1项通过（59.5秒）：读取已有两批次/两checkpoint/两样本目录，真实指标CSV下载、pressure预测着色、画布占预览高度65%以上、追加两个结果、十次Tab切换、草稿及相机保持、隐藏心跳、显式保存重开、退出回收均通过。内层Trame高度超过外层90%且大于600px。浏览器未记录页面错误。

复验期间发现运行环境缺少已在workbench依赖组声明的pandas等依赖，新会话报 `phys_worker_start_failed`。使用 `uv sync --group visualization --inexact` 恢复依赖，重新安装Vis当前副本后完成上述真实验收；服务运行/验收应保留visualization组，不能用不含该组的同步覆盖运行环境。

证据目录：`/Users/zonghui/work/project_simulation/dojo_train/post-ui-refinement/`。

- `metrics-1920.png`、`files-1440.png`、`files-1920.png`、`trame-1440.png`：当前构建的真实结果截图，已人工查看。
- `metrics.csv`、`session-evidence.json`、`save-reopen.json`：实际下载及会话前后证据。
- `live-post-1440.png`、`live-browser.json`：日常5173页面三个Tab及接口复查，空任务保持真实空态。

本轮只优化页面布局和相关交互，没有重算算法定义，没有扩展Linux阴影或生产精度验收；不声明与参考图逐像素一致。

## 结果文件纳入训练数据产物（2026-09-17）

产品要求结果文件不只消费推理批次。`list_post_result_files` 同时列出训练运行文件夹（「训练运行 ·」加 run 短号）和未挂批次的独立推理；有写出时按层展开任务 `data_dir` 的 `infer` / `post` / `predictions` / `meshes` / `analysis` / `exports`。无写出仍保留该 run 并说明没有预测或网格，失败开训不冒充有结果。评价指标目录仍只解析已提交清单；无清单的训练产物只出现在结果文件。检查点、日志、`rawprep` / `trainprep` 准备副本不进入此树。完全没有训练运行和推理结果时说明「暂无训练运行或推理固定结果」。

圈定 `tests/integration/test_task_post_results.py`、`tests/integration/test_web_post_results.py`、`packages/ai4e-web/e2e/post-files.spec.ts`。训练设置另提供写出预测/网格/分片，默认关闭；打开并成功结束后才会在该训练 `data_dir/infer/` 出现场文件。

正式 8000/5173 冒烟（2026-09-17 19:41–20:05，用户当次授权）：已按规定重装 `ai4e-core`/`ai4e-task`/`ai4e-server` 并重启 8000（Python PID **99745**）。安装 `post_results.py` `da1a1dca01a182fd`。首页任务成功训练 `3a5933a4c48c4a3ea3ad501800b3157d` 仍无场文件；`GET …/post/results?view=files` 返回 0 条。5173 结果文件页「共 0 个文件」，空态为「暂无推理固定结果或训练运行写出的预测、网格、导出文件」，未列出检查点/日志/准备目录。训练设置「训练结束写出」：写出预测关、写出网格禁用、分片测试集，`evaluation_enabled` 值仍为 false。证据：`/Users/zonghui/work/project_simulation/dojo_train/post-workspace-acceptance/official-20260917-2002-training-export.png`、`official-20260917-2003-post-files.png`、同目录复制的 `official-20260917-2005-smoke.json`。未开写出重训，故无训练场文件进入结果树。

训练 run 必须可见（2026-09-17 续）：上一版只列有写出产物的训练 run，关写出开关或失败开训会整段消失。现改为始终列出「训练运行 ·」加 run 短号；有预测/网格按层展开，没有则说明空态，失败开训写「开训失败」不冒充有结果。正式 5173（22:53，8000 未重装）结果文件页已见本任务五条训练 run：`e14ce795`、`7fe91b30`、`e9fbb4be`、`cc0a4fe2`、`7f80018e`，以及「批量推理 · f0213b8b」。展开成功且关写出的 `e14ce795` 为「没有写出预测或网格」；失败 `7fe91b30` 为「没有预测或网格（开训失败）」。证据：`official-20260917-2253-post-files.png`、`official-20260917-2253-post-files-expand.png`、`official-20260917-2253-post-files-failed-stopped.png`。正式 `GET …/post/results?view=files` 仍只回推理批次，须重装 `ai4e-task` 并重启 8000 后接口才原生列出训练 run。

切步产物名单（2026-09-17 续）：`list_stage_artifacts` 不再在列举时整文件核验检查点；正式入口此前 `GET …/stage-inputs` 约 32 秒。须重装 `ai4e-task` 并重启 8000 后再核耗时。相机联动源码已放宽，正式须另重装 `ai4e-viz` 并换 Vis。

正式 8000/5173 冒烟（2026-09-17 20:46–20:54，用户当次授权重装重启）：`uv sync --group dev --group visualization --reinstall-package ai4e-task --reinstall-package ai4e-viz` 后正式 8000 PID **6975**、Vis **7457** 端口 50759，5173 仍为 **23629**。安装 `artifacts.py` `1c61e2a540e15862`、`scene.py` `bf008c274581c4df` 与源码一致。`GET …/stage-inputs` 21 条 **0.18s / 0.13s**。训练设置页约 1.56s 见到写出开关。后处理结果文件「批量推理 · 0bdc98ce」下可见 100 个 `full_surface.vtp`。三维页新会话 `fc293cff…` 建 RenderView2 后打开相机联动，无共同坐标空间报错。证据：`/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/official-20260917-2054-smoke.json`。未新跑 887 样本，张量日志降级本轮未验证。

## 批次身份与指标聚合口径（2026-09-17）

后处理批次下拉不再只显示「批量推理」：有 `created_at` 时格式化为 `infer-YYYYMMDD-HHMMSS`（本地墙钟，精确到秒）；自定义名称保留。指标页标题、状态、空态和详情写明「按检查点聚合」。只改 web 源码，未改 task/server 默认名，未重装 8000。圈定 `e2e/post-workspace.spec.ts`（4 项）、`e2e/inference.spec.ts`（6 项）、`e2e/post-ui.spec.ts`（2 项）。结果文件树仍用服务端存储前缀，旧批次目录可能仍带「批量推理 · 短号」。

正式 5173 源码冒烟（2026-09-17，未重启 8000）：`http://127.0.0.1:5173/projects/32cdee6900924df096838663a4a70a05/tasks/beab7b5ab1414787b8cc6a288e6db0cc/post`。目录接口该批次仍名「批量推理」、`created_at=2026-09-17T12:57:37Z`；指标与结果文件下拉均显示 `infer-20260917-205737`，无「批量推理」。指标表标题/状态/空态含「按检查点聚合」。截图 `official-20260917-2248-metrics-batch.png`。

## 推理 VTK 与平台数据集对照（2026-09-17）

对照任务 `beab7b5ab1414787b8cc6a288e6db0cc` 已有推理批次请求 `export_vtk:false`，样本目录只有 PT/清单、没有 VTK。源码现默认写出锚点 VTK（场名 `.prediction`/`.truth`），完整网格另走查询；用户关闭导出时写入清单 `vtk.reason` 并在推理页/结果树展示。缺拓扑或点数对不上则该样本失败，清单先写原因，整批不冒充全部成功。结果文件树增加「平台数据集 ·」加名称，与训练 run、推理批次并列，样本 ID 用 `param1/<设计号>`。历史缺 VTK 批次不回写文件，须重跑推理才有网格。

圈定源码验收（2026-09-17，`PYTHONPATH` 覆盖当前包源码，未重装 `.venv`）：

- pytest：`test_web_rawprep.py`、`test_web_dataset_binding.py`、`test_web_rawprep_handoff.py`、`test_web_stage_consistency.py`、`test_trainprep_consume.py`、`test_infer_inspect_contract.py`、`test_web_post_results.py`、`test_task_post_results.py`、`test_post_mesh.py`、`test_infer_vtk_identity.py`，**133 passed / 2 skipped**。
- 其中 `test_missing_raw_surface_rejects` 曾因历史锚点路径把缺表面网格记成跳过且整次成功而失败；`infer/anchor_stage.py` 记下原因后重新抛出，该项已过。
- e2e：`rawprep-consistency.spec.ts`、`model-picker.spec.ts`、`post-files.spec.ts`、`post-workspace.spec.ts`、`inference.spec.ts`，**29 passed**。

正式 5173→8000 冒烟（2026-09-17 23:44–23:50，用户当次授权）：`uv sync --group dev --group visualization --reinstall-package ai4e-core --reinstall-package ai4e-server --reinstall-package ai4e-contrib --reinstall-package ai4e-task` 后只重启正式 8000。入口 `http://127.0.0.1:5173` → `http://127.0.0.1:8000`，对照任务 `32cdee6900924df096838663a4a70a05` / `beab7b5ab1414787b8cc6a288e6db0cc`。新 8000 PID **33633**，5173 仍为 **23629**。安装摘要与源码一致：`post_results.py` `7bec3f2c920c9ed6`，`anchor_stage.py` `015db74cdd7e07a8`，`vtk_export.py` `0409d8eb6b1c6e46`，`inspection.py` `837e06583d49a50a`。

逐页：

- 原始处理「全部」：处理样本 **889**（来自绑定数据集），来源文件 1778，`sample_universe=bound_dataset`。
- 数据准备处理结果：可见 `normalize` 与 `preparation.json`，展开含 train/test 归一化副本。
- 模型设置：已保存参数 192/6/3 与几何 3586 先出；`model-options` 0.107s；正式检查 `b8462e49` 约 6s 成功，无点数冲突。
- 推理：红条「当前模型权重结构与检查点 effective_config 不兼容」；导出网格默认勾选。未新跑推理。
- 后处理：指标下拉 `infer-20260917-205737`，文案「按检查点聚合」。结果文件并列「平台数据集 · shapenet_car2」「平台数据集 · training_execution_real_cfd」、五条「训练运行 ·」与历史「批量推理 · f0213b8b」。平台数据集展开样本 `param1/<设计号>`。历史推理样本见「未写出VTK：该次推理未导出网格」。

新默认网格未验证：现有检查点与当前大结构不对，未提交新推理；历史关网格批次不回写。步骤条把训练运行显示成成功、标题写「流程已完成」，与已知 last-rowid 诊断一致，本轮不改。

证据：`/Users/zonghui/work/project_simulation/dojo_train/post-workspace-acceptance/official-20260917-2348/`（`official-smoke.json`、`api-smoke.json`、`model-check.json` 与五页截图）。

复测（2026-09-18 00:22–00:28）：安装副本仍与源码一致，8000 仍为 PID **33633**，未再重装或重启。接口 catalog 889 / `bound_dataset`，准备文件 `normalize`+`preparation.json`，推理样本仍报权重结构不兼容，结果树仍列平台数据集、五条训练运行、历史推理批次及「未写出VTK」。页面再点：原始处理 889、准备处理结果、模型「配置与交接检查通过」（3586 点数未挡）、推理红条、后处理三根与跳过说明、指标「按检查点聚合」。证据 `official-20260918-0022/`。

原始处理 VTKHDF 默认勾选（2026-09-18）：对照任务当时保存为关，已写回 `rawprep.vtkhdf: true`；页面缺键按清单/案例默认勾选。正式 `5173` 原始处理页复测 VTKHDF 已勾选，8000 仍为 PID **33633**，未重装或重启。圈定 `e2e/rawprep-consistency.spec.ts` 7 passed。证据 `official-20260918-vtkhdf/`。

## 隐藏后处理指标页签（2026-09-18）

推理页已有指标表格/图表，后处理不再展示重复的「指标」页签。

- UI：`PostResultsWorkspace` 只留结果文件、三维物理场可视化；默认结果文件。`PostMetricsPanel` 与评价 API 保留，不作为页签渲染。
- 深链接：`tab=metrics` 或未知 tab 落到结果文件，不空白、不报错；`tab=visualization` 仍进三维。
- 圈定：`packages/ai4e-web/e2e/post-workspace.spec.ts`、`post-files.spec.ts`、`post-ui.spec.ts`、`post-session.spec.ts`；回归 `tests/integration/test_task_post_results.py`、`test_web_post_results.py`。评价接口用例不改。
- 只改 web 源码，正式 5173 读源码即可冒烟，未重装/重启 8000。
- 正式 5173→8000 冒烟（2026-09-18）：任务 `测试0918`（`179ed1fe447b415b8870c45b6a89a296` / `f8f89f8037b34026ae778116f441a3f6`）。默认只有结果文件与三维，无指标页签/计算按钮；切到三维再切回仍是两页签；`?tab=metrics` 落到结果文件；推理深链接 `batch=726c91ae…&run=fd7da8f3…&sample=param0/100715345ee54d7ae38b52b4ee9d36a3` 仍定位固定来源。推理页指标区与表格仍在。证据 `/Users/zonghui/work/project_simulation/dojo_train/post-workspace-acceptance/official-20260918-hide-metrics/`。

## 正式后处理与 VTK 一致性冒烟（2026-09-18，用户授权）

- 正式 API 8000 已按规则重装相关 force-include 包并重启为 PID **34563**；5173 保持用户进程。
- 后处理结果文件页只显示一个训练绑定平台数据集：`平台数据集 · shapenet_car4`，并列训练运行 `08bbe33e` 与推理批次 `infer-20260918-132824 · c9a60689`；没有“固定结果文件与后处理交接”容器。
- 三维物理场工作台在正式页面成功建立 Vis/Trame 会话；外层容器高度已调整为约 714px。当前未选择具体文件时显示 0 点/0 单元属于空选择状态，不是 Vis 启动失败。
- 真实 `surface.vtp`（3586 点、3584 单元）含 `surface.pressure.prediction`、`surface.pressure.truth` 两个独立字段；通过原始点 ID 对齐后两字段分别与对应 PT 完全一致，prediction/truth 最大差值 104.5523529。此前“云图一样”的原因不是 prediction 未写入，而是查看时没有选中具体结果资产/字段，或使用了未按字段身份切换的显示状态。
- 数值、资产修订、字段和 manifest filemap 证据：`/Users/zonghui/work/project_simulation/dojo_train/formal-20260918-consistency/vtk-identity.json`。
- 后续健康检查返回 `{"status":"ok"}`；正式服务当前 PID 为 **48179**，发布冒烟时 PID **34563** 的证据仍对应同一正式 root 和入口。
