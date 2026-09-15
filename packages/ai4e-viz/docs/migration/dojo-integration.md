# AI4E_Vis 迁入 Dojo：安装、接入与交付边界

## 迁移来源和目录

来源版本为 `879e3a5d333e91ceae10da16d5228cad8661a7fd`。385 个跟踪文件与 8 个额外规则/技能文件保持原相对路径，共393份；逐文件来源哈希与 copy/adapt 处置见 [source-manifest.json](source-manifest.json)，完整当前文件目录见 [file-inventory.md](file-inventory.md)。原 Dojo inspect/preview/pipeline/serialization/render/compose/runtime 继续保留。

13个模块 dataAssets、visDatasets、visTaskManage、visPhysField、visGeometry、visFigure、visIO、visConvertor、visEngine、reportManage、reportDesigner、automation、MCP 均迁入；未创建平行 visAssets/visCharts，也未拆走原 JSX 应用。折线、散点、表格、图片和报告仍由原模块提供。本期不重写图表产品或 Dojo 曲线页。

不迁入 .git、数据库、业务数据、安装依赖、构建缓存、本机连接配置和失效技能链接。示例资源、夹具、原测试和原架构资料保留；requirements 只作为历史资料，依赖真源为包 pyproject.toml、根 uv.lock 与各前端 package.json/package-lock.json。

## 当前实现分层

后端采用模块优先的轻量 DDD；api 处理协议，application 编排，domain 保存规则，Repository 负责模块持久化。技术性文件事务、进程和代理在 infrastructure。原 SQLite 保存入口保留历史读取，新配置资产由 visIO 和 visTaskManage 的文件 Repository 写入任务目录。

- visTaskManage/fileSpecRepository.py：模式校验、轻量限制、不可变 spec 修订。
- visIO/assetRepository.py、save.py：CAS 修订、幂等请求、索引最后提交、配置摘要核验。
- visIO/exportRepository.py、exports.py：独立输出进程、取消、临时目录和最终清单。
- dataAssets/externalSources.py：固定来源解析与递归复合文件修订校验。
- visDatasets/physicalDataset.py：完整网格、明确几何点云、PVD/显式帧和块选择。
- visPhysField/session.py、worker.py：每工作区独立 Trame/VTK 进程。
- visPhysField/scene.py：Apply 事务、图层/视口/相机与命令；producer.py：PNG/CSV/动画。
- visPhysField/modules/fieldVisualization、dataExtraction、dataOverview：原二级业务边界，实际字段/过滤/提取实现从这里调用 Engine。
- visEngine：VTK 过滤、真实采样、几何复用、远程阴影原语，不管理业务资产。
- visPhysField/trameUI/layout.py：一级 UI 装配及属性/树/时间/提取控件。
- Vis React visIO：保存表单、导出状态；visPhysField：工作区生命周期、嵌入、客户端录制。
- Dojo Web visualization/PhysFieldEmbed.tsx：宿主目标任务选择与独立应用嵌入；原查看器仍可使用。

相较计划，UI子文件集中为 layout.py，命令集中为 Scene.command，录制集中在 React 工作区组件，进程监督使用 Sessions 与 infrastructure/process。没有为了目录数量建立空 ports/commands/rendering 占位；现有文件职责与依赖门禁有测试。全局架构只在 Dojo 根架构文件维护，应用内部架构在本包 docs/architecture/architecture.md。

## 项目—任务保存契约

```text
tasks/<task>/visualizations/
  <visualization-id>/
    asset.json
    revisions/000001/spec.json
    exports/<export-id>/manifest.json + 显式请求的文件
  .runtime/locks/
  .runtime/staging/
```

会话对象驻留独立进程，不默认创建磁盘场景检查点。保存记录输入固定引用、处理步骤、图层、相机、颜色和时间配置；不复制原网格、数组，不自动截图，不写训练 runs 或配置，也不创建任务版本。exports 仅显式导出后出现。

asset.json 的 revision/content_hash 指向当前修订，revision_hashes 用于历史内容核验。保存需 expected_revision，冲突返回409；同 request_id 不得换内容。不可变 spec 写入成功后原子提升 asset 索引，失败保留旧索引。导出清单单独记录 revision/content_hash/files SHA-256；失败或取消无成功文件清单。

数据引用不包含任意机器输出路径。来源缺失和修改分别报错，重绑定通过显式提交新来源和新修订完成；历史 spec 不直接覆盖。目录复制后可列出并读取配置，外部引用需要宿主重新解析/登记。缓存删除不影响配置真源。归档任务经宿主写入检查拒绝保存及新导出。

## 安装和运行

从 Dojo 根运行：

