"""通过注入的模型上下文执行分块查询，并保证异常时释放资源和恢复模式。"""

import torch


def query_model(
    model, inputs, positions, *, context_factory, preparation_id, features=None, chunk_size=1024
):
    """按查询顺序返回预测，结束或失败后释放缓存并恢复各模块模式。"""
    modes = {module: module.training for module in model.modules()}
    try:
        model.eval()
        with (
            torch.no_grad(),
            context_factory(model, inputs, preparation_id=preparation_id) as context,
        ):
            return context.chunks(
                positions, features=features, chunk_size=chunk_size, preparation_id=preparation_id
            )
    finally:
        for module, mode in modes.items():
            module.training = mode
