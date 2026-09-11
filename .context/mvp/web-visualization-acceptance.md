# 整合平台可视化实施切片验收

日期：2026-09-10。负责人：并行 Agent 1。此记录只声明可视化切片，不能替代四组合研究链路或全平台原型验收。

## 实现与交接

- B1：真实文本、表格、PT/NPY/Zarr 成员、指定维度分页；VTK 块及 point/cell/global 字段目录；字段有效值统计与直方图。高维张量不隐式压平，大整数分页返回字符串。
- B2：VTK 保留体网格至过滤完成，支持 surface、slice、clip、threshold、contour。等值使用点标量，拒绝隐式 cell-to-point。几何、拓扑、字段、有效值、身份分别二进制提交，manifest 最后发布。过滤生成实体明确标记。
- B3：公开 VisualizationWorkspace 与 FilePreviewContent 接入真实服务；字段/分量/表示/透明度、色标、相机、单输入管线分支与草稿应用；最多四窗口；场景由宿主保存。
- B4：相机默认独立，已验收同一固定资产的多个窗口显式联动；字段和色标独立开关。相机判断的实际限制及跨源缺口见下方。共享二进制缓存引用计数、最后订阅者取消下载、卸载释放；修订固定到内容请求。
- 提供可信 tensor_points 声明读取差值 PT：必须明确 coordinates/values/ids，不从数组名称猜几何；校验数量、有限坐标、唯一整数 ID，保留单位和实体集。真实差值服务浏览器链路验收见下方补充记录。

Python 工作进程兼容旧单 JSON 与 protocol_version=1 NDJSON；stdout 仅承载 progress/result/error，数组不进入事件。服务负责受控路径、生命周期、取消和缓存注册，viz 不访问 task 数据库或模型实现。

## 已执行测试

Python 使用已安装 ai4e-viz：

```bash
UV_CACHE_DIR=/private/tmp/dojo-uv-cache uv run --offline pytest tests/integration/test_viz_pipeline.py tests/integration/test_viz_extended.py tests/integration/test_viz_file_preview.py -q
UV_CACHE_DIR=/private/tmp/dojo-uv-cache uv run --offline ruff check packages/ai4e-viz tests/integration/test_viz_pipeline.py tests/integration/test_viz_extended.py
```

结果：20 passed；ruff 通过。覆盖解析场切片/裁切/等值、源 ID 阈值、二进制清单、向量范围与无效掩码、多块选择、真实 Zarr、高维和大整数分页、进程协议、显式张量点云拒绝路径。存在 VTK 9.6 GetData 弃用提醒及既有 FastAPI 测试客户端弃用提醒。

浏览器使用真实本机服务 8002、Vite 5174；公开组件通过 Vite 模块挂载，未替换服务接口或渲染器。命令模板：

```bash
DOJO_WEB_URL=http://127.0.0.1:5174 DOJO_API_URL=http://127.0.0.1:8002 DOJO_VIZ_FILE=<真实登记源相对路径> PLAYWRIGHT_JSON_OUTPUT_NAME=<证据目录报告路径> npm run --prefix packages/ai4e-web test:e2e -- visualization-views.spec.ts --reporter=json
```

两份报告与实际画面均位于 `.context/mvp/web-visualization-results/`：

- `shapenet-playwright.json`、`shapenet-field.png`：真实 ShapeNet quadpress_smpl.vtk 与安全组合，2 passed（8.2 秒）。登记根 data0，源 `param1/1dc58be25e1b6e5675cad724c63e222e/quadpress_smpl.vtk`。
- `nasa-playwright.json`、`nasa-field.png`：真实 NASA CRM surface.vtp，含直接原型尺寸对照，1 passed（8.4 秒）。源 `viz-nasa/surface.vtp`，来源为既有实际比较产物 `/private/tmp/dojo-cross-model/comparison/nasa/surface/sample-1/surface.vtp`；SHA256 `a497df8f57857fb3dbc92a8bc049a2833583a80ea10c6dd3f95b300eb7e57945`。

浏览器断言覆盖：真实取消返回 canceled 且无结果引用、真实字段渲染、四窗口上限及关闭、表示方式独立、鼠标旋转后的真实相机联动、阈值转换、服务保存/读取场景、卸载重挂后的分支与字段恢复、相机姿态以 1e-10 精度恢复、缓存引用与条目归零、所有二进制请求固定修订、分支祖先链和大端字节转换。截图为实际几何渲染证据，不用截图体积声明视觉一致性。

本轮修复：窗口关闭后已取消下载的迟到异常不再误报为整个工作区失败；相机恢复断言允许 VTK 浮点规范化造成的机器舍入误差。

## 本期已验收的补充功能

以下能力已完成，不能再列入“未交付”：

