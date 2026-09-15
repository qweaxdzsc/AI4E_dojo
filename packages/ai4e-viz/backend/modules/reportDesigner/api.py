"""报告编排草稿的 HTTP 适配层。

Router 只解析修订号与文档请求，并把领域/Repository 异常转换为稳定错误码；草稿 SQL
和乐观锁事务仍由本模块 Repository 管理。
"""

from fastapi import APIRouter, Body, HTTPException

from .application import get_draft, replace_draft


router = APIRouter(tags=["reportDesigner"])


@router.get("/api/reports/{report_id}/draft")
def api_report_draft(report_id: str) -> dict:
    """读取可编辑报告草稿和当前修订号。"""

    try:
        return get_draft(report_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知可编辑报告: {report_id}") from exc


@router.patch("/api/reports/{report_id}/draft")
def api_update_report_draft(report_id: str, payload: dict = Body(...)) -> dict:
    """用乐观锁保存完整报告文档，并返回新的修订号。"""

    base_revision = payload.get("base_revision")
    if not isinstance(base_revision, int):
        raise HTTPException(422, detail={"code": "BASE_REVISION_REQUIRED", "field": "base_revision"})
    try:
        return replace_draft(report_id, base_revision, payload.get("document"))
    except KeyError as exc:
        raise HTTPException(404, f"未知可编辑报告: {report_id}") from exc
    except PermissionError as exc:
        raise HTTPException(409, detail={"code": "REPORT_READ_ONLY", "message": "内置报告需要复制后编辑"}) from exc
    except RuntimeError as exc:
        raise HTTPException(409, detail={"code": "STALE_DRAFT_REVISION", "expected": int(str(exc)), "received": base_revision}) from exc
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "INVALID_REPORT_DOCUMENT", "errors": exc.args[0]}) from exc
