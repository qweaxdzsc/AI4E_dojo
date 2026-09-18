"""无梯度推理的模式保护；可选隔离调用方随机流。"""

from collections.abc import Iterator
from contextlib import contextmanager, nullcontext

import torch

from .randomness import preserve_randomness


@contextmanager
def inference_execution(model, *, preserve_rng: bool = True) -> Iterator[None]:
    """成功或失败均恢复每个子模块模式；同一批内可共享受外层保护的随机流。"""
    modes = {module: module.training for module in model.modules()}
    try:
        with preserve_randomness() if preserve_rng else nullcontext():
            model.eval()
            with torch.no_grad():
                yield
    finally:
        for module, mode in modes.items():
            module.training = mode


@contextmanager
def inference_group(models, *, preserve_rng: bool = True):
    """整个模型组共用一次随机上下文；成功、异常时恢复全部子模块模式。"""
    from contextlib import ExitStack

    with ExitStack() as stack:
        if preserve_rng:
            stack.enter_context(preserve_randomness())
        for model in models:
            stack.enter_context(inference_execution(model, preserve_rng=False))
        yield
