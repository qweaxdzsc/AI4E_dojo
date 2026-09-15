"""报告中心、不可变版本和导出任务的 HTTP 适配层。

本 Router 组合 reportManage 与 reportDesigner 的公开门面，不访问其他模块内部
Repository。内置报告在导出前冻结为不可变阅读快照，避免把源文件链接伪装成报告产物。
"""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import FileResponse

from modules.reportDesigner import get_draft, replace_draft

from . import (
    create_export, create_report, duplicate_report, freeze_reader_snapshot,
    freeze_report, get_export, get_report_version, list_reports as stored_reports,
)
from .builtinReports import REPORT_DOCUMENTS, REPORTS
from .gradShafranovReport import (
    REPORT_ID as GS_REPORT_ID,
    build_report as build_gs_report,
    report_list_item as gs_report_list_item,
)
from .millerReport import (
    REPORT_ID as MILLER_REPORT_ID,
    build_report as build_miller_report,
    report_list_item as miller_report_list_item,
)
from .quarto import EXPORT_ROOT, quarto_health, start_export


router = APIRouter(tags=["reportManage"])


@router.get("/api/reports")
def api_reports():
    """列出持久化报告和内置可追溯报告。"""

    persisted = stored_reports()
    persisted_ids = {item["id"] for item in persisted}
    seeded = [item for item in [*REPORTS, gs_report_list_item(), miller_report_list_item()] if item["id"] not in persisted_ids]
    items = [*persisted, *seeded]
    return {"items": items, "updated_at": max((item.get("updated_at") or item.get("generated_at") or "" for item in items), default=None)}


@router.post("/api/reports", status_code=201)
def api_create_report(payload: dict = Body(...)):
    """校验报告简报并创建可编辑报告。"""

    required = ["title", "goal", "audience", "template"]
    missing = [key for key in required if not str(payload.get(key) or "").strip()]
    if missing:
        raise HTTPException(422, detail={"code": "REPORT_BRIEF_REQUIRED", "fields": missing})
    if payload["template"] not in {"analysis", "validation", "weekly", "blank"}:
        raise HTTPException(422, detail={"code": "INVALID_REPORT_TEMPLATE", "legal": ["analysis", "validation", "weekly", "blank"]})
    return create_report(payload)


@router.get("/api/reports/{report_id}")
def api_report(report_id: str, request: Request):
    """读取草稿报告或内置只读报告的阅读模型。"""

    try:
        draft = get_draft(report_id)
        return {
            "id": report_id, "title": draft["title"], "author": draft["author"], "status": draft["status"],
            "summary": draft["brief"].get("goal", "可编辑报告草稿"), "generated_at": draft["generated_at"],
            "spec": f"ReportDocument draft r{draft['draft_revision']}", "takeaways": [],
            "document": draft["document"], "draft_revision": draft["draft_revision"], "editable": draft["editable"],
        }
    except KeyError:
        pass
    if report_id == GS_REPORT_ID:
        return build_gs_report(str(request.base_url))
    if report_id == MILLER_REPORT_ID:
        return build_miller_report(str(request.base_url))
    report = REPORT_DOCUMENTS.get(report_id)
    if report is None:
        raise HTTPException(404, f"未知报告: {report_id}")
    return report


@router.get("/api/report-snapshots/{snapshot_report_id}/versions/{version}")
def api_report_snapshot(snapshot_report_id: str, version: int):
    """只返回导出接口冻结的不可变阅读快照。"""

    try:
        snapshot = get_report_version(snapshot_report_id, version)
    except KeyError as exc:
        raise HTTPException(404, "报告导出快照不存在") from exc
    document = snapshot["document"]
    if document.get("document_type") != "reader-snapshot-v1":
        raise HTTPException(404, "报告导出快照不存在")
    return document["report_payload"]


@router.post("/api/reports/{report_id}/versions", status_code=201)
def api_freeze_report(report_id: str, payload: dict = Body(default={})):
    """把当前草稿冻结为新的不可变报告版本。"""

    try:
        return freeze_report(report_id, str(payload.get("created_by") or "原力"))
    except KeyError as exc:
        raise HTTPException(404, f"未知可编辑报告: {report_id}") from exc
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "INVALID_REPORT_DOCUMENT", "errors": exc.args[0]}) from exc


