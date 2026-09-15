"""三维物理场一级应用门面。

本层负责把请求编排到二级业务、统一Trame会话、事务和错误边界；二级模块不重复建立
Application门面。
"""

from typing import Any

from .domain import FieldCommand
from .trame import legacy_scene_builder


def build_field_command(action: str, payload: dict[str, Any] | None = None) -> FieldCommand:
    """构造经过一级模块校验的物理场命令。"""

    normalized_action = action.strip()
    if not normalized_action:
        raise ValueError("物理场操作名称不能为空")
    return FieldCommand(action=normalized_action, payload=dict(payload or {}))


__all__ = ["build_field_command", "legacy_scene_builder"]


def append_sources(runtime, session_id, context_id, binding_context):
    """受控来源先加载成功，再扩展会话与保存上下文；失败不发布来源。"""
    context = runtime.context(context_id)
    sources, bindings = binding_context["sources"], binding_context["bindings"]
    session = runtime.sessions.get(session_id, context_id)
    # 锁住单会话通道和上下文发布，避免并发追加覆盖彼此。
    with runtime.sessions.lock:
        snapshot = session["channel"].call(
            {"operation": "append_sources", "sources": sources, "bindings": bindings}
        )
        context["sources"] = snapshot["spec"]["sources"]
        context["bindings"] = context["bindings"] + bindings
    return snapshot


def append_registered_source(runtime, session_id, context_id, asset_id, member=""):
    """独立 Vis 只接受本模块资产身份，不接受用户提交的文件路径。"""
    from uuid import uuid4

    from modules.dataAssets import get_artifact, resolve_data_asset_file, source_fingerprint

    context = runtime.context(context_id)
    if context.get("host") == "dojo":
        raise ValueError("host_source_authorization_required")
    asset = get_artifact(asset_id)
    _, file_path = resolve_data_asset_file(asset_id)
    from pathlib import Path

    path = Path(file_path)
    if member:
        from infrastructure.storage.atomic import contained

        if not path.is_dir():
            raise ValueError("source_member_requires_directory")
        path = contained(path, member)
    ref = {"asset_id": asset_id, "revision": source_fingerprint(path)}
    if member:
        ref["member"] = member
    value = runtime.register(
        {
            "sources": [{"id": uuid4().hex, "name": asset.get("name", asset_id), "ref": ref}],
            "bindings": [{"ref": ref, "path": str(path)}],
        }
    )
    try:
        return append_sources(runtime, session_id, context_id, runtime.context(value["context_id"]))
    finally:
        runtime.contexts.pop(value["context_id"], None)
