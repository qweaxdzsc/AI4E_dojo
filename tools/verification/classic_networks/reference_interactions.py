"""独立注意力/图公式参考；不导入或调用 Dojo 被验数值实现。

依据标准缩放点积注意力、PyTorch 后规范化定义和显式残差 MPNN 变体。
本文件是独立公式实现，不是 DeepMind/Sonnet 移植：后者先聚合边增量，
本批为兼容既有 Dojo 块，聚合加残差后的新边状态。不能宣称二者等价。
"""

from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F

SOURCE_IDENTITY = {
    "attention_paper": "https://arxiv.org/abs/1706.03762",
    "mpnn_paper": "https://arxiv.org/abs/1704.01212",
    "torch_version": "2.14.0",
    "torch_commit": "08187d9e0fba026dc8217405802ab5381dc88d90",
    "torch_license": "BSD-3-Clause (dependency; independent formula implementation)",
    "torch_activation_sha256": "9b1ef5c6daeaf392b9267f82a7212da22233c23b8b344a7494d58426a2bf3679",
    "torch_transformer_sha256": "651d83bc800de2ce02d196253da2c4cddb791e8cd18c71769de1c49864329d2c",
    "graph_comparison_commit": "f5de0ede8430809180254ee957abf36ed62579ef",
    "graph_comparison_license": "Apache-2.0 (inspected, not copied)",
    "graph_variant": "aggregate_residual_updated_edges_then_residual_node_update",
    "paper_reproduction": False,
    "position_dtype": "FP32 computation preserved; double model buffer cast only at evaluation, not FP64 position precision",
    "attention_oracles": {
        "explicit": "Independent separate Q/K/V linear, QK-softmax-V formula for local semantic checks",
        "torch_native": "Independent assembly using PyTorch packed MHA functional/SDPA; current dense eval fastpath matched for long FP32 trajectories",
    },
    "native_oracle_scope": "Plain dense batch-first tensors, eager execution, dropout=0 or eval; no core forward calls; not a separately maintained upstream full-model implementation",
}


def dense(module: nn.Module, value: torch.Tensor) -> torch.Tensor:
    """仅读取参数并执行独立基础公式，不调用被验模块 forward。"""
    if isinstance(module, nn.Linear):
        return F.linear(value, module.weight, module.bias)
    if isinstance(module, nn.LayerNorm):
        return F.layer_norm(value, module.normalized_shape, module.weight, module.bias, module.eps)
    if isinstance(module, nn.ReLU):
        # clamp_min 的零点子梯度是 1；ReLU 定义为 0，必须保留该边界。
        return F.relu(value)
    if isinstance(module, nn.GELU):
        return F.gelu(value, approximate=module.approximate)
    if isinstance(module, (nn.Identity, nn.Dropout)):
        if isinstance(module, nn.Dropout) and module.p and module.training:
            raise ValueError("独立固定数值参考要求 dropout=0 或 eval 模式")
        return value
    if isinstance(module, nn.Sequential):
        for child in module:
            value = dense(child, value)
        return value
    if hasattr(module, "projection") and hasattr(module.projection, "layers"):
        return dense(module.projection.layers, value)
    raise TypeError(f"没有独立参考公式: {type(module).__name__}")


