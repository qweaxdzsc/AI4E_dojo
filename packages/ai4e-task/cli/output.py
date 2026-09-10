"""CLI 统一文本与机器可读输出。"""

import json


def render(value, *, as_json: bool = False) -> str:
    """JSON 固定保留字段；文本模式保留可直接检查的缩进记录。"""
    return json.dumps(value, ensure_ascii=False, indent=2 if not as_json else None, default=str)
