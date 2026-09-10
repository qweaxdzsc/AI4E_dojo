"""仅限无梯度评估的模型绑定缓存与分块查询生命周期。"""

from dataclasses import dataclass

import torch


def model_signature(model):
    """对象身份和版本计数检测正常更新、加载及设备/精度变更。"""
    return (
        id(model),
        getattr(model, "_cache_generation", 0),
        tuple(
            (name, id(t), t._version, str(t.device), str(t.dtype))
            for name, t in list(model.named_parameters()) + list(model.named_buffers())
        ),
        tuple(m.training for m in model.modules()),
        model.layout.signature,
    )


@dataclass
class ModelCache:
    """进程内推理状态，不允许序列化为检查点。"""

    signature: tuple
    geometry: torch.Tensor
    geometry_rope: torch.Tensor
    condition: torch.Tensor | None
    geometry_condition: torch.Tensor | None
    batch_size: int
    physics: list | None = None
    decoders: dict | None = None
    valid: bool = True

    def validate(self, model):
        if not self.valid or model.training or torch.is_grad_enabled():
            raise ValueError("缓存仅限有效上下文中的无梯度 eval")
        if self.signature != model_signature(model):
            raise ValueError("缓存模型、权重、设备、精度或模式已改变")
        if torch.is_autocast_enabled(self.geometry.device.type):
            raise ValueError("缓存推理不允许自动混合精度，请显式转换模型和输入")
        if (self.physics is None) != (self.decoders is None):
            raise ValueError("缓存层载荷不完整")
        if self.physics is not None and (
            len(self.physics) != len(model.blocks)
            or set(self.decoders) != set(model.layout.domains)
        ):
            raise ValueError("缓存层布局不完整")
        if self.decoders is not None and any(
            len(self.decoders[d]) != len(model.decoders[d]) for d in self.decoders
        ):
            raise ValueError("域解码缓存层缺失")

    def geometry_only(self):
        """保留几何编码，允许重新编码 anchors；几何条件必须一致。"""
        if not self.valid:
            raise ValueError("缓存已经释放")
        return ModelCache(
            self.signature,
            self.geometry,
            self.geometry_rope,
            None,
            self.geometry_condition,
            self.batch_size,
        )

    def __getstate__(self):
        raise TypeError("推理缓存不能序列化或写入检查点")


class InferenceContext:
    """绑定准备记录，预填充一次并显式释放缓存。"""

    def __init__(self, model, inputs, *, preparation_id):
        if not preparation_id:
            raise ValueError("推理上下文必须绑定准备记录")
        if model.training or torch.is_grad_enabled():
            raise ValueError("推理上下文需要 eval 和 no_grad")
        if inputs.get("domain_query_positions"):
            raise ValueError("预填充仅接受 anchors")
        self.model, self.preparation_id = model, preparation_id
        self.predictions, self.cache = model(**inputs, return_cache=True)

    def query(self, positions, *, features=None, preparation_id):
        """只改变查询坐标和局部查询特征，不改变锚点或条件。"""
        if preparation_id != self.preparation_id:
            raise ValueError("缓存准备记录冲突")
        return self.model(
            domain_query_positions=positions, domain_query_features=features, kv_cache=self.cache
        )[0]

    def chunks(self, positions, *, features=None, chunk_size=1024, preparation_id):
        """按域分别分块，拼接恢复查询顺序。"""
        if chunk_size <= 0 or not positions:
            raise ValueError("查询及分块预算必须非空且为正")
        if features and set(features) - set(positions):
            raise ValueError("查询特征没有对应坐标域")
        result = {}
        for domain, points in positions.items():
            if points.ndim != 3 or points.shape[1] == 0:
                raise ValueError("查询必须为非空 (B,N,3)")
            pieces = {}
            for start in range(0, points.shape[1], chunk_size):
                feats = (
                    {domain: features[domain][:, start : start + chunk_size]}
                    if features and domain in features
                    else None
                )
                output = self.query(
                    {domain: points[:, start : start + chunk_size]},
                    features=feats,
                    preparation_id=preparation_id,
                )
                for name, tensor in output.items():
                    pieces.setdefault(name, []).append(tensor)
            result.update({name: torch.cat(values, dim=1) for name, values in pieces.items()})
        return result

    def close(self):
        """释放所有持有的张量并使后续调用失败。"""
        self.cache.valid = False
        self.cache.geometry = self.cache.geometry_rope = None
        self.cache.physics = self.cache.decoders = None
        self.cache.condition = self.cache.geometry_condition = None
        self.predictions = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
