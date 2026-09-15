"""数据资产列表、详情、分类、文件读取和上传的HTTP适配层。

Router只转换HTTP请求与错误；资产业务由application编排，SQL只存在于本模块Repository。
公开URL保持不变，确保重构前保存的数据和前端书签继续可用。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .application import (
    classify_data_asset, get_data_asset, list_data_assets, register_uploaded_asset,
    resolve_data_asset_file,
)


router = APIRouter(tags=["dataAssets"])

MEDIA_TYPES = {
    ".stl": "model/stl", ".ply": "application/octet-stream", ".obj": "model/obj",
    ".vtu": "application/octet-stream", ".vti": "application/octet-stream",
    ".vts": "application/octet-stream", ".vtm": "application/octet-stream",
    ".csv": "text/csv", ".parquet": "application/octet-stream", ".npz": "application/octet-stream",
    ".json": "application/json", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".md": "text/markdown; charset=utf-8",
    ".markdown": "text/markdown; charset=utf-8", ".html": "text/html; charset=utf-8",
    ".pt": "application/octet-stream", ".glb": "model/gltf-binary",
}


@router.get("/api/artifacts")
def api_list_data_assets() -> dict:
    """返回数据资产列表及兼容旧前端的artifacts字段。"""

    items = list_data_assets()
    return {"items": items, "artifacts": items, "updated_at": max((item["updated_at"] for item in items), default=None)}


@router.get("/api/artifacts/{artifact_id}")
def api_data_asset_detail(artifact_id: str) -> dict:
    """返回一个数据资产详情，首次访问时允许触发内容分析。"""

    try:
        return get_data_asset(artifact_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}") from exc


@router.patch("/api/artifacts/{artifact_id}/classification")
def api_classify_data_asset(artifact_id: str, payload: dict = Body(...)) -> dict:
    """保存用户分类修正及原因，并返回刷新后的分析结果。"""

    declared_kind = payload.get("declared_kind")
    reason = str(payload.get("reason") or "用户根据解析结果修正分类")
    try:
        return classify_data_asset(artifact_id, declared_kind, reason)
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "INVALID_DECLARED_KIND", "message": str(exc)}) from exc
    except KeyError as exc:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}") from exc


@router.get("/api/artifact/{artifact_id}/file/{file_name}")
def api_data_asset_file(artifact_id: str, file_name: str) -> FileResponse:
    """校验登记文件名后返回资产原始字节，防止路径穿越。"""

    try:
        metadata, raw_path = resolve_data_asset_file(artifact_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}") from exc
    path = Path(raw_path)
    if path.name != file_name and metadata.get("file") != file_name:
        raise HTTPException(404, f"文件名与登记不符: {file_name}")
    if not path.is_file():
        raise HTTPException(404, f"数据文件不存在: {file_name}")
    return FileResponse(path, media_type=MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream"), filename=path.name)


async def _store_upload(file: UploadFile, declared_kind: str, dataset_id: str | None) -> dict:
    """读取一个上传文件并把应用异常转换为HTTP错误。"""

    try:
        return register_uploaded_asset(file.filename or "upload.bin", await file.read(), declared_kind, dataset_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.post("/api/artifacts", status_code=201)
async def api_upload_data_assets(
    files: list[UploadFile] = File(...), declared_kind: str = Form("auto"),
    dataset_id: str | None = Form(None),
) -> dict:
    """上传一个或多个文件，并返回逐文件登记与分析结果。"""

    results = [await _store_upload(file, declared_kind, dataset_id) for file in files]
    return {"items": results, "count": len(results)}


@router.post("/api/upload")
async def api_upload_legacy(
    file: UploadFile = File(...), declared_kind: str = Form("auto"),
    dataset_id: str | None = Form(None),
) -> dict:
    """保留旧单文件上传URL，并返回旧前端使用的recommend字段。"""

    result = await _store_upload(file, declared_kind, dataset_id)
    return {**result, "recommend": result.get("recommendations")}
