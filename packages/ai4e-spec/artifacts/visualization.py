"""独立可视化应用与宿主交接；只包含声明，不包含数组或运行对象。"""

from typing import NotRequired, TypedDict


class VisualizationStorageScope(TypedDict):
    """可信服务分配的任务保存区域；root 不发送给浏览器。"""

    scope_id: str
    project_id: str
    task_id: str
    root: str
    writable: bool


class VisualizationRef(TypedDict):
    """稳定配置资产引用；导出不会改变 revision 或 content_hash。"""

    visualization_id: str
    project_id: str
    task_id: str
    revision: int
    content_hash: str
    kind: str


class VisualizationSession(TypedDict):
    """浏览器所见会话，不泄露物理文件路径或内部端口。"""

    session_id: str
    status: str
    embed_url: str
    scope_id: str | None
    error: NotRequired[str | None]


class VisualizationSourceRef(TypedDict):
    """固定输入身份；具体机器位置只在可信运行绑定中出现。"""

    asset_id: str
    revision: str
    project_id: NotRequired[str]
    task_id: NotRequired[str | None]
    member: NotRequired[str]
    block: NotRequired[int]


class VisualizationExportRef(TypedDict):
    """显式输出关联固定配置修订，不覆盖资产内容身份。"""

    export_id: str
    visualization_id: str
    revision: int
    content_hash: str
    status: str
    format: str
