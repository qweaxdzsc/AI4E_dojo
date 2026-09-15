"""数据集解析、画像、体检、统计和内容查看模块公开入口。"""

from .inspection import inspect_profile
from .pipeline import (
    analyze_artifact, artifact_to_public_dto, build_example, ensure_builtin_artifacts,
    recommend_artifact, supported_kind_names, supported_upload_formats,
)

__all__ = [
    "analyze_artifact", "artifact_to_public_dto", "build_example", "ensure_builtin_artifacts",
    "inspect_profile", "recommend_artifact", "supported_kind_names", "supported_upload_formats",
]

from .physicalDataset import (
    describe_physical,
    list_named_blocks,
    list_named_surfaces,
    load_physical,
    source_times,
)
