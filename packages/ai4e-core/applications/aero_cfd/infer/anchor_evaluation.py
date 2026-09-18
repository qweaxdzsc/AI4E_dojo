"""外流独立评估装配，复用训练相同的锚点评估口径。"""

from ai4e_core.abilities.eval.evaluation import evaluate


def evaluate_model(model, batches, *, predict, objectives, normalization, batch_context=None):
    """评估已经显式加载权重的模型，不修改训练状态。"""
    return evaluate(model, batches, predict, objectives, normalization, batch_context=batch_context)
