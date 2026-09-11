"""报告只接受结构化文字和固定证据，不保存任意执行内容。"""


def validate(value):
    """检查报告内容边界。"""
    if not isinstance(value.get("title"), str) or not value["title"].strip():
        raise ValueError("report_title_required")
    if len(value.get("text", "")) > 200000:
        raise ValueError("report_too_large")
    return value