- 真实 NASA 两模型差值：服务 → viz → 二进制 → 浏览器点云显示。
- 正式 HTTP post 导出网格：真实表面拓扑、预测/真值字段、454404 个原点身份全量一致及真实点拾取。
- 点/单元拾取、字段分量值和 64 位身份保真；单元语义另有解析夹具浏览器测试。
- WebGL 实际 context-loss 恢复、单窗口预算失败隔离及卸载缓存释放。
- 场景经服务保存/读取后恢复固定来源、过滤分支、字段和相机。
- 共享转换订阅：本切片前端两项协议测试通过；主 Agent 已重新验收真实后端共享进程/订阅/取消/缓存等 33 项。后端证据入口为 `web-integrated-acceptance.md` 的 `integration-final.xml`，不是本切片以夹具代验服务。
- 布局：本切片直接比较整合 HTML 的查看器栏宽、间距和内边距；主 Agent 补充完成六页宿主主面板误差 ≤2px 的验收。两者均不等同所有状态的逐像素一致性。

### 相机联动完整身份与显式跨源证据已验收

当前同源判断完整核对 project_id / asset_id / revision / member / block。不同源必须由显示资产提供同一显式 coordinate_space.id 和 coordinate_space.unit，并且 evidence 为 source-declaration、source_refs 与当前固定源身份一致；物理场单位、文件名、包围盒和几何外观均不能作为替代证据。

恢复场景先保持相机独立，等待实际显示资产到达后重查联动；不兼容时明确提示“相机联动已禁用”，保存时移除该联动组。原“只比较 asset_id”限制已撤除，不再把跨源已知同坐标联动列为未交付。

合法声明由用户显式 dataset.coordinate_space 写入正式 post 的 VTK FieldData coordinate_space_id/coordinate_space_unit 或差值 sidecar。viz 读取实际字段，或读取服务从受控 sidecar 注入的可信 geometry.coordinate_space，再绑定 source_refs；浏览器不能自行补证据。实际 NASA 当前无可信坐标单位，因此保持未知并拒绝跨源，未为测试注入猜测单位。

## 本期实现缺口与限制

### 其他未完成实现

超大成员目录虚拟化、完整文本搜索和全部表格列分页尚未完成。这些是现有文件浏览/预览实现的限制，不应混入已验收完整性声明；是否作为本期必须验收叶子由总计划统筹明确。

## 已实现但尚未执行的专项测试

- 隐藏窗口延迟绘制已实现，尚无专门的可见性自动测试。
- 资源预算、单窗口超限隔离和引用释放已有测试；尚未完成真实大数据压力测试或 GPU 泄漏长测，不能声明生产规模资源稳定性。
- 尚未覆盖全部原型状态、错误状态、视口尺寸的逐像素回归；现有真实渲染截图与主面板尺寸对照不能替代此项。

## 本期范围外

流线、体渲染、时间动画、自动插值/配准、完整 ParaView 和高级结构化重建不属于本期承诺。生产规模压力和训练精度也不因本切片功能测试而获得承诺。

## 已验收补充的具体证据

- 通过 WEBGL_lose_context 实际丢失和恢复上下文，验证恢复后相机与字段状态继续可用；不以派发虚拟 DOM 事件代替浏览器机制。
- 新增 `visualization-safety.spec.ts`，明确使用解析三角形测试夹具：四窗口中的第四窗口 129 MiB 声明触发 128 MiB 门禁，三个其他窗口继续渲染，单元字段拾取返回 cell 0、原 ID `9007199254740993`、实际字段值 99；卸载后缓存归零。结果 1 passed（2.1 秒）。
- 按整合 HTML 内嵌第 7 步的 post-body、viewer-pane、viewcontrols 对齐网格比例、9px 间距、侧栏宽度、标题与覆盖式窗口标签；修正宿主全局 header 高度干扰。本项为布局尺寸对齐，未宣称全部像素基线通过。
- 新增保留既有 original_point_id/original_cell_id 回归，拒绝重复或非整数身份；安装后 Python 圈定 18 passed。
- NASA 与安全组合曾通过 2 项（10.2 秒）；同名报告已被后续 NASA 原型尺寸对照运行替换，当前保留报告结果以下方最新记录为准。

- 真实差值 `visualization-difference.spec.ts`：1 passed（5.0 秒），使用总验收的 NASA 两模型正式差值操作，454404×1 数值由主 Agent 独立逐值确认；浏览器通过固定 AssetRef/revision/member 获得受信任点云，不生成替代数组。报告 `difference-playwright.json`、实际截图 `nasa-difference.png`。差值无拓扑声明，因此显示点云，不伪造表面网格。
- 实看实际差值截图后修复 Canvas 内在像素尺寸撑开 CSS 网格造成的白边/裁切，并新增视图高度不超工作区的自动断言；最终截图已复核飞机全形及真实红蓝差值。

- 最终 ShapeNet 与安全组合回归 `shapenet-playwright.json`：2 passed（8.2 秒），同时覆盖最终画布布局、context-loss 与四窗口预算隔离。前端 build 通过，仍有既有体积提醒。

- 最新 NASA 原型尺寸对照回归 `nasa-playwright.json`：1 passed（8.4 秒）。测试直接读取唯一整合 HTML 的 stageDocuments[6]，在禁用脚本的 iframe 中取 post-body 真实计算样式，逐值比较查看器前两栏宽度、gap、padding；通过。此为真实原型尺寸对照，不将实现自身截图当作原型基线，仍不等同全部控件逐像素对照。

