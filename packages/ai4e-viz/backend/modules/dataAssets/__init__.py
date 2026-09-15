"""数据资产一级模块公开门面。"""

from .application import (
    classify_data_asset, get_data_asset, list_data_assets, register_uploaded_asset,
    resolve_data_asset_file,
)
from .repository import (
    find_uploaded_by_sha256, get_artifact, list_artifacts, save_analysis,
    save_analysis_error, store_uploaded_bytes, update_classification, upsert_artifact,
)

__all__ = [
    "classify_data_asset", "find_uploaded_by_sha256", "get_artifact", "get_data_asset",
    "list_artifacts", "list_data_assets", "register_uploaded_asset", "resolve_data_asset_file",
    "save_analysis", "save_analysis_error", "store_uploaded_bytes", "update_classification", "upsert_artifact",
]

from .externalSources import fingerprint as source_fingerprint, resolve_external, dependency_snapshot
