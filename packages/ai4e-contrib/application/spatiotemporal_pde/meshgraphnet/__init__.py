"""MeshGraphNet 的时空预测连接。"""

from .inference import evaluation_rollout_input, rollout_prediction
from .model import build_graph, build_model

__all__ = ["build_graph", "build_model", "evaluation_rollout_input", "rollout_prediction"]
