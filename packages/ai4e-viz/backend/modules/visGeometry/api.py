"""几何可视化及 O3DV 派生表现的 HTTP 适配层。

几何模块通过dataAssets公开门面取得源文件，通过visDatasets完成内容分析，再由
visConvertor公开门面生成GLB；
派生文件写入统一运行目录，不在源码树建立缓存、Server 或业务数据库。
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from infrastructure.config import runtime_paths
from modules.dataAssets import get_artifact, resolve_data_asset_file
from modules.visConvertor import convert_to_glb
from modules.visDatasets import analyze_artifact, ensure_builtin_artifacts


router = APIRouter(tags=["visGeometry"])


@router.get("/api/artifact/{artifact_id}/representation/o3dv.glb")
def api_o3dv_representation(artifact_id: str) -> FileResponse:
    """返回源 GLB 或从真实几何源生成的可重建 O3DV GLB 表现。"""

    ensure_builtin_artifacts()
    try:
        stored = get_artifact(artifact_id)
    except KeyError as exc:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}") from exc
    if stored["parse_status"] != "ready":
        analyze_artifact(artifact_id)
        stored = get_artifact(artifact_id)
    inferred_kind = (stored.get("profile") or {}).get("inferred_kind") or stored.get("detected_kind")
    if inferred_kind != "mesh":
        raise HTTPException(404, f"Artifact 没有 O3DV 表示: {artifact_id}")
    _, source_path = resolve_data_asset_file(artifact_id)
    source = Path(source_path)
    if not source.exists():
        raise HTTPException(404, f"源模型不存在: {artifact_id}")
    if source.suffix.lower() == ".glb":
        return FileResponse(source, media_type="model/gltf-binary", filename=f"{artifact_id}.glb")
    conversion_directory = runtime_paths().derived / "conversions"
    conversion_directory.mkdir(parents=True, exist_ok=True)
    output = conversion_directory / f"{artifact_id}.glb"
    try:
        convert_to_glb(str(source), str(output))
    except Exception as exc:  # noqa: BLE001 - 适配层必须转换第三方转换器异常
        raise HTTPException(500, f"O3DV 表示转换失败: {exc}") from exc
    return FileResponse(output, media_type="model/gltf-binary", filename=f"{artifact_id}.glb")


@router.get("/api/artifacts/{artifact_id}/representations/{name}")
def api_artifact_representation(artifact_id: str, name: str) -> FileResponse:
    """通过统一派生表现 URL 兼容 O3DV GLB 名称。"""

    if name != "o3dv.glb":
        raise HTTPException(404, f"未知派生表示: {name}")
    return api_o3dv_representation(artifact_id)