@router.post("/api/reports/{report_id}/duplicate", status_code=201)
def api_duplicate_report(report_id: str, request: Request, payload: dict = Body(default={})):
    """复制可编辑报告，或把内置只读报告转换为可编辑文档。"""

    try:
        return duplicate_report(report_id, str(payload.get("created_by") or "原力"))
    except KeyError:
        if report_id == GS_REPORT_ID:
            legacy = build_gs_report(str(request.base_url))
        elif report_id == MILLER_REPORT_ID:
            legacy = build_miller_report(str(request.base_url))
        else:
            legacy = REPORT_DOCUMENTS.get(report_id)
        if legacy is None:
            raise HTTPException(404, detail={"code": "REPORT_NOT_FOUND", "message": "报告不存在"})
        author = str(payload.get("created_by") or "原力")
        created = create_report({
            "title": f"{legacy['title']} 副本", "author": author,
            "goal": legacy.get("summary") or "基于只读报告创建的可编辑副本",
            "audience": "项目团队", "template": "blank", "key_questions": [],
        })
        document = created["document"]
        document["sections"] = []

        def editor_block(block_type: str, title: str = "", body: str = "", **extra):
            """把只读报告块转换为报告编排可编辑内容块。"""

            return {
                "id": f"block-{uuid.uuid4().hex[:10]}", "type": block_type, "title": title, "body": body,
                "source_ref": None, "layout": {"span": 12, "align": "stretch", "min_height": 120, "page_break_before": False, "keep_together": True, "hidden": False},
                "display": {"caption": "", "alt_text": title, "show_source": True}, **extra,
            }

        for legacy_section in legacy.get("sections", []):
            rows = []
            for legacy_block in legacy_section.get("blocks", []):
                block_type = legacy_block.get("type")
                if block_type == "metrics":
                    metrics = [editor_block("metric", item.get("label", "指标"), value=item.get("value", "—"), unit=item.get("unit", "")) for item in legacy_block.get("items", [])]
                    for start in range(0, len(metrics), 3):
                        chunk = metrics[start:start + 3]
                        for item in chunk:
                            item["layout"]["span"] = 12 // len(chunk)
                        rows.append({"id": f"row-{uuid.uuid4().hex[:8]}", "gap": 16, "align": "start", "blocks": chunk})
                    continue
                if block_type == "table":
                    converted = editor_block("table", legacy_block.get("title", "表格"), columns=legacy_block.get("columns", []), rows=legacy_block.get("rows", []))
                elif block_type == "markdown":
                    converted = editor_block("markdown", legacy_block.get("title", ""), legacy_block.get("body", ""))
                elif block_type in {"source", "source_link"}:
                    converted = editor_block("source", legacy_block.get("title", "来源"), legacy_block.get("body", ""))
                elif block_type == "error":
                    converted = editor_block("callout", legacy_block.get("title", "诊断"), f"{legacy_block.get('message', '')}\n\n恢复：{legacy_block.get('recovery', '')}")
                elif block_type == "example":
                    converted = editor_block("source", legacy_block.get("title", "案例引用"), f"原报告引用数据资产 `{legacy_block.get('artifact_id')}`。请从素材库加入已保存的可视化结果（Visualization）后替换本提示。")
                else:
                    converted = editor_block("markdown", legacy_block.get("title", "待重新编排的证据"), "该只读报告块已迁移为可编辑提示；请使用已保存的可视化结果（Visualization）重建交互证据。")
                rows.append({"id": f"row-{uuid.uuid4().hex[:8]}", "gap": 16, "align": "start", "blocks": [converted]})
            document["sections"].append({
                "id": f"section-{uuid.uuid4().hex[:8]}", "title": legacy_section.get("title", "未命名章节"),
                "description": "", "page_break_before": False,
                "rows": rows or [{"id": f"row-{uuid.uuid4().hex[:8]}", "gap": 16, "align": "start", "blocks": [editor_block("markdown", "待补充", "请补充可追溯内容。")]}],
            })
        return replace_draft(created["report_id"], created["draft_revision"], document)


