# AI4E_Vis PRD 索引

产品需求以用户确认和本目录文档为准，代码结构与文件职责由 [`.context/index.md`](../../.context/index.md) 导航。十三级一级模块与同名 PRD 一一对应，不能用代码现状反推需求。

历史治理切片记录在 [`CHANGELOG.md`](CHANGELOG.md)。以后每次代码修改至少更新：

1. 受影响模块 PRD 的行为、边界或验收条件；若不改变产品行为，在 `CHANGELOG.md` 说明原因。
2. 对应 `.context/modules/<moduleName>.md` 的文件与链路索引。
3. 对应模块测试、契约测试或 E2E 用例。

| 一级模块 | PRD 文件 |
| --- | --- |
| `dataAssets` | [`dataAssets.md`](dataAssets.md) |
| `visTaskManage` | [`visTaskManage.md`](visTaskManage.md) |
| `visGeometry` | [`visGeometry.md`](visGeometry.md) |
| `visDatasets` | [`visDatasets.md`](visDatasets.md) |
| `visPhysField` | [`visPhysField.md`](visPhysField.md) |
| `visFigure` | [`visFigure.md`](visFigure.md) |
| `visIO` | [`visIO.md`](visIO.md) |
| `visConvertor` | [`visConvertor.md`](visConvertor.md) |
| `automation` | [`automation.md`](automation.md) |
| `MCP` | [`MCP.md`](MCP.md) |
| `reportManage` | [`reportManage.md`](reportManage.md) |
| `reportDesigner` | [`reportDesigner.md`](reportDesigner.md) |
| `visEngine` | [`visEngine.md`](visEngine.md) |
