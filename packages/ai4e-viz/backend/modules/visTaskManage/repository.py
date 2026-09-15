"""可视化任务持久化公开门面。

具体表、SQL、迁移和映射位于同一一级模块的 ``specRepository``，本文件为Application
提供稳定且精简的Repository接口。
"""

from .specRepository import append_version, create_spec, get_version, list_specs, list_versions

__all__ = ["append_version", "create_spec", "get_version", "list_specs", "list_versions"]
