"""公开推理原子能力：权重恢复、预测、查询与模式保护。"""

from .execution import inference_execution
from .prediction import predict
from .query import query_model
from .rebuild import model_restore_contract, rebuild
from .stream import predict_stream

__all__ = [
    "inference_execution",
    "model_restore_contract",
    "predict",
    "predict_stream",
    "query_model",
    "rebuild",
]

from .timing import measure

__all__ += ["measure"]
