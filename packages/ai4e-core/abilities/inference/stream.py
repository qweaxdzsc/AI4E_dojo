"""流式推理执行；模型组件拥有算法，框架拥有模式和资源边界。"""

import torch


def predict_stream(model, chunks, *, factory, observer=None):
    """注入专用推理组件；正常结束或异常退出都恢复模型模式。"""
    modes = {module: module.training for module in model.modules()}
    try:
        model.eval()
        with torch.no_grad():
            context = factory(model)
            yield from context.predict(chunks, observer=observer)
    finally:
        for module, mode in modes.items():
            module.training = mode
