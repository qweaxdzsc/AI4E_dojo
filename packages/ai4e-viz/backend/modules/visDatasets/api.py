"""数据集解析、画像和质量检测的HTTP适配层。

资产列表、上传、分类和原始文件下载由dataAssets Router负责；本模块只暴露必须读取
文件内容的数据集能力，两个一级模块继续复用原有公开URL。
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from modules.reportManage.gradShafranovReport import ROOT as GS_FIXTURE_ROOT

from .pipeline import analyze_artifact


router = APIRouter(tags=["visDatasets"])

FIXTURE_MEDIA_TYPES = {
    ".csv": "text/csv", ".json": "application/json", ".npz": "application/octet-stream",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
}


@router.get("/api/artifact/{artifact_id}/parse")
def api_parse_dataset(artifact_id: str) -> dict:
    """解析一个已登记数据资产并返回真实文件内容画像。"""

    return analyze_artifact(artifact_id)["parse"]


@router.post("/api/artifacts/{artifact_id}/analyze")
def api_analyze_dataset(artifact_id: str) -> dict:
    """执行格式解析、数据画像、质量检测和语义类型推断。"""

    return analyze_artifact(artifact_id)


@router.get("/api/gs-fixture/{relative_path:path}")
def api_grad_shafranov_fixture(relative_path: str) -> FileResponse:
    """在路径边界校验后提供Grad-Shafranov数据集文件。"""

    root = GS_FIXTURE_ROOT.resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise HTTPException(404, "非法 fixture 路径")
    if not target.is_file():
        raise HTTPException(404, f"fixture 文件不存在: {relative_path}")
    return FileResponse(
        target, media_type=FIXTURE_MEDIA_TYPES.get(target.suffix.lower(), "application/octet-stream"),
        filename=target.name,
    )
