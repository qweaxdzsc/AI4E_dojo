"""报告编排一级模块公开入口。

跨模块只能从此处使用文档骨架、校验和草稿用例，禁止访问内部 Domain 或 Repository。
"""

from .domain import scaffold_document, validate_document
from .repository import get_draft, replace_draft

__all__ = ["get_draft", "replace_draft", "scaffold_document", "validate_document"]
