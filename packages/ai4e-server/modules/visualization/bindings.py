"""项目—任务与 Vis 的可信交接，原数据只读且不复制。"""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode

import ai4e_task as task
from ai4e_task.tasks.post_results import MESH_SUFFIXES

from ...infrastructure.content_access import listing, revision, roots
from .application import asset


def _dependencies(path):
    """解析授权根内全部复合数据成员。"""
    dependencies = []
    visited = {path.resolve()}

    def collect_dependencies(current):
        if current.suffix.lower() not in (
            ".pvd",
            ".vtm",
            ".pvtu",
            ".pvti",
            ".pvtp",
            ".pvtr",
            ".pvts",
        ):
            return
        for entry in ET.parse(current).iter():
            member = entry.attrib.get("file") or entry.attrib.get("Source")
            if not member:
                continue
            child = (current.parent / member).resolve()
            if not child.is_relative_to(path.parent) or not child.is_file():
                raise ValueError("source_member_outside_root_or_missing")
            if child in visited:
                continue
            visited.add(child)
            dependencies.append(
                {"member": child.relative_to(path.parent).as_posix(), "revision": revision(child)}
            )
            collect_dependencies(child)

    collect_dependencies(path)
    return dependencies


def context(service, project, task_id, sources=None, *, write=False):
    """获取 task 公开存储区域，验证每个固定来源及受控成员。"""
    scope = task.visualization_storage(service.project(project), task_id, write=write)
    bindings, declarations = [], []
    for i, source in enumerate(sources or []):
        ref = source.get("ref", source)
        if ref.get("project_id", project) != project:
            raise ValueError("visualization_sources_must_share_project")
        path = asset(service, project, ref)
        record = service.store.get("asset", ref["asset_id"])
        if ref.get("member"):
            candidate = (path / ref["member"]).resolve()
            if (
                not path.is_dir()
                or not candidate.is_relative_to(path.resolve())
                or not candidate.exists()
            ):
                raise ValueError("source_member_outside_root")
            path = candidate
        declaration = {"id": source.get("id", "source-" + str(i)), "ref": ref}
        for key in ("block", "reader", "part", "coordinate_space"):
            if key in source:
                declaration[key] = source[key]
        if record.get("geometry") and ref.get("member") == record.get("geometry_member"):
            declaration["geometry"] = record["geometry"]
        dependencies = _dependencies(path)
        data_revision = hashlib.sha256(
            json.dumps([revision(path), dependencies], sort_keys=True).encode()
        ).hexdigest()
        if source.get("data_revision") and source["data_revision"] != data_revision:
            raise ValueError("source_revision_conflict")
        declaration["data_revision"] = data_revision
        bindings.append(
            {
                "ref": ref,
                "path": str(path),
                "fingerprint": revision(path),
                "dependencies": dependencies,
                "data_revision": data_revision,
            }
        )
        declarations.append(declaration)
    value = service.vis.request(
        "POST",
        "/internal/contexts",
        {"scope": scope, "bindings": bindings, "sources": declarations, "host": "dojo"},
    )
    service.vis_contexts[value["context_id"]] = {"project": project, "task": task_id}
    return value


def list_saved(service, project, task_id):
    """直接通过 Vis 扫描任务目录，服务数据库不持有配置真源。"""
    ctx = context(service, project, task_id)
    return service.vis.request(
        "GET", "/api/visualizations?" + urlencode({"context_id": ctx["context_id"]})
    )


def read_saved(service, project, task_id, identity, revision_value=None):
    """读取配置不要求原数据仍存在，重开时另行核验来源。"""
    ctx = context(service, project, task_id)
    query = {"context_id": ctx["context_id"]}
    if revision_value is not None:
        query["revision"] = revision_value
    return service.vis.request("GET", f"/api/visualizations/{identity}?" + urlencode(query))


def save(service, project, task_id, body):
    """保存不会修改任务配置或增加任务版本。"""
    ctx = context(service, project, task_id, body["spec"]["sources"], write=True)
    body = {**body, "spec": {**body["spec"], "sources": ctx["sources"]}}
    return service.vis.request(
        "POST", "/api/visualizations", {**body, "context_id": ctx["context_id"]}
    )


