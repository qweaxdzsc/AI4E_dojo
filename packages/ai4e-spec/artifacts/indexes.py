"""运行资产和指标索引的轻量格式，不规定科学数据格式。"""

import math

INDEX_VERSION = 1
ASSET_KINDS = frozenset({"dataset", "preparation", "checkpoint", "model_preset", "other"})


def validate_asset_record(record: dict) -> None:
    """校验可持久化资产信息；内容校验由文件消费者承担。"""
    for key in ("name", "stage", "path", "digest"):
        if not isinstance(record.get(key), str) or not record[key]:
            raise ValueError(f"invalid_asset_{key}")
    if record.get("kind") not in ASSET_KINDS:
        raise ValueError("invalid_asset_kind")
    if not isinstance(record.get("dependencies"), list):
        raise TypeError("asset_dependencies_required")
    if any(not isinstance(p, str) or not p for p in record["dependencies"]):
        raise TypeError("asset_dependencies_must_be_paths")


def validate_metric_record(record: dict) -> None:
    """缺失指标语义不允许冒充可比较科学指标。"""
    value = record.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("metric_must_be_finite")
    for key in ("name", "stage"):
        if not isinstance(record.get(key), str) or not record[key]:
            raise ValueError(f"invalid_metric_{key}")
    semantics = record.get("semantics")
    for key in ("field", "unit", "split", "statistic", "data_identity"):
        if not isinstance(semantics, dict) or semantics.get(key) in (None, "", {}, []):
            raise ValueError(f"metric_semantics_required: {key}")
    if not isinstance(record.get("assets"), list) or not record["assets"]:
        raise ValueError("metric_assets_required")
