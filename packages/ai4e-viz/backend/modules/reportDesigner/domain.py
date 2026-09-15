"""报告编排领域规则：建立文档骨架并校验十二列布局与内容引用。

本文件只处理内存中的报告文档，不连接数据库，也不依赖报告管理模块。
报告管理模块需要创建或冻结文档时，只能通过 ``reportDesigner`` 的公开门面调用。
"""

from __future__ import annotations

import uuid
from typing import Any


# 内容块类型属于报告编排领域，而不是报告实体管理或导出领域。
BLOCK_TYPES = {
    "markdown", "visualization", "metric", "table", "image", "video",
    "callout", "divider", "toc", "source", "page_break", "diagnostic",
}


def _block(
    block_type: str,
    *,
    title: str = "",
    body: str = "",
    span: int = 12,
    source_ref: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """建立一个带稳定布局默认值的内容块。"""

    return {
        "id": f"block-{uuid.uuid4().hex[:10]}",
        "type": block_type,
        "title": title,
        "body": body,
        "source_ref": source_ref,
        "layout": {
            "span": span,
            "align": "stretch",
            "min_height": 120,
            "page_break_before": False,
            "keep_together": True,
            "hidden": False,
        },
        "display": {"caption": "", "alt_text": "", "show_source": True},
    }


def _section(title: str, placeholder: str) -> dict[str, Any]:
    """建立一个含默认文字占位块的报告章节。"""

    return {
        "id": f"section-{uuid.uuid4().hex[:8]}",
        "title": title,
        "description": "",
        "page_break_before": False,
        "rows": [{
            "id": f"row-{uuid.uuid4().hex[:8]}",
            "gap": 16,
            "align": "start",
            "blocks": [_block("markdown", title="待补充", body=placeholder)],
        }],
    }


def scaffold_document(brief: dict[str, Any]) -> dict[str, Any]:
    """根据报告简报建立可编辑文档骨架，不自动生成业务结论。"""

    template = brief.get("template", "analysis")
    templates = {
        "analysis": ["执行摘要", "数据与方法", "结果证据", "讨论", "结论", "来源"],
        "validation": ["执行摘要", "验证目标与判据", "数据与方法", "结果证据", "偏差与风险", "结论", "来源"],
        "weekly": ["本周结论", "进展与关键指标", "结果证据", "问题与风险", "下周计划", "来源"],
        "blank": ["未命名章节"],
    }
    titles = templates.get(template, templates["analysis"])
    goal = str(brief.get("goal") or "用户尚未填写项目目标")
    audience = str(brief.get("audience") or "项目团队")
    questions = brief.get("key_questions") or []
    question_text = "；".join(str(item) for item in questions) if questions else "尚未填写关键问题"
    sections = []
    for title in titles:
        if title in {"执行摘要", "本周结论"}:
            prompt = f"请面向{audience}总结可由证据支持的结论。当前目标：{goal}。系统不会自动虚构结论。"
        elif title in {"结果证据", "进展与关键指标"}:
            prompt = f"请从左侧素材库拖入已保存的可视化结果。需要回答：{question_text}。"
        elif title == "来源":
            prompt = "来源会根据加入报告的可视化结果自动汇总，也可以补充说明。"
        else:
            prompt = f"请补充“{title}”内容，并确保陈述能够追溯到数据或可视化证据。"
        sections.append(_section(title, prompt))
    return {
        "schema_version": "1.0",
        "metadata": {
            "title": str(brief.get("title") or "未命名报告"),
            "author": str(brief.get("author") or "原力"),
            "audience": audience,
            "goal": goal,
            "key_questions": questions,
        },
        "theme": {
            "page_size": brief.get("page_size", "A4"),
            "orientation": brief.get("orientation", "portrait"),
            "toc": True,
            "number_sections": True,
            "primary_color": "#1677FF",
            "accent_color": "#0E9F9F",
            "body_font": "Noto Sans CJK SC",
        },
        "sections": sections,
    }


def validate_document(document: Any) -> list[dict[str, Any]]:
    """校验报告章节、行、内容块、引用和十二列布局约束。"""

    errors: list[dict[str, Any]] = []
    if not isinstance(document, dict):
        return [{"path": "/", "message": "报告文档必须是对象"}]
    sections = document.get("sections")
    if not isinstance(sections, list) or not sections:
        return [{"path": "/sections", "message": "报告至少需要一个章节"}]
    if len(sections) > 50:
        errors.append({"path": "/sections", "message": "章节数量不能超过 50"})
    block_count = 0
    seen_ids: set[str] = set()
    for section_index, section in enumerate(sections):
        path = f"/sections/{section_index}"
        if not isinstance(section, dict) or not section.get("id") or not isinstance(section.get("rows"), list):
            errors.append({"path": path, "message": "章节缺少 id 或 rows"})
            continue
        for row_index, row in enumerate(section["rows"]):
            row_path = f"{path}/rows/{row_index}"
            if not isinstance(row, dict) or not row.get("id") or not isinstance(row.get("blocks"), list):
                errors.append({"path": row_path, "message": "行缺少 id 或 blocks"})
                continue
            span_total = 0
            for block_index, block in enumerate(row["blocks"]):
                block_count += 1
                block_path = f"{row_path}/blocks/{block_index}"
                if not isinstance(block, dict) or block.get("type") not in BLOCK_TYPES:
                    errors.append({"path": f"{block_path}/type", "message": "不支持的报告块类型"})
                    continue
                block_id = block.get("id")
                if not block_id or block_id in seen_ids:
                    errors.append({"path": f"{block_path}/id", "message": "块 ID 缺失或重复"})
                else:
                    seen_ids.add(block_id)
                if block.get("type") == "visualization":
                    source_ref = block.get("source_ref")
                    required = {"artifact_id", "visualization_id", "spec_id", "spec_version", "content_hash"}
                    if isinstance(source_ref, dict) and "revision" in source_ref:
                        required = {"project_id", "task_id", "visualization_id", "revision", "content_hash"}
                        if not isinstance(source_ref["revision"], int) or isinstance(source_ref["revision"], bool) or source_ref["revision"] < 1:
                            errors.append({"path": f"{block_path}/source_ref/revision", "message": "配置修订必须是正整数"})
                    if not isinstance(source_ref, dict) or not required.issubset(source_ref) or not all(source_ref.get(key) is not None for key in required):
                        errors.append({"path": f"{block_path}/source_ref", "message": "可视化结果块必须冻结数据资产、结果、Spec 版本和 content_hash"})
                span = (block.get("layout") or {}).get("span", 12)
                if not isinstance(span, int) or not 1 <= span <= 12:
                    errors.append({"path": f"{block_path}/layout/span", "message": "span 必须是 1 到 12 的整数"})
                else:
                    span_total += span
            if span_total > 12:
                errors.append({"path": f"{row_path}/blocks", "message": "同一行的列宽总和不能超过 12"})
    if block_count > 1000:
        errors.append({"path": "/sections", "message": "报告块数量不能超过 1000"})
    return errors


__all__ = ["BLOCK_TYPES", "scaffold_document", "validate_document"]
