# 架构说明

AI4E_Vis前后端均按十三级一级业务模块建立限界上下文。后端模块位于
`backend/modules/<moduleName>`，前端模块位于 `frontend/src/modules/<moduleName>`。

一级模块拥有自己的 API、Application、Domain、Repository 或前端 Page、Hook、Component；
跨模块只调用目标模块公开门面。公共无业务技术能力位于前后端各自的 `infrastructure`。

`dataAssets`拥有资产登记、上传、原始文件和资产表；`visDatasets`拥有格式解析、画像、
体检和数据内容查看。数据资产详情页通过两个模块公开门面聚合能力，不合并模块所有权。

`visPhysField` 是大型一级模块，其二级业务统一放入 `modules/fieldVisualization`、
`modules/dataExtraction`、`modules/dataOverview`，共享一级 Router、Repository、SQLite、
Trame、Provider、Store 和 API。`visEngine` 仅允许纯内核、缓存和性能原语。

仓库只保留根 `AGENTS.md` 作为开发入口。模块局部边界与文件约束统一维护在
`.context/modules/*.md` 和适用的 `.cursor/rules/*.mdc`，代码子目录不得散放 `AGENTS.md`。
