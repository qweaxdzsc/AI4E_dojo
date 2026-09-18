"""AB-UPT 多域骨干：显式域布局、条件调制与逐层推理缓存。"""

import torch
from torch import nn

from ai4e_core.abilities.modeling.modules.position_encoding import (
    ContinuousSincosEmbed,
    RopeFrequency,
)

from .domains import DomainLayout
from .inference import ModelCache, model_signature
from .modules.blocks.domain import DomainBlock, DomainReadout, initialize_linear
from .modules.supernode_pooling_posonly import SupernodePoolingPosonly


class AnchoredBranchedUPT(nn.Module):
    """新版本命名域模型；不接受旧双域扁平参数或状态字典。"""

    structure_version = 3

    def train(self, mode=True):
        """进入训练即永久撤销此前创建的推理缓存。"""
        if mode:
            self._cache_generation = getattr(self, "_cache_generation", 0) + 1
        return super().train(mode)

    def __init__(
        self,
        *,
        data_specs,
        dim=192,
        geometry_depth=6,
        num_heads=3,
        blocks="pscscscscsc",
        num_domain_decoder_blocks=None,
        radius=9.0,
        geometry_conditioning_dims=None,
        geometry_position_mode="abspos",
        require_features=True,
    ):
        super().__init__()
        self.require_features = require_features
        self.layout = DomainLayout(data_specs, geometry_conditioning_dims)
        if dim <= 0 or num_heads <= 0 or dim % num_heads or (dim // num_heads) % 2:
            raise ValueError("隐藏维数必须整除头数且每头维数为偶数")
        if geometry_depth < 0 or not blocks or set(blocks) - set("psc"):
            raise ValueError("非法深度或物理块声明")
        if "c" in blocks and len(self.layout.domains) < 2:
            raise ValueError("跨域注意力至少需要两个域")
        depths = (
            num_domain_decoder_blocks
            if num_domain_decoder_blocks is not None
            else {d: 12 for d in self.layout.domains}
        )
        if set(depths) != set(self.layout.domains) or any(
            type(n) is not int or n < 0 for n in depths.values()
        ):
            raise ValueError("每域解码深度必须明确且非负")
        self.rope = RopeFrequency(dim=dim // num_heads, ndim=3)
        self.pos_embed = ContinuousSincosEmbed(dim=dim, ndim=3)
        # 模块按官方构造顺序局部初始化，避免末尾整体重置改变相同种子的初值。
        self.biases = nn.ModuleDict({d: self._mlp(dim, dim, dim) for d in self.layout.domains})
        self.block_types = tuple(blocks)
        self.blocks = nn.ModuleList(
            [
                DomainBlock(dim, num_heads, bool(self.layout.conditions), perceiver=k == "p")
                for k in blocks
            ]
        )
        self.encoder = SupernodePoolingPosonly(
            hidden_dim=dim, ndim=3, radius=radius, mode=geometry_position_mode
        )
        self.geometry_blocks = nn.ModuleList(
            [
                DomainBlock(dim, num_heads, bool(self.layout.geometry_conditions))
                for _ in range(geometry_depth)
            ]
        )
        self.feature_projections = nn.ModuleDict(
            {
                d: self._mlp(sum(w for _, w in fields), dim, dim)
                for d, fields in self.layout.features.items()
                if fields
            }
        )
        self.decoders = nn.ModuleDict(
            {
                d: nn.ModuleList(
                    [
                        DomainBlock(dim, num_heads, bool(self.layout.conditions))
                        for _ in range(depths[d])
                    ]
                )
                for d in self.layout.domains
            }
        )
        self.readouts = nn.ModuleDict(
            {
                d: DomainReadout(
                    dim, sum(w for _, w in self.layout.outputs[d]), bool(self.layout.conditions)
                )
                for d in self.layout.domains
            }
        )
        self.conditioner = self._conditioner(self.layout.conditions, dim)
        self.geometry_conditioner = (
            None
            if self.layout.inherit_geometry
            else self._conditioner(self.layout.geometry_conditions, dim)
        )

    @staticmethod
    def _mlp(inputs, hidden, outputs):
        module = nn.Sequential(nn.Linear(inputs, hidden), nn.GELU(), nn.Linear(hidden, outputs))
        module.apply(initialize_linear)
        return module

    @staticmethod
    def _conditioner(fields, dim):
        return (
            nn.Sequential(nn.Linear(sum(w for _, w in fields), dim), nn.SiLU(), nn.Linear(dim, dim))
            if fields
            else None
        )

    def _tensor(self, value, shape, label, *, integer=False):
        parameter = next(self.parameters())
        dtype = torch.long if integer else parameter.dtype
        if not isinstance(value, torch.Tensor):
            raise ValueError(  # noqa: TRY004 - 保留公开输入契约既有的 ValueError
                f"{label} 输入类型不匹配: expected=Tensor actual={type(value).__name__}"
            )
        if value.shape != shape:
            raise ValueError(
                f"{label} 形状不匹配: expected={tuple(shape)} actual={tuple(value.shape)}"
            )
        if value.dtype != dtype:
            raise ValueError(f"{label} 精度不匹配: expected={dtype} actual={value.dtype}")
        if value.device != parameter.device:
            raise ValueError(
                f"{label} 设备不匹配: expected={parameter.device} "
                f"(type={parameter.device.type}, index={parameter.device.index}) "
                f"actual={value.device} (type={value.device.type}, index={value.device.index})"
            )
        if not integer and not torch.isfinite(value).all():
            raise ValueError(f"{label} 包含非有限值")

    def _condition(self, values, fields, module, batch, label):
        values = values or {}
        if set(values) != {n for n, _ in fields}:
            raise ValueError(f"{label} 条件字段缺失或多余")
        for name, width in fields:
            self._tensor(values[name], (batch, width), label + name)
        return module(torch.cat([values[n] for n, _ in fields], dim=-1)) if fields else None

    def _geometry(self, position, indices, batches, batch_size, condition):
        if not isinstance(position, torch.Tensor) or position.ndim != 2 or not len(position):
            raise ValueError("几何必须为非空 (N,3)")
        self._tensor(position, (len(position), 3), "几何")
        if not isinstance(indices, torch.Tensor) or indices.ndim != 1 or not len(indices):
            raise ValueError("超节点必须为非空索引")
        self._tensor(indices, (len(indices),), "超节点", integer=True)
        self._tensor(batches, (len(position),), "几何批次", integer=True)
        if (
            indices.min() < 0
            or indices.max() >= len(position)
            or len(indices.unique()) != len(indices)
        ):
            raise ValueError("超节点越界或重复")
        if (
            not torch.equal(batches.unique(), torch.arange(batch_size, device=batches.device))
            or (batches[1:] < batches[:-1]).any()
        ):
            raise ValueError("几何批次必须连续且按样本排列")
        counts = torch.bincount(batches[indices], minlength=batch_size)
        if not (counts == counts[0]).all() or counts[0] == 0:
            raise ValueError("同批超节点数量必须相同且非零")
        # 聚合输出与采样 supernode 的顺序一致，RoPE 保持同一行身份。
        frequencies = self.rope(position[indices].reshape(batch_size, -1, 3))
        geometry = self.encoder(input_pos=position, supernode_idx=indices, batch_idx=batches)
        for block in self.geometry_blocks:
            if condition is None:
                result, _ = block(
                    {"geometry": geometry},
                    {"geometry": frequencies},
                    {"geometry": geometry.shape[1]},
                    kind="s",
                )
                geometry = result["geometry"]
            else:
                geometry = block(
                    geometry,
                    frequencies,
                    block.project_kv(geometry, frequencies, condition),
                    condition,
                )
        return geometry, frequencies

    def forward(
        self,
        geometry_position=None,
        geometry_supernode_idx=None,
        geometry_batch_idx=None,
        domain_anchor_positions=None,
        domain_query_positions=None,
        domain_anchor_features=None,
        domain_query_features=None,
        conditioning_inputs=None,
        geometry_conditioning_inputs=None,
        kv_cache=None,
        *,
        return_cache=False,
    ):
        """完整前向或缓存查询，返回标准预测和可选进程内缓存。"""
        if kv_cache is not None and not isinstance(kv_cache, ModelCache):
            raise ValueError("不支持的缓存类型")
        caching = return_cache or kv_cache is not None
        if caching and (self.training or torch.is_grad_enabled()):
            raise ValueError("缓存仅支持无梯度 eval")
        if caching and torch.is_autocast_enabled(next(self.parameters()).device.type):
            raise ValueError("缓存推理不支持自动混合精度")
        if kv_cache is not None:
            kv_cache.validate(self)
        cached = kv_cache is not None and kv_cache.physics is not None
        anchors, queries = domain_anchor_positions or {}, domain_query_positions or {}
        af, qf = domain_anchor_features or {}, domain_query_features or {}
        domains = set(self.layout.domains)
        if (
            set(anchors) - domains
            or set(queries) - domains
            or set(af) - set(anchors)
            or set(qf) - set(queries)
        ):
            raise ValueError("未知域或特征没有对应坐标")
        if cached:
            if (
                anchors
                or af
                or conditioning_inputs is not None
                or geometry_conditioning_inputs is not None
                or any(
                    v is not None
                    for v in (geometry_position, geometry_supernode_idx, geometry_batch_idx)
                )
            ):
                raise ValueError("完整缓存调用只接受新的查询输入")
            if not queries:
                raise ValueError("缓存查询不能为空")
            batch = kv_cache.batch_size
            condition, geo_condition = kv_cache.condition, kv_cache.geometry_condition
        else:
            if set(anchors) != domains:
                raise ValueError("完整前向必须提供所有域 anchors")
            first = next(iter(anchors.values()))
            if first.ndim != 3 or first.shape[0] == 0:
                raise ValueError("域坐标必须为 (B,N,3)")
            batch = first.shape[0]
            condition = self._condition(
                conditioning_inputs, self.layout.conditions, self.conditioner, batch, "全局"
            )
            if self.layout.inherit_geometry:
                if geometry_conditioning_inputs is not None:
                    raise ValueError("继承几何条件时不能显式提供第二份条件")
                geo_condition = condition
            else:
                geo_condition = self._condition(
                    geometry_conditioning_inputs,
                    self.layout.geometry_conditions,
                    self.geometry_conditioner,
                    batch,
                    "几何",
                )
        x, frequencies, anchor_sizes = {}, {}, {}
        for domain in self.layout.domains:
            parts, positions = [], []
            for values, feats in ((anchors, af), (queries, qf)):
                if domain not in values:
                    continue
                pos = values[domain]
                if not isinstance(pos, torch.Tensor) or pos.ndim != 3 or pos.shape[1] == 0:
                    raise ValueError("域坐标必须为非空 (B,N,3)")
                self._tensor(pos, (batch, pos.shape[1], 3), domain)
                embedded = self.biases[domain](self.pos_embed(pos))
                width = sum(w for _, w in self.layout.features[domain])
                if width:
                    if domain not in feats and self.require_features:
                        raise ValueError("声明的域特征缺失")
                    if domain not in feats:
                        parts.append(embedded)
                        positions.append(pos)
                        continue
                    self._tensor(feats[domain], (batch, pos.shape[1], width), domain + " 特征")
                    embedded = embedded + self.feature_projections[domain](feats[domain])
                elif domain in feats:
                    raise ValueError("未声明的域特征")
                parts.append(embedded)
                positions.append(pos)
            if parts:
                x[domain] = torch.cat(parts, dim=1)
                frequencies[domain] = self.rope(torch.cat(positions, dim=1))
                anchor_sizes[domain] = anchors[domain].shape[1] if domain in anchors else 0
        if kv_cache is None:
            geometry, geometry_rope = self._geometry(
                geometry_position, geometry_supernode_idx, geometry_batch_idx, batch, geo_condition
            )
        else:
            if not cached:
                if any(
                    v is not None
                    for v in (geometry_position, geometry_supernode_idx, geometry_batch_idx)
                ):
                    raise ValueError("几何缓存调用不能替换几何")
                old = kv_cache.geometry_condition
                if (old is None) != (geo_condition is None) or (
                    old is not None and not torch.equal(old, geo_condition)
                ):
                    raise ValueError("几何缓存条件冲突")
            if batch != kv_cache.batch_size:
                raise ValueError("缓存批次布局冲突")
            geometry, geometry_rope = kv_cache.geometry, kv_cache.geometry_rope
        physics_cache, decoder_cache = [], {}
        for i, (kind, block) in enumerate(zip(self.block_types, self.blocks, strict=True)):
            if condition is None:
                x, layer = block(
                    x,
                    frequencies,
                    anchor_sizes,
                    kind=kind,
                    geometry=geometry,
                    geometry_frequencies=geometry_rope,
                    cache=kv_cache.physics[i] if cached else None,
                )
                physics_cache.append(layer)
                continue
            if cached:
                layer = kv_cache.physics[i]
            elif kind == "p":
                layer = {"geometry": block.project_kv(geometry, geometry_rope, condition)}
            else:
                layer = {
                    d: block.project_kv(
                        v[:, : anchor_sizes[d]], frequencies[d][:, : anchor_sizes[d]], condition
                    )
                    for d, v in x.items()
                }
            expected = {"geometry"} if kind == "p" else domains
            if set(layer) != expected:
                raise ValueError("物理块缓存不完整")
            next_x = {}
            for domain, value in x.items():
                sources = (
                    ["geometry"]
                    if kind == "p"
                    else (
                        [domain] if kind == "s" else [d for d in self.layout.domains if d != domain]
                    )
                )
                kv = tuple(torch.cat([layer[d][j] for d in sources], dim=2) for j in (0, 1))
                next_x[domain] = block(value, frequencies[domain], kv, condition)
            x = next_x
            physics_cache.append(layer)
        predictions = {}
        for domain, value in x.items():
            layers = []
            for i, block in enumerate(self.decoders[domain]):
                if condition is None:
                    result, layer = block(
                        {domain: value},
                        {domain: frequencies[domain]},
                        {domain: anchor_sizes[domain]},
                        kind="s",
                        cache={domain: kv_cache.decoders[domain][i]} if cached else None,
                    )
                    value = result[domain]
                    layers.append(layer[domain])
                    continue
                kv = (
                    kv_cache.decoders[domain][i]
                    if cached
                    else block.project_kv(
                        value[:, : anchor_sizes[domain]],
                        frequencies[domain][:, : anchor_sizes[domain]],
                        condition,
                    )
                )
                value = block(value, frequencies[domain], kv, condition)
                layers.append(kv)
            decoder_cache[domain] = layers
            value = self.readouts[domain](value, condition)
            count = anchor_sizes[domain]
            if count:
                predictions.update(self.layout.split(domain, value[:, :count]))
            if value.shape[1] > count:
                predictions.update(self.layout.split(domain, value[:, count:], query=True))
        cache = None
        if return_cache:
            cache = (
                kv_cache
                if cached
                else ModelCache(
                    model_signature(self),
                    geometry,
                    geometry_rope,
                    condition,
                    geo_condition,
                    batch,
                    physics_cache,
                    decoder_cache,
                )
            )
        return predictions, cache
