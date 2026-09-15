"""数据资产登记、上传、分类和文件定位的应用用例。

本模块拥有资产生命周期与持久化；格式解析、画像和数据质量仍调用visDatasets公开门面。
采用函数内延迟导入可避免两个限界上下文初始化时形成循环依赖。
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from infrastructure.config import runtime_paths

from .repository import (
    find_uploaded_by_sha256, get_artifact, list_artifacts, store_uploaded_bytes,
    update_classification, upsert_artifact,
)

UPLOAD_DIR = runtime_paths().objects / "datasets"


def _dataset_services():
    """延迟取得数据集解析公开能力，避免导入模块内部文件。"""

    from modules.visDatasets import (
        analyze_artifact, artifact_to_public_dto, ensure_builtin_artifacts,
        supported_kind_names, supported_upload_formats,
    )

    return (
        analyze_artifact, artifact_to_public_dto, ensure_builtin_artifacts,
        supported_kind_names, supported_upload_formats,
    )


def list_data_assets() -> list[dict[str, Any]]:
    """列出已经登记的全部数据资产，并转换为稳定公开DTO。"""

    _, to_public, ensure_builtin, _, _ = _dataset_services()
    ensure_builtin()
    return [to_public(item) for item in list_artifacts()]


def get_data_asset(artifact_id: str, *, analyze_if_needed: bool = True) -> dict[str, Any]:
    """读取一个数据资产；必要时触发visDatasets完成首次内容分析。"""

    analyze, to_public, ensure_builtin, _, _ = _dataset_services()
    ensure_builtin()
    item = get_artifact(artifact_id)
    if analyze_if_needed and item["parse_status"] not in {"ready", "error"}:
        analyze(artifact_id)
        item = get_artifact(artifact_id)
    return to_public(item)


def classify_data_asset(artifact_id: str, declared_kind: str, reason: str) -> dict[str, Any]:
    """创建新的资产分类版本，并用数据集解析能力刷新画像与推荐输入。"""

    analyze, _, _, kind_names, _ = _dataset_services()
    legal = kind_names()
    if declared_kind not in legal:
        raise ValueError(f"不支持的数据语义类型: {declared_kind}")
    update_classification(artifact_id, declared_kind, reason)
    return analyze(artifact_id)


def register_uploaded_asset(
    file_name: str, content: bytes, declared_kind: str = "auto",
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """按SHA-256保存上传字节、登记资产，再调用visDatasets分析文件内容。"""

    if not content:
        raise ValueError("空文件")
    safe_name = Path(file_name or "upload.bin").name
    extension = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    analyze, to_public, _, _, upload_formats = _dataset_services()
    formats = upload_formats()
    file_format = formats.get(extension)
    if file_format is None:
        raise ValueError(f"暂不支持的扩展名 .{extension}；支持 {', '.join(sorted(formats))}")

    digest = hashlib.sha256(content).hexdigest()
    existing = find_uploaded_by_sha256(digest)
    if existing is not None:
        if existing["parse_status"] != "ready":
            analyze(existing["artifact_id"])
            existing = get_artifact(existing["artifact_id"])
        return {
            "deduplicated": True, "artifact": to_public(existing),
            "parse": existing.get("profile"), "recommendations": existing.get("recommendations"),
        }

    artifact_id = f"U-{digest[:8].upper()}"
    destination = store_uploaded_bytes(content, safe_name, digest, UPLOAD_DIR)
    upsert_artifact({
        "artifact_id": artifact_id, "name": safe_name.rsplit(".", 1)[0].replace("_", " "),
        "file_name": safe_name, "file_path": destination, "format": file_format,
        "sha256": digest, "size_bytes": len(content), "declared_kind": declared_kind or "auto",
        "dataset_id": dataset_id, "source": "uploaded",
    })
    try:
        analysis = analyze(artifact_id)
        return {
            "deduplicated": False, "artifact": to_public(analysis["artifact"]),
            "parse": analysis["parse"], "recommendations": analysis["recommendations"],
            "artifact_id": artifact_id,
        }
    except HTTPException as exc:
        # 解析失败不能回滚已经安全落盘的原始资产；前端仍需拿到资产ID和可追溯诊断。
        stored = get_artifact(artifact_id)
        return {
            "deduplicated": False, "artifact": to_public(stored), "error": exc.detail,
            "artifact_id": artifact_id,
        }


def resolve_data_asset_file(artifact_id: str) -> tuple[dict[str, Any], str]:
    """返回资产登记元数据与解析后的真实文件路径。"""

    _, _, ensure_builtin, _, _ = _dataset_services()
    ensure_builtin()
    stored = get_artifact(artifact_id)
    metadata = {
        "file": stored["file_name"], "path": stored["file_path"], "format": stored["format"],
        "declared_kind": stored["declared_kind"], "name": stored["name"], "source": stored["source"],
    }
    return metadata, stored["file_path"]
