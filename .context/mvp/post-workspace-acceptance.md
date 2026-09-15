# 后处理工作台验收（2026-09-15）

本切片实施任务级“指标 / 结果文件 / 三维物理场可视化”。保留九步平台外壳、历史推理结果和已存在工作区改动，不重新执行模型推理。长期功能正文见 Web、core abilities/applications、task tasks/storage 和 server modules 的现行 PRD；本文只记录验收范围及证据。

## 布局交互

- 默认指标页；批次、样本和物理量筛选属于指标页，结果文件默认覆盖任务全部批次。
- 结果文件使用共享树形表和可拖动的左右预览区；原始处理产物树使用同一组件。窄容器保留列宽并横向滚动，操作不被裁掉。
- 历史 `PostWorkspace` 保留原调用签名，转入统一三页签，不再显示独立图表导航。
- `post-workspace.spec.ts` 在1440/1920验证三个Tab、选择互不干扰；`post-session.spec.ts` 验证三维页 820px 滚动窗口、宿主 iframe 贴合且整页不锁死滚动。文件与会话浏览器测试另行验证。原始处理三条回归与预览弹窗一条通过。

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