## 正式 HTTP 导出网格复验

`visualization-export.spec.ts` 使用 `.context/mvp/web-integrated-results/nasa_crm_transolver3-preview.json` 的固定 `mesh` AssetRef，不复制文件、不另行登记来源。已通过（1 passed，3.8 秒）：

- 几何为 454404×3，存在真实 polys 拓扑，未标成生成实体。
- 字段包含 `surface.cp.prediction`、`surface.cp.truth`、`original_point_id`、`original_cell_id`。
- 下载实际二进制后逐项对照全部 454404 个显示原点映射与 `original_point_id`，完全一致。
- 浏览器实际选择预测字段、鼠标拾取真实点，返回 point 归属、原始 ID、有限预测值。
- 截图已经复核完整飞机表面及实际场着色；报告 `export-playwright.json`，图片 `nasa-export.png`。

命令：

```bash
DOJO_WEB_URL=http://127.0.0.1:5174 DOJO_API_URL=http://127.0.0.1:8002 PLAYWRIGHT_JSON_OUTPUT_NAME=$PWD/.context/mvp/web-visualization-results/export-playwright.json npm run --prefix packages/ai4e-web test:e2e -- visualization-export.spec.ts --reporter=json --output=/private/tmp/dojo-viz-export-test-results
```

独立输出目录避免并行平台测试清理可视化截图。测试保留原资产 project/task/revision 来源；未通过缩减网格或接口替身替代实际产物。


## 共享转换订阅客户端

`api.ts` 捕获初次 POST 的可选 `subscription_id`；取消仅提交 JSON `{subscription_id}`，重复 abort 至多释放一次。旧服务未返回该字段时维持无正文取消。轮询共享操作不能替换本调用的订阅身份。

`visualization-subscriptions.spec.ts` 使用明确的协议夹具，2 passed（2.3 秒）：两个查看器共享 operation_id，取消 A 只提交 subscriber-1，B 继续成功；旧无订阅服务取消正文仍为空。报告 `subscriptions-playwright.json`，独立输出 `/private/tmp/dojo-viz-subscription-test-results`。该测试验证客户端正文与等待逻辑，不能替代后端真实工作进程订阅隔离测试；后者由主 Agent 的 33 项最终回归另行覆盖，见总验收记录。前端 build 通过。


## 相机联动最终复验

`visualization-camera.spec.ts`：最终服务重启后 2 passed（4.6 秒），报告 `camera-playwright.json`，独立输出 `/private/tmp/dojo-viz-camera-test-results`。

- 契约用例逐项改变 project/asset/revision/member/block 验证不能冒充同源；跨源声明 ID、单位、固定来源不匹配均拒绝。
- 恢复合法声明联动组允许联动，缺少声明则明确禁用；再次点击开启仍拒绝，保存不保留失效组。
- 真实服务读取两个明确标为测试数据的解析 VTK 文件：`data0/viz-camera-contract/left.vtp`、`right.vtp`，三个点分别为 (-1,-1,0)、(1,-1,0)、(0,1,0)，明确米单位，坐标空间 ID 为 explicit-test-triangle-frame。两个文件的真实 FieldData 经 viz 读取，允许跨资产相机传播。这是物理坐标明确的测试夹具，不是 NASA 研究数据或训练产物。
- 同一真实服务读取既有实际 NASA 正式表面网格和真实差值资产，因无可信坐标长度单位，恢复时相机组被禁用，两个视图仍正常显示。未修改这些资产或猜测单位。
- 已安装 viz 的圈定 Python 回归现为 20 passed，新增真实 VTK 写入/读回声明及可信张量声明单位独立性；前端 build 通过。

算法声明传播和平台 sidecar 可信读取由对应 Agent 的真实导出及平台回归另行覆盖；本浏览器记录不将解析夹具冒称正式 NASA 坐标单位已确认。

## 总体验收发现的问题及修复

总浏览器运行暴露两处边界，已保留原功能断言修复：

1. 正式网格测试只监听 GET 成功结果。共享缓存命中时，POST 直接返回成功清单，测试误将未观察到 GET 当作显示失败。现同时采集 POST/GET 成功回执，仍保留 454404 身份全量比对和真实点拾取。
2. 初次提交把外部 AbortSignal 传入 fetch，回执前取消会丢失服务已创建的 subscription_id，导致无法释放该订阅。现已取消的调用在提交前直接拒绝；已经发出的提交收取回执后，若调用已取消，则准确释放本订阅。状态轮询仍响应取消。

`final-fixes-playwright.json`：4 passed（4.7 秒），覆盖真实正式 NASA 导出网格、确定性延迟回执下 A 取消/B 成功、旧无订阅接口兼容、提交前取消不产生请求。取消竞争使用明确传输夹具而非真实研究数据替身。独立输出 `/private/tmp/dojo-viz-final-fixes`，前端 build 通过。