```bash
uv sync --group visualization
npm ci --prefix packages/ai4e-viz/frontend
npm run --prefix packages/ai4e-viz/frontend build
uv sync --group visualization --reinstall-package ai4e-viz
uv run --no-sync ai4e-vis --port 8091 --runtime-root /absolute/vis-runtime --context /absolute/context.json
```

context.json 只由受信任调用者创建，路径必须在源码和安装目录之外，例如：

```json
{
  "scope": {
    "scope_id": "project-a:task-a",
    "project_id": "project-a",
    "task_id": "task-a",
    "root": "/absolute/project/tasks/task-a/visualizations",
    "writable": true
  },
  "sources": [
    {"id": "field", "ref": {"asset_id": "field-a", "revision": "<原文件SHA256>"}}
  ],
  "bindings": [
    {"ref": {"asset_id": "field-a", "revision": "<原文件SHA256>"}, "path": "/absolute/original/field.vtu"}
  ]
}
```

只预览时 scope 可以省略（禁止保存），sources/bindings 仍需明确。CLI 返回包含不透明 context ID 的地址。没有 context 的入口提示调用者提供来源与目标，不自动创建研究任务或回退到代码目录。

工作区默认4个并发、心跳超时900秒、满员短空闲回收45秒，可在启动进程时设置 AI4E_VIS_MAX_SESSIONS、AI4E_VIS_SESSION_TTL、AI4E_VIS_SESSION_IDLE。打开页面30秒续约，卸载组件先关闭再创建，浏览器关闭/断网的残留会话超时回收；满员时先回收已无心跳的短空闲会话。重启服务后需由可信宿主重新绑定 context，已保存配置仍在任务目录。

实际 wheel 发布前必须先构建 frontend；build_hook.py 将已有 dist 放进 wheel。没有前端产物的纯 Python 安装不会在工作区页面假装成功，会返回明确503。安装后用外部 runtime/context 运行；禁止把包根加进普通 Python PYTHONPATH，避免旧 inspect 目录遮蔽标准库。

## Dojo 宿主交接

ai4e-task.visualization_storage 核验项目/任务和归档状态；server 通过稳定引用解析来源与 XML 依赖；Vis 不导入 task/core/server，也不访问任务 SQLite。服务间 /internal/contexts 需实例控制令牌，浏览器 /vis 代理拒绝内部控制入口。每请求绑定 context，不切换全局环境变量选择任务。

沿用 Dojo API 版本前缀：

```text
POST /api/v1/projects/{project}/tasks/{task}/visualizations
GET  /api/v1/projects/{project}/tasks/{task}/visualizations
GET  /api/v1/projects/{project}/tasks/{task}/visualizations/{id}
POST /api/v1/projects/{project}/tasks/{task}/visualizations/sessions
DELETE /api/v1/projects/{project}/tasks/{task}/visualizations/sessions/{session}
```

Vis 公开接口为 /api/visualizations、/api/phys/sessions、会话 commands/heartbeat、资产 exports/recordings 及 /api/phys/capabilities。宿主通过 /vis 同源代理，独立应用通过原地址使用同一 API。HTTP与WebSocket均转发；跨机器复制与远程数据搬运未引入。

脚本顺序与 UI 一致：取得 context → POST sessions → POST commands（operation=apply，spec=声明式配置）→ snapshot → POST visualizations（context_id/name/spec/expected_revision/request_id）→ 按需 POST exports（revision/options）。轮询输出状态到 succeeded 后下载清单中的文件。新保存必须带 context，历史无 context GET 保留 SQLite 读取。

## 物理场默认行为和已知限制

云图、切面、Glyph、流线、等值、Probe均计算完整数据；普通数组须提供明确几何映射，不猜体拓扑。时间加载支持 PVD 与固定显式帧，缺失时间不插值；native VTKHDF 内部时间轴尚未专门接入。静态 VTK 家族能力沿用现有 reader，不能按文件扩展名无限承诺任意格式。

多源共享工作区，1/2/4窗口，各图层可独立隐藏。相机联动默认关闭；不同来源需显式同坐标空间声明。轨道结束只回写活动相机，不因交互重读网格。几何/拓扑相同的时间帧复用结构，拓扑改变重新装配。Apply错误保留原画面。

PNG、PNG序列、CSV、MP4及真实浏览器WebM均为显式输出，默认1280×720、24fps，UI/接口可改。脚本动画传固定 times/cameras；交互录制记录实际视口变化。报告通过 visIO.materialize_reference 按固定资产、修订、摘要和视图请求PNG，沿用唯一物理输出器；完整Quarto产品流程另行验收。

本地渲染默认，remote需显式选择。Linux远程阴影实现已接入，但本次macOS环境不能证明Linux/EGL/OSMesa实际可用；能力中的平台条件不代替硬件验收。完整结果和证据见 [验收记录](../../../../.context/mvp/vis-migration-acceptance.md)。