@router.post("/api/reports/{report_id}/exports", status_code=202)
def api_create_report_export(report_id: str, request: Request, payload: dict = Body(...)):
    """冻结当前报告并创建异步 HTML 或 PDF 导出任务。"""

    export_format = payload.get("format")
    mode = payload.get("mode", "portable" if export_format == "html" else "static")
    if export_format not in {"pdf", "html"}:
        raise HTTPException(422, detail={"code": "INVALID_EXPORT_FORMAT", "legal": ["pdf", "html"]})
    if export_format == "html" and mode not in {"portable", "connected"}:
        raise HTTPException(422, detail={"code": "INVALID_HTML_MODE", "legal": ["portable", "connected"]})
    if export_format == "pdf":
        mode = "static"
    # Built-in reports are rendered by the React reader rather than stored as
    # ReportDocument drafts. Freeze their current API payload, then capture the
    # exact reader as a self-contained HTML or print PDF. This replaces the old
    # source-file links that incorrectly masqueraded as report downloads.
    try:
        get_draft(report_id)
        is_authored_report = True
    except KeyError:
        is_authored_report = False

    if is_authored_report:
        health_state = quarto_health()
        if health_state["state"] not in {"live", "stale"}:
            raise HTTPException(503, detail={"code": "QUARTO_UNAVAILABLE", **health_state})
        version = freeze_report(report_id, str(payload.get("created_by") or "原力"))
        export_report_id = report_id
    else:
        if report_id == GS_REPORT_ID:
            current_report = build_gs_report(str(request.base_url))
        elif report_id == MILLER_REPORT_ID:
            current_report = build_miller_report(str(request.base_url))
        else:
            current_report = REPORT_DOCUMENTS.get(report_id)
        if current_report is None:
            raise HTTPException(404, f"未知报告: {report_id}")
        snapshot_document = {
            "document_type": "reader-snapshot-v1",
            "source_report_id": report_id,
            "metadata": {
                "title": current_report.get("title", report_id),
                "author": current_report.get("author", "原力"),
                "generated_at": current_report.get("generated_at"),
            },
            "report_payload": current_report,
        }
        version = freeze_reader_snapshot(
            report_id, snapshot_document, str(payload.get("created_by") or "原力")
        )
        export_report_id = version["report_id"]
        mode = "static" if export_format == "pdf" else "portable"

    export = create_export(export_report_id, version["version"], export_format, mode)
    if payload.get("context_id"):
        runtime = request.app.state.runtime
        start_export(export["export_id"], vis_context=runtime.context(payload["context_id"]), vis_exports=runtime.exports)
    else:
        start_export(export["export_id"])
    return {**export, "source_report_id": report_id}


@router.get("/api/report-exports/{export_id}")
def api_report_export(export_id: str):
    """读取报告导出任务及当前阶段。"""

    try:
        return get_export(export_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知报告导出任务: {export_id}") from exc


@router.post("/api/report-exports/{export_id}/retry", status_code=202)
def api_retry_report_export(export_id: str, request: Request, payload: dict = Body(default={})):
    """重新提交失败或仍在排队的报告导出任务。"""

    try:
        export = get_export(export_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知报告导出任务: {export_id}") from exc
    if export["status"] not in {"failed", "queued"}:
        raise HTTPException(409, detail={"code": "EXPORT_NOT_RETRYABLE", "status": export["status"]})
    if payload.get("context_id"):
        runtime = request.app.state.runtime
        start_export(export_id, vis_context=runtime.context(payload["context_id"]), vis_exports=runtime.exports)
    else:
        start_export(export_id)
    return {**export, "status": "queued"}


@router.get("/api/report-exports/{export_id}/download")
def api_download_report_export(export_id: str):
    """在产物路径校验通过后下载已完成的报告文件。"""

    try:
        export = get_export(export_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知报告导出任务: {export_id}") from exc
    if export["status"] != "succeeded" or not export.get("output_path"):
        raise HTTPException(409, detail={"code": "EXPORT_NOT_READY", "status": export["status"], "stage": export["stage"]})
    target = Path(export["output_path"]).resolve()
    root = EXPORT_ROOT.resolve()
    if not target.is_file() or (target != root and root not in target.parents):
        raise HTTPException(404, "导出文件不存在")
    media_type = "application/pdf" if target.suffix == ".pdf" else "application/zip" if target.suffix == ".zip" else "text/html"
    return FileResponse(target, media_type=media_type, filename=target.name)


@router.get("/api/quarto/health")
def api_quarto_health():
    """返回报告导出所需 Quarto 运行时健康状态。"""

    return quarto_health()
