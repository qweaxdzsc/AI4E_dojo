# visPhysField 二级业务索引

三个二级业务不是独立服务，统一共享 [`../visPhysField.md`](../visPhysField.md) 列出的一级 Router、Application、Repository、SQLite、Provider、API、Store 语义和 Trame 连接。

| 二级模块 | 后端位置 | 前端位置 | 逐文件索引 |
| --- | --- | --- | --- |
| `fieldVisualization` | [`backend/.../fieldVisualization/`](../../../backend/modules/visPhysField/modules/fieldVisualization/) | [`frontend/.../fieldVisualization/`](../../../frontend/src/modules/visPhysField/modules/fieldVisualization/) | [`fieldVisualization.md`](fieldVisualization.md) |
| `dataExtraction` | [`backend/.../dataExtraction/`](../../../backend/modules/visPhysField/modules/dataExtraction/) | [`frontend/.../dataExtraction/`](../../../frontend/src/modules/visPhysField/modules/dataExtraction/) | [`dataExtraction.md`](dataExtraction.md) |
| `dataOverview` | [`backend/.../dataOverview/`](../../../backend/modules/visPhysField/modules/dataOverview/) | [`frontend/.../dataOverview/`](../../../frontend/src/modules/visPhysField/modules/dataOverview/) | [`dataOverview.md`](dataOverview.md) |

禁止二级 `api`、Router、Application 门面、Repository、数据库连接、`module.js`、`index.js`、独立路由/Store/Trame Server。变更同步一级 PRD/变更记录、对应二级索引、模块测试和 Trame E2E。

后处理Tab保持：`worker.py`在IPC前stash草稿；`trameUI/controller.py`接受visibility暂停/重绘，按下先分类手柄/轨道/点选，几何刷新不夹带相机；`interaction.js` 的 `phys-scene-ready` 只在推过新相机时同步；`client/bridge.js`接收直接同源宿主尺寸通知且已可见时不重复 resize；React `PhysFieldWorkspacePage.jsx`与`usePhysField.js`校验并转交。宿主验收见根 `e2e/post-session.spec.ts`、`post-real.spec.ts` 与 `.context/mvp/post-workspace-acceptance.md`。

`frontend/.../pages/PhysFieldWorkspacePage.css`：嵌入按父 iframe 高度铺满，不用 100dvh 叠一层浏览器视口；真实后处理浏览器验证内外iframe尺寸。
