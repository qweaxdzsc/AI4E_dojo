"""可持久化场景门禁：只保存显示意图，核验来源和视图关联。"""

import math

KEYS = {
    "schema_version",
    "sources",
    "pipeline_nodes",
    "representations",
    "viewports",
    "link_groups",
    "active_view",
    "selected_node",
}


def validate_scene(document):
    """拒绝悬空引用、重复身份、非法联动及不可序列化运行状态。"""
    if not isinstance(document, dict) or set(document) != KEYS or document["schema_version"] != 1:
        raise ValueError("scene_schema_invalid")
    for key in ("sources", "pipeline_nodes", "representations", "viewports", "link_groups"):
        if not isinstance(document[key], list) or not all(
            isinstance(item, dict) for item in document[key]
        ):
            raise ValueError("scene_list_required: " + key)
    if not 0 <= len(document["viewports"]) <= 4:
        raise ValueError("scene_viewport_limit")

    def identities(key, required=True):
        values = [item.get("id") for item in document[key] if required or "id" in item]
        if any(not isinstance(value, str) or not value for value in values) or len(values) != len(
            set(values)
        ):
            raise ValueError("scene_duplicate_or_missing_id: " + key)
        return set(values)

    views = identities("viewports")
    nodes = identities("pipeline_nodes", False)
    identities("representations", False)
    if document["active_view"] is not None and document["active_view"] not in views:
        raise ValueError("scene_dangling_active_view")
    if document["selected_node"] is not None and document["selected_node"] not in nodes:
        raise ValueError("scene_dangling_selected_node")
    source_ids = {source.get("asset_id") for source in document["sources"]}
    for view in document["viewports"]:
        if "source" in view and (
            not isinstance(view["source"], int)
            or isinstance(view["source"], bool)
            or not 0 <= view["source"] < len(document["sources"])
        ):
            raise ValueError("scene_dangling_view_source")
        if "opacity" in view and (
            not isinstance(view["opacity"], (int, float)) or not 0 <= view["opacity"] <= 1
        ):
            raise ValueError("scene_view_opacity_invalid")
        camera = view.get("camera")
        if camera is not None:
            if not isinstance(camera, dict):
                raise ValueError("scene_camera_invalid")
            for key in ["position", "focalPoint", "viewUp"]:
                if key in camera and (
                    not isinstance(camera[key], list)
                    or len(camera[key]) != 3
                    or any(not isinstance(v, (int, float)) for v in camera[key])
                ):
                    raise ValueError("scene_camera_vector_invalid")
    if None in source_ids:
        raise ValueError("scene_asset_id_required")
    previous = set(source_ids)
    for node in document["pipeline_nodes"]:
        if node.get("type") not in {"slice", "clip", "threshold", "contour", "surface"}:
            raise ValueError("scene_pipeline_type")
        if "input" in node and node["input"] not in previous:
            raise ValueError("scene_dangling_or_forward_pipeline_input")
        if "id" in node:
            previous.add(node["id"])
    for representation in document["representations"]:
        for key, ids in [
            ("viewport_id", views),
            ("pipeline_node", nodes),
            ("source_id", source_ids),
        ]:
            if key in representation and representation[key] not in ids:
                raise ValueError("scene_dangling_" + key)
        if "opacity" in representation and (
            not isinstance(representation["opacity"], (int, float))
            or not 0 <= representation["opacity"] <= 1
        ):
            raise ValueError("scene_opacity_invalid")
    for group in document["link_groups"]:
        if group.get("kind") not in {"camera", "field", "color"} or not isinstance(
            group.get("enabled"), bool
        ):
            raise ValueError("scene_link_invalid")
        members = group.get("view_ids", [])
        if (
            not isinstance(members, list)
            or len(members) != len(set(members))
            or any(v not in views for v in members)
        ):
            raise ValueError("scene_dangling_link_view")
        if group["enabled"] and len(members) < 2:
            raise ValueError("scene_link_requires_two_views")

    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("scene_nonfinite_value")
        if isinstance(value, dict):
            if set(value) & {"buffers", "webgl", "renderer", "download_handle"}:
                raise ValueError("scene_runtime_state_forbidden")
            for child in value.values():
                finite(child)
        elif isinstance(value, list):
            for child in value:
                finite(child)

    finite(document)
    return document
