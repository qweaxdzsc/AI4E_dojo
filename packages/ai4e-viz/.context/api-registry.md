# AI4E_Vis · API 注册表

> 唯一应用装配入口：[`backend/server/api.py`](../backend/server/api.py)。业务 Router 在一级模块 `api.py`，Server 不实现业务。
> 契约基线：[`backend/tests/test_contract.py`](../backend/tests/test_contract.py)。最后核对：2026-08-29。

## Server 与技术健康

| 方法与路径 | 所有者 | 作用 |
| --- | --- | --- |
| `GET /api/health` | `server` | API、目录修订和内置资产健康 |
| `GET /api/renderer-health` | `server` + Infrastructure | ECharts、Perspective、O3DV、Trame 技术可达性 |

## `dataAssets`

| 路径组 | 作用 |
| --- | --- |
| `GET /api/artifacts`、`GET /api/artifacts/{artifact_id}` | 资产列表与详情 |
| `PATCH /api/artifacts/{artifact_id}/classification` | 分类修正与版本历史 |
| `GET /api/artifact/{artifact_id}/file/{file_name}` | 白名单原始文件读取 |
| `POST /api/artifacts`、`POST /api/upload` | 批量上传与旧单文件兼容入口 |

## `visDatasets`

| 路径组 | 作用 |
| --- | --- |
| `GET /api/artifact/{artifact_id}/parse`、`POST .../analyze` | 解析画像、质量检测与显式分析 |
| `GET /api/gs-fixture/{relative_path:path}` | G-S fixture 受控读取 |

## `visTaskManage`

| 路径组 | 作用 |
| --- | --- |
| `GET /api/catalog`、`GET /api/specs` | 5 家族、19 类型、23 方法与参数 Schema |
| `GET /api/examples/{artifact_id}` | 确定性或真实数据案例 |
| `GET /api/artifact/{id}/recommend`、`GET /api/artifacts/{id}/recommendations` | 推荐候选 |
| `/api/visualization-specs*` | Spec 列表、创建、不可变版本读取与乐观锁追加 |

## 可视化表现

| 模块 | 路径组 | 作用 |
| --- | --- | --- |
| `visGeometry` | `/api/artifact/{id}/representation/o3dv.glb`、`/api/artifacts/{id}/representations/{name}` | GLB 直出或派生 |
| `visFigure` | `GET /api/example-assets/{asset_id}` | 图片、视频和静态回退 |
| `visIO` | `POST /api/artifacts/{id}/visualizations/preview` | 参数校验后的非持久预览 |
| `visIO` | `POST /api/artifacts/{id}/visualizations` | 创建 Spec 版本与冻结可视化 |
| `visIO` | `GET /api/visualizations*` | 可视化列表与详情 |

## 报告

| 模块 | 路径组 | 作用 |
| --- | --- | --- |
| `reportManage` | `GET/POST /api/reports`、`GET /api/reports/{id}` | 报告中心与报告读取 |
| `reportManage` | `POST /api/reports/{id}/versions`、`.../duplicate` | 冻结版本与复制 |
| `reportManage` | `/api/report-exports*`、`GET /api/quarto/health` | 导出、重试、下载和 Quarto 健康 |
| `reportDesigner` | `GET/PATCH /api/reports/{id}/draft` | 草稿读取与乐观锁保存 |

## 当前无独立 HTTP 路由

`visPhysField` 的交互走统一 Trame 服务；`visConvertor` 由几何模块调用；`automation`、`MCP` 当前只保留应用边界；`visEngine` 不允许建立业务 HTTP API。

新增或移动路由时：先改所属模块测试，再改 `test_contract.py`，确认 `server/api.py` 仍只注册 Router，最后同步本表。

## 任务配置与物理场工作区

- `POST /internal/contexts`：可信宿主登记，控制令牌校验，不能由宿主公共代理转发。
- `POST/GET /api/visualizations`、`GET /api/visualizations/{id}`：上下文内配置保存、列表及读取，历史 GET 无上下文保留旧库。
- `POST /api/visualizations/{id}/exports`：固定修订显式输出；状态、取消与成功文件下载使用对应子资源。
- `POST /api/visualizations/{id}/recordings`：用户明确提交的 WebM。
- `POST/DELETE /api/phys/sessions`：工作区建立和按 ID 关闭；commands、heartbeat 共享一级协议。
- `/api/phys/view/{context}/{session}/...`：受控 Trame HTTP/WS。
- `GET /api/phys/capabilities`：实际模式与平台能力。

## 对象工作台补充

- `/api/phys/sessions/{id}/commands`：对象创建/参数应用/复制/重命名/删除、display、视图/布局/相机、Probe 与时间命令；浏览器不能通过命令传原始绑定。
- `/api/phys/sessions/{id}/sources`：独立 Vis 的已登记资产追加。
- `/internal/phys/sessions/{id}/sources`：可信宿主上下文追加，不经公共代理暴露。
- 宿主消息 `source-list`、`source-append`、`session-open`：请求 ID 与来源窗口校验；重开由宿主重新绑定全部保存来源。

工作台同源嵌入动作 `export_csv`：明确 Probe CSV 请求，仍由共享导出弹窗、固定修订及原导出 API 处理；不新增独立存储路径。
