"""独立预览工作进程协议；只描述检查与显示，不描述处理方案。"""

from typing import Literal, NotRequired, TypedDict


class PreviewRequest(TypedDict):
    """宿主校验后的进程请求，path 只用于本机进程间传递。"""

    path: str
    operation: Literal["inspect", "preview"]
    options: NotRequired[dict]


class PreviewResult(TypedDict):
    """成功结果与错误互斥，失败不得提供旧预览代替当前内容。"""

    result: NotRequired[dict]
    error: NotRequired[str]
