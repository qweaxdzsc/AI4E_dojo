"""图片及静态预览资产的 HTTP 适配层。

本模块只提供已登记预览文件，不生成物理场或几何业务结果；动画录制仍归
visPhysField，资产导出归 visIO。
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from infrastructure.config import REPOSITORY_ROOT


router = APIRouter(tags=["visFigure"])

ASSET_DIRECTORY = REPOSITORY_ROOT / "resources" / "examples" / "assets"
EXAMPLE_ASSETS = {
    "A-1112": ("temperature_fixed_camera.png", "image/png"),
    "A-1113": ("plume_evolution_silent.mp4", "video/mp4"),
    "A-1027-snapshot": ("o3dv_A-1027_fixed_camera.png", "image/png"),
    "A-1028-trame-snapshot": ("trame_A-1028_fixed_camera.png", "image/png"),
    "A-1029-trame-snapshot": ("trame_A-1029_fixed_camera.png", "image/png"),
    "A-1108-trame-snapshot": ("trame_A-1108_fixed_camera.png", "image/png"),
}


@router.get("/api/example-assets/{asset_id}")
def api_example_asset(asset_id: str) -> FileResponse:
    """返回白名单中的图片或视频预览资产。"""

    asset = EXAMPLE_ASSETS.get(asset_id)
    if asset is None:
        raise HTTPException(404, f"未知案例资产: {asset_id}")
    file_name, media_type = asset
    path = ASSET_DIRECTORY / file_name
    if not path.exists():
        raise HTTPException(404, f"案例资产尚未生成: {asset_id}")
    return FileResponse(path, media_type=media_type, filename=file_name)
