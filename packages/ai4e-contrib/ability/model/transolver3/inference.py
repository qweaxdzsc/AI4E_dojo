"""全表面物理状态缓存与解码；保留参考逐层、逐块计算顺序。"""

import torch

from .amortize import FullMeshDecodingModel, PhysicalStateCachingModel


class SurfaceInference:
    """同一权重构造缓存与解码模型；缓存仅存活于一个样本。"""

    def __init__(self, model):
        device = next(model.parameters()).device
        self.caching = PhysicalStateCachingModel(**model.dojo_parameters).to(device).float().eval()
        self.decoding = FullMeshDecodingModel(**model.dojo_parameters).to(device).float().eval()
        self.caching.load_state_dict(model.state_dict(), strict=True)
        self.decoding.load_state_dict(model.state_dict(), strict=True)
        self.layers = model.dojo_parameters["n_layers"]
        self.device = device

    @torch.no_grad()
    def predict(self, chunks, *, observer=None, query_chunk_size=None):
        """chunks 为可重新遍历的输入工厂，返回保留身份的归一化预测块。"""
        cache = []
        try:
            for layer in range(self.layers):
                numerator = denominator = None
                for identity, inputs in chunks():
                    tensor = inputs["features"].to(self.device)
                    _, num, den = self.caching([tensor], cache, layer, use_checkpoint=False)
                    numerator = num if numerator is None else numerator + num
                    denominator = den if denominator is None else denominator + den
                if numerator is None:
                    raise ValueError("物理状态缓存没有输入块")
                state = numerator / (denominator[..., None] + 1e-5)
                cache.append(state)
                if observer:
                    observer("cache", layer, state)
            for identity, inputs in chunks():
                tensor = inputs["features"].to(self.device)
                size = query_chunk_size if query_chunk_size is not None else tensor.shape[1]
                if isinstance(size, bool) or not isinstance(size, int) or size < 1:
                    raise ValueError("查询块大小必须为正整数")
                for start in range(0, tensor.shape[1], size):
                    value = self.decoding(
                        [tensor[:, start : start + size]], cache, use_checkpoint=False
                    )[0]
                    selected = (
                        identity if query_chunk_size is None else identity[start : start + size]
                    )
                    yield selected, {"fields": value}
        finally:
            cache.clear()
