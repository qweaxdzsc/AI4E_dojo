"""MeshGraphNet 模型本体；通用图原语由 ai4e-core 提供。"""

from .network import MeshGraphNet
from .static import StaticMeshGraphNet

__all__ = ["MeshGraphNet", "StaticMeshGraphNet"]
