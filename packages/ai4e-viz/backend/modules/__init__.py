"""AI4E_Vis 后端一级业务模块集合。

本包只负责声明十三级限界上下文。跨模块调用应通过各模块 ``__init__``
公开的应用接口完成，禁止直接导入其他模块的 Repository 或内部业务文件。
"""

MODULE_NAMES = (
    "dataAssets", "visTaskManage", "visGeometry", "visDatasets", "visPhysField",
    "visFigure", "visIO", "visConvertor", "automation", "MCP",
    "reportManage", "reportDesigner", "visEngine",
)