def open_session(service, project, task_id, body):
    """重开固定资产或创建新工作区，数据变化必须显式重新绑定。"""
    saved = (
        read_saved(service, project, task_id, body["visualization_id"], body.get("revision"))
        if body.get("visualization_id")
        else None
    )
    spec = saved["spec"] if saved else body.get("spec")
    sources = spec["sources"] if spec else body["sources"]
    ctx = context(service, project, task_id, sources)
    if spec:
        spec = {**spec, "sources": ctx["sources"]}
    session = service.vis.request(
        "POST",
        "/api/phys/sessions",
        {"context_id": ctx["context_id"], **({"spec": spec} if spec else {})},
    )
    session["scope_id"] = f"{project}:{task_id}"
    session["embed_url"] = "/vis/workspace/#/phys?" + urlencode(
        {
            "embed": "1",
            "host": "dojo",
            "context": ctx["context_id"],
            "session": session["session_id"],
            "secret": session["secret"],
            **({"asset": saved["visualization_id"]} if saved else {}),
        }
    )
    # 能力 ID 仅用于本地嵌入应用，宿主关闭接口仍核验项目—任务身份。
    service.vis_sessions[session["session_id"]] = {
        "project": project,
        "task": task_id,
        "context": ctx["context_id"],
        "sources": ctx["sources"],
    }
    return session


def close_session(service, project, task_id, identity):
    """关闭只允许操作当前宿主工作区。"""
    binding = service.vis_sessions[identity]
    if binding["project"] != project or binding["task"] != task_id:
        raise ValueError("visualization_session_scope_mismatch")
    result = service.vis.request(
        "DELETE", f"/api/phys/sessions/{identity}?" + urlencode({"context_id": binding["context"]})
    )
    service.vis_sessions.pop(identity, None)
    return result


_APPEND_LOCK = __import__("threading").RLock()


def _visualizable_entries(entries, root_id):
    """只保留目录和可视化网格，隐藏其余后缀。"""
    items = []
    for entry in entries:
        suffix = Path(entry["name"]).suffix.lower()
        if entry.get("directory"):
            items.append(
                {
                    **entry,
                    "id": f"{root_id}:{entry['path']}",
                    "root": root_id,
                    "leaf": False,
                }
            )
        elif suffix in MESH_SUFFIXES:
            items.append(
                {
                    **entry,
                    "id": f"{root_id}:{entry['path']}",
                    "root": root_id,
                    "leaf": True,
                }
            )
    return items


def list_visualizable_sources(service, project, task_id, root=None, path=""):
    """列出任务产物、共享数据集和已挂数据根中的可视化网格。"""
    service.project(project)
    if root:
        try:
            entries = listing(service, project, root, path or "", task_id)
        except FileNotFoundError:
            entries = []
        return {"items": _visualizable_entries(entries, root)}
    groups = []
    visible = roots(service, project, task_id)
    declared = [("task", "任务产物", "")] if "task" in visible else []
    if "project" in visible:
        declared.append(("project", "共享数据集", "shared/datasets"))
    declared.extend((key, f"已挂数据根 {key}", "") for key in visible if str(key).startswith("data"))
    for root_id, name, relative in declared:
        try:
            children = listing(service, project, root_id, relative, task_id)
        except (FileNotFoundError, KeyError, ValueError):
            children = []
        groups.append(
            {
                "id": f"{root_id}:{relative}",
                "name": name,
                "directory": True,
                "root": root_id,
                "path": relative,
                "leaf": False,
                "children": _visualizable_entries(children, root_id),
            }
        )
    return {"items": groups}


def append_session_sources(service, project, task_id, identity, sources):
    """串行追加固定来源，重复请求不新增对象，失败不发布宿主来源清单。"""
    from uuid import uuid4

    def key(source):
        ref = source.get("ref", source)
        return tuple(ref.get(k) for k in ("project_id", "asset_id", "revision", "member", "block"))

    with _APPEND_LOCK:
        binding = service.vis_sessions[identity]
        if binding["project"] != project or binding["task"] != task_id:
            raise ValueError("visualization_session_scope_mismatch")
        if not isinstance(sources, list) or not sources:
            raise ValueError("visualization_sources_required")
        known = {key(s) for s in binding.get("sources", [])}
        declarations = []
        for source in sources:
            if key(source) not in known:
                declarations.append({**source, "id": uuid4().hex})
                known.add(key(source))
        duplicates = [source for source in sources if key(source) in {key(s) for s in binding.get("sources", [])}]
        if duplicates:
            context(service, project, task_id, duplicates)
        if not declarations:
            return {"status": "already_added", "added": 0}
        ctx = context(service, project, task_id, declarations)
        result = service.vis.request("POST", f"/internal/phys/sessions/{identity}/sources", {
            "context_id": binding["context"], "binding_context_id": ctx["context_id"]})
        binding["sources"] = binding.get("sources", []) + ctx["sources"]
        return {**result, "added": len(declarations)}
