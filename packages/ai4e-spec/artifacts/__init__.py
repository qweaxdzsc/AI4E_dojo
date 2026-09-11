"""跨包运行溯源与预览契约。"""

from .platform import AssetRef, DisplayAssetManifest, FieldDescriptor, Operation, SceneDocument
from .preview import PreviewRequest, PreviewResult
from .run import RunContext

__all__ = [
    "AssetRef",
    "DisplayAssetManifest",
    "FieldDescriptor",
    "Operation",
    "PreviewRequest",
    "PreviewResult",
    "RunContext",
    "SceneDocument",
]
