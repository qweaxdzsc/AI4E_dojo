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

from .visualization import VisualizationRef, VisualizationSession, VisualizationStorageScope
from .visualization import VisualizationSourceRef, VisualizationExportRef

from .platform import RawprepDescriptor, DatasetDescriptor

__all__ += ["RawprepDescriptor", "DatasetDescriptor"]

from .inference import InferenceCheckpointRef, InferenceRequest, InferenceResultRef

__all__ += ["InferenceCheckpointRef", "InferenceRequest", "InferenceResultRef"]

from .inference import InferenceSampleSelection, InferenceFieldDescription, InferenceMetricDescription, InferenceStatistic

__all__ += ["InferenceSampleSelection", "InferenceFieldDescription", "InferenceMetricDescription", "InferenceStatistic"]
