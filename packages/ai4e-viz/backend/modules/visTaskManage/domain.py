"""可视化任务、方法推荐和Spec版本的领域规则。"""

from __future__ import annotations


def ensure_base_version(current_version: int, base_version: int) -> None:
    """校验乐观锁基线；不一致时拒绝覆盖其他编辑者创建的新版本。"""

    if current_version != base_version:
        raise ValueError("version_conflict")
