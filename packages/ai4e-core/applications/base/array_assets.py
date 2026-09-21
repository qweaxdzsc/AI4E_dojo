"""具名数组/网格目录与管理资产的公开交接。"""

from pathlib import Path


def record_bundle(session, name, manifest, *, kind, stage):
    """登记自包含目录的全部文件依赖，复制后不依赖原始来源路径。"""
    manifest = Path(manifest).resolve()
    dependencies = [
        path for path in manifest.parent.rglob("*") if path.is_file() and path != manifest
    ]
    return session.record_asset(
        name,
        manifest,
        kind=kind,
        stage=stage,
        dependencies=dependencies,
        bundle_root=manifest.parent,
    )