def attention(module, query, context, *, key_padding_mask=None, attn_mask=None):
    """用显式 QK^T、softmax、V 和输出投影核对多头注意力。"""
    mha = module.attention
    dim, heads = mha.embed_dim, mha.num_heads
    if mha.in_proj_weight is not None:
        qw, kw, vw = mha.in_proj_weight.chunk(3)
    else:
        qw, kw, vw = mha.q_proj_weight, mha.k_proj_weight, mha.v_proj_weight
    qb, kb, vb = mha.in_proj_bias.chunk(3)
    batch, queries = query.shape[:2]
    keys = context.shape[1]
    q = F.linear(query, qw, qb).reshape(batch, queries, heads, dim // heads).transpose(1, 2)
    k = F.linear(context, kw, kb).reshape(batch, keys, heads, dim // heads).transpose(1, 2)
    v = F.linear(context, vw, vb).reshape(batch, keys, heads, dim // heads).transpose(1, 2)
    logits = q @ k.transpose(-2, -1) / math.sqrt(dim // heads)
    if key_padding_mask is not None:
        logits = logits.masked_fill(key_padding_mask[:, None, None], -torch.inf)
    if attn_mask is not None:
        mask = attn_mask if attn_mask.ndim == 2 else attn_mask.reshape(batch, heads, queries, keys)
        logits = logits.masked_fill(mask, -torch.inf) if mask.dtype == torch.bool else logits + mask
    probabilities = logits.softmax(dim=-1)
    result = (probabilities @ v).transpose(1, 2).reshape(batch, queries, dim)
    return F.linear(result, mha.out_proj.weight, mha.out_proj.bias)


def native_attention(module, query, context, *, key_padding_mask=None, attn_mask=None):
    """原生 PyTorch 注意力参考；只映射参数，不调用任何 Dojo forward。

    与显式公式 oracle 分开：用于 FP32 长优化轨迹，保留 packed QKV、SDPA
    和当前 PyTorch 普通稠密张量的 eval fastpath 算术。仅支持本批 batch-first
    稠密注意力；不扩展为 NestedTensor、编译/追踪或张量子类的通用实现。
    """
    mha = module.attention
    if query.ndim != 3 or context.ndim != 3 or query.is_nested or context.is_nested:
        raise ValueError("原生参考只支持普通 [B,N,D] 稠密张量")
    if type(query) is not torch.Tensor or type(context) is not torch.Tensor:
        raise TypeError("原生参考不支持张量子类")
    if not mha.batch_first:
        raise ValueError("原生参考要求 batch_first")
    # 同生产外层：浮点 attention mask 与 bool padding 先统一成加性掩码。
    padding = key_padding_mask
    if attn_mask is not None and attn_mask.is_floating_point() and padding is not None:
        padding = torch.zeros_like(padding, dtype=attn_mask.dtype).masked_fill(padding, -torch.inf)
    floating_mask = any(
        mask is not None and mask.is_floating_point() for mask in (padding, attn_mask)
    )

    def additive(mask):
        if mask is None or mask.dtype != torch.bool:
            return mask
        return torch.zeros_like(mask, dtype=query.dtype).masked_fill(mask, -torch.inf)

    padding, mask = additive(padding), additive(attn_mask)
    params = (
        query,
        context,
        mha.in_proj_weight,
        mha.in_proj_bias,
        mha.out_proj.weight,
        mha.out_proj.bias,
    )
    devices = {"cpu", "cuda", torch.utils.backend_registration._privateuse1_backend_name}
    fast = (
        torch.backends.mha.get_fastpath_enabled()
        and not floating_mask
        and query is context
        and not mha.training
        and mha.num_heads % 2 == 0
        and mha.in_proj_weight is not None
        and mha.in_proj_bias is not None
        and query.dtype == mha.in_proj_weight.dtype
        and query.dtype == mha.in_proj_bias.dtype
        and mha.bias_k is None
        and mha.bias_v is None
        and not mha.add_zero_attn
        and mha._qkv_same_embed_dim
        and not torch.is_autocast_enabled()
        and all(value is None or value.device.type in devices for value in params)
        and not (
            torch.is_grad_enabled()
            and any(value is not None and value.requires_grad for value in params)
        )
    )
    if fast:
        # 对齐 MHA.merge_masks；这里独立拼装，不调用被验对象的方法。
        merged, mask_type = padding, (1 if padding is not None else None)
        if mask is not None:
            batch, length = query.shape[:2]
            merged = (
                mask.reshape(batch, -1, length, length)
                if mask.ndim == 3
                else mask.reshape(1, 1, length, length).expand(batch, mha.num_heads, -1, -1)
            )
            if padding is not None:
                merged = merged + padding.reshape(batch, 1, 1, length).expand(
                    -1, mha.num_heads, -1, -1
                )
            mask_type = 2
        return torch._native_multi_head_attention(
            query,
            context,
            context,
            mha.embed_dim,
            mha.num_heads,
            mha.in_proj_weight,
            mha.in_proj_bias,
            mha.out_proj.weight,
            mha.out_proj.bias,
            merged,
            False,
            True,
            mask_type,
        )[0]
    # Q/K/V 身份决定 packed 投影分支；不能分别 transpose 后丢失对象身份。
    q = query.transpose(0, 1)
    k = q if query is context else context.transpose(0, 1)
    output, _ = F.multi_head_attention_forward(
        q,
        k,
        k,
        mha.embed_dim,
        mha.num_heads,
        mha.in_proj_weight,
        mha.in_proj_bias,
        mha.bias_k,
        mha.bias_v,
        mha.add_zero_attn,
        mha.dropout,
        mha.out_proj.weight,
        mha.out_proj.bias,
        training=mha.training,
        key_padding_mask=padding,
        need_weights=False,
        attn_mask=mask,
        use_separate_proj_weight=not mha._qkv_same_embed_dim,
        q_proj_weight=mha.q_proj_weight,
        k_proj_weight=mha.k_proj_weight,
        v_proj_weight=mha.v_proj_weight,
        average_attn_weights=True,
        is_causal=False,
    )
    return output.transpose(0, 1)


def encoder_block(
    module, value, *, key_padding_mask=None, attn_mask=None, attention_backend="explicit"
):
    """独立后规范化两残差公式，固定数值参考不使用随机丢弃。"""
    if attention_backend not in {"explicit", "torch_native"}:
        raise ValueError("attention_backend 必须为 explicit 或 torch_native")
    if any(part.training and part.p for part in (module.dropout1, module.dropout2)):
        raise ValueError("独立固定数值参考要求 dropout=0 或 eval 模式")
    implementation = attention if attention_backend == "explicit" else native_attention
    first = value + implementation(
        module.attention, value, value, key_padding_mask=key_padding_mask, attn_mask=attn_mask
    )
    first = dense(module.norm1, first)
    return dense(module.norm2, first + dense(module.feed_forward, first))


def aggregate_enumerated(messages, target, node_count, reduction="sum"):
    """仅供小图核对的逐节点枚举参考，禁止用于正式大图计算。"""
    rows = []
    for node in range(node_count):
        selected = messages[target == node]
        row = selected.sum(0)
        if reduction == "mean":
            row = row / max(len(selected), 1)
        rows.append(row)
    return torch.stack(rows) if rows else messages.new_empty(0, messages.shape[1])


def adjacency_slots(target, node_count):
    """CPU稳定按目标节点分桶，返回[N,maxdegree]边槽及入度。

    仅不可微整数拓扑转CPU；每个桶保持原边顺序，等价于稳定target排序。
    构建复杂度O(E+N*maxdegree)，不调用生产index_add或Dojo图能力。
    """
    cpu_target = target.detach().to(device="cpu", dtype=torch.long)
    buckets = [[] for _ in range(node_count)]
    for edge, node in enumerate(cpu_target.tolist()):
        if node < 0 or node >= node_count:
            raise ValueError("参考目标节点索引越界")
        buckets[node].append(edge)
    counts = torch.tensor([len(bucket) for bucket in buckets], dtype=torch.long)
    degree = int(counts.max()) if len(counts) else 0
    slots = torch.full((node_count, degree), len(target), dtype=torch.long)
    for node, bucket in enumerate(buckets):
        if bucket:
            slots[node, : len(bucket)] = torch.tensor(bucket, dtype=torch.long)
    return slots.to(target.device), counts.to(target.device)


def aggregate(messages, target, node_count, reduction="sum", *, layout=None):
    """在原消息设备逐槽gather并顺序求和，梯度不转CPU。"""
    if reduction not in {"sum", "mean"}:
        raise ValueError("参考聚合只支持sum或mean")
    slots, counts = adjacency_slots(target, node_count) if layout is None else layout
    padded = torch.cat((messages, messages.new_zeros(1, messages.shape[1])), dim=0)
    result = messages.new_zeros(node_count, messages.shape[1])
    for slot in range(slots.shape[1]):
        result = result + padded[slots[:, slot]]
    if reduction == "mean":
        result = result / counts.to(messages.dtype).clamp_min(1).unsqueeze(-1)
    return result


def graph_interaction(module, nodes, edges, edge_index, *, aggregation_layout=None):
    """独立核对先边残差、再聚合、再节点残差的明确变体。"""
    source, target = edge_index
    joined = torch.cat((nodes[source], nodes[target], edges), dim=-1)
    updated_edges = edges + dense(module.edge_update.network, joined)
    messages = aggregate(
        updated_edges, target, len(nodes), module.aggregation, layout=aggregation_layout
    )
    updated_nodes = nodes + dense(module.node_update.network, torch.cat((nodes, messages), dim=-1))
    return updated_nodes, updated_edges


def graph_network(module, node_features, edge_features, edge_index):
    """使用公开子结构参数独立执行完整节点预测。"""
    nodes = dense(module.encoder.nodes, node_features)
    edges = dense(module.encoder.edges, edge_features)
    layout = adjacency_slots(edge_index[1], len(nodes))
    for block in module.processor.blocks:
        nodes, edges = graph_interaction(block, nodes, edges, edge_index, aggregation_layout=layout)
    return dense(module.readout.network, nodes)


def patch_transformer(module, value, valid_mask=None, *, attention_backend="explicit"):
    """独立分块/位置/编码/重建完整公式；不调用生产模型子结构 forward。"""
    import itertools

    patch = module.embedding.patch_shape
    spatial = value.shape[1:-1]
    padded = tuple(((n + p - 1) // p) * p for n, p in zip(spatial, patch, strict=True))
    grid = tuple(n // p for n, p in zip(padded, patch, strict=True))
    if valid_mask is None:
        valid_mask = torch.ones(value.shape[:-1], dtype=torch.bool, device=value.device)
    pad = [0, 0]
    for n, size in reversed(list(zip(spatial, padded, strict=True))):
        pad.extend((0, size - n))
    expanded = F.pad(value.masked_fill(~valid_mask.unsqueeze(-1), 0), pad)
    validity = F.pad(valid_mask.unsqueeze(-1), pad, value=False)
    indices = list(itertools.product(*(range(n) for n in grid)))
    patches, masks, centers = [], [], []
    for index in indices:
        slices = tuple(slice(i * p, (i + 1) * p) for i, p in zip(index, patch, strict=True))
        patches.append(expanded[(slice(None), *slices, slice(None))].reshape(len(value), -1))
        masks.append(~validity[(slice(None), *slices, slice(None))].reshape(len(value), -1).any(-1))
        centers.append(tuple((i + 0.5) / n for i, n in zip(index, grid, strict=True)))
    tokens = F.linear(
        torch.stack(patches, 1),
        module.embedding.projection.weight,
        module.embedding.projection.bias,
    )
    mask = torch.stack(masks, 1)
    coords = torch.tensor(centers, device=value.device, dtype=value.dtype).float()
    position = module.position_encoding
    angles = coords[..., None] * position.omega.float()
    if attention_backend == "torch_native":
        # 长轨迹使用同一底层设备浮点运算顺序；explicit 保留独立枚举坐标公式。
        axes = [(torch.arange(n, device=value.device, dtype=value.dtype) + 0.5) / n for n in grid]
        coords = torch.stack(torch.meshgrid(*axes, indexing="ij"), -1).reshape(-1, len(grid))
        angles = coords.float().unsqueeze(-1) @ position.omega.to(dtype=torch.float32).unsqueeze(0)
    encoded_position = torch.cat((angles.sin(), angles.cos()), -1).reshape(len(indices), -1)
    if position.padding:
        encoded_position = F.pad(encoded_position, (0, position.padding))
    tokens = tokens + encoded_position.to(tokens.dtype)
    for block in module.encoder.blocks:
        tokens = encoder_block(
            block, tokens, key_padding_mask=mask, attention_backend=attention_backend
        )
    values = F.linear(
        tokens, module.reconstruction.projection.weight, module.reconstruction.projection.bias
    )
    output = value.new_zeros(len(value), *padded, module.reconstruction.out_channels)
    for slot, index in enumerate(indices):
        slices = tuple(slice(i * p, (i + 1) * p) for i, p in zip(index, patch, strict=True))
        output[(slice(None), *slices, slice(None))] = values[:, slot].reshape(
            len(value), *patch, -1
        )
    output = output[(slice(None), *(slice(n) for n in spatial), slice(None))]
    return output.masked_fill(~valid_mask.unsqueeze(-1), 0)


def native_patch_transformer(module, value, valid_mask=None):
    """完整原生算子 oracle 入口；位置、块布局与读出仍独立装配。"""
    return patch_transformer(module, value, valid_mask, attention_backend="torch_native")


def reference_model(network: nn.Module, *, attention_backend="explicit") -> nn.Module:
    """复制参数并绑定独立完整公式；保留生产参数键和调用签名供配对训练。

    仅支持本批标准默认组成；状态保存使用 state_dict，不序列化绑定函数。
    explicit 保留独立 QK-softmax-V 公式；torch_native 使用原生 MHA 算术用于
    长 FP32 轨迹，仍独立组合布局、位置、残差和输出。二者均不调用 core forward，
    也不声称完整上游工程复现。该适配器自身不执行训练或优化器更新。
    """
    import copy
    import types

    if attention_backend not in {"explicit", "torch_native"}:
        raise ValueError("attention_backend 必须为 explicit 或 torch_native")
    result = copy.deepcopy(network)
    if hasattr(network, "embedding") and hasattr(network, "reconstruction"):
        implementation = (
            native_patch_transformer if attention_backend == "torch_native" else patch_transformer
        )
        result.forward = types.MethodType(implementation, result)
    elif hasattr(network, "processor") and hasattr(network, "readout"):
        result.forward = types.MethodType(graph_network, result)
    else:
        raise TypeError("reference_model 仅支持 PatchTransformer 或 GraphNetwork")
    return result
