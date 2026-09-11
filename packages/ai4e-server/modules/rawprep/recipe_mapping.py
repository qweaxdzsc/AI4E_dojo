"""页面与原案例配置双向映射；未知设置不落入任务配置。"""

from .domain import validate


def patch(raw):
    """保持训练及其他段不变。"""
    return {"rawprep": validate(raw)}
