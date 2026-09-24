"""Transolver 点场绑定与跨步数据组织；不识别具体数据集名称。"""

import random

import torch

from ai4e_core.abilities.sampling.stride import indices


def domain_binding(config: dict) -> tuple[str, dict]:
    """一次 Transolver 训练只消费一个显式域。"""
    domains = config["trainprep"]["domains"]
    if len(domains) != 1:
        raise ValueError("Transolver 单实例需要一个域；不同域请使用独立 example")
    return next(iter(domains.items()))


def arrays(sample: dict, config: dict, normalization) -> tuple[torch.Tensor, torch.Tensor]:
    """按具名字段顺序拼接特征，工况在模型输入处广播。"""
    domain, binding = domain_binding(config)
    fields = sample["fields"]
    chunks = []
    for name in [binding["position"], *binding.get("features", {}).values()]:
        value = normalization.transforms[name].apply(fields[name])
        chunks.append(value.reshape(len(value), -1))
    count = len(chunks[0])
    for name, declaration in config["trainprep"].get("conditioning", {}).items():
        key = declaration["field"]
        value = normalization.transforms[key].apply(sample["conditions"][key])
        chunks.append(value.expand(count, -1))
    features = torch.cat(chunks, dim=-1)
    targets = torch.cat(
        [
            normalization.transforms[name].apply(fields[name]).reshape(count, -1)
            for name in binding["targets"].values()
        ],
        dim=-1,
    )
    if (
        features.shape[1] != config["model"]["parameters"]["space_dim"]
        or targets.shape[1] != config["model"]["parameters"]["out_dim"]
    ):
        raise ValueError(f"{sample['identity']}/{domain}: 模型输入输出宽度与字段绑定不一致")
    return features, targets


def prepare_sample(
    sample: dict, config: dict, normalization, *, evaluation: bool = False, epoch: int = 0
) -> dict:
    """训练随机块与起点，准备检查固定块；保留计算项原点身份。"""
    x, y = arrays(sample, config, normalization)
    parts = int(config["sampling"].get("chunk_count", 20))
    stride = int(config["sampling"].get("stride", 4))
    part = 0 if evaluation else random.randrange(parts)
    offset = 0 if evaluation else random.randrange(stride)
    selected = torch.from_numpy(indices(len(x), parts, part))[offset::stride]
    if not len(selected):
        raise ValueError(f"{sample['identity']}: 分块抽稀后为空")
    domain, _ = domain_binding(config)
    return {
        "inputs": {"features": x[selected][None]},
        "targets": {"fields": y[selected][None]},
        "metadata": [{**sample["identity"], "chunk": part, "offset": offset}],
        "point_ids": sample["domains"][domain]["ids"][selected],
    }


def prepare_inputs(
    fields,
    sampling,
    *,
    sample,
    bindings,
    normalization=None,
    evaluation=False,
    **_kwargs,
):
    """把通用准备链的归一化平面字段组织为单域 Transolver 样本。

    通用链已经变换点场；这里只对 ``scope=condition`` 的样本条件应用
    冻结变换。返回未拼批张量，批次维由组件 ``collate`` 统一添加。
    """
    domains = bindings.get("domains") or {}
    if len(domains) != 1:
        raise ValueError("Transolver 单实例需要一个域；不同域请使用独立 example")
    domain, binding = next(iter(domains.items()))

    def point_field(name):
        if name not in fields:
            raise ValueError(f"绑定字段不存在: {name}")
        value = fields[name]
        if not isinstance(value, torch.Tensor) or value.ndim not in (1, 2):
            raise ValueError(f"绑定字段形状不一致: {name}")
        return value.reshape(len(value), -1)

    chunks = [point_field(binding["position"])]
    chunks.extend(point_field(name) for name in binding.get("features", {}).values())
    count = len(chunks[0])
    for name, declaration in (bindings.get("conditioning") or {}).items():
        source = declaration.get("field")
        if source is None or source not in fields:
            raise ValueError(f"条件缺样本字段: {sample}/{source or name}")
        value = torch.as_tensor(fields[source], dtype=torch.float32).reshape(1, -1)
        if normalization is None or source not in normalization.transforms:
            raise ValueError(f"条件必须声明冻结变换或恒等变换: {source}")
        chunks.append(normalization.transforms[source].apply(value).expand(count, -1))
    if any(len(value) != count for value in chunks):
        raise ValueError(f"{sample}/{domain}: 输入字段实体数量不一致")
    targets = [point_field(name) for name in binding.get("targets", {}).values()]
    if not targets or any(len(value) != count for value in targets):
        raise ValueError(f"{sample}/{domain}: 监督字段实体数量不一致")

    features = torch.cat(chunks, dim=-1)
    target = torch.cat(targets, dim=-1)
    parts = int(sampling.get("chunk_count", 20))
    stride = int(sampling.get("stride", 4))
    part = 0 if evaluation else random.randrange(parts)
    offset = 0 if evaluation else random.randrange(stride)
    selected = torch.from_numpy(indices(count, parts, part))[offset::stride]
    if not len(selected):
        raise ValueError(f"{sample}: 分块抽稀后为空")
    return {
        "inputs": {"features": features[selected]},
        "targets": {"fields": target[selected]},
        "metadata": {"sample": sample, "chunk": part, "offset": offset},
        "point_ids": selected,
    }


def loss(model, batch: dict, config: dict) -> dict:
    """等权标准化逐元素均方误差。"""
    from .model import predict

    prediction = predict(model, batch["inputs"])["fields"]
    target = batch["targets"]["fields"]
    if prediction.shape != target.shape:
        raise ValueError("监督形状不一致")
    difference = prediction - target
    return {
        "loss": difference.square().mean(),
        "squared_error": float(difference.detach().square().sum().cpu()),
        "element_count": difference.numel(),
    }


@torch.no_grad()
def predict_sample(
    model, sample: dict, config: dict, normalization, *, preparation_id: str
) -> dict:
    """完整域逐层状态汇总后解码；原点顺序回贴物理具名输出。"""
    from .inference import SurfaceInference

    _domain, binding = domain_binding(config)
    x, _ = arrays(sample, config, normalization)
    count = len(x)
    parts = int(config["sampling"].get("chunk_count", 20))

    def chunks():
        for part in range(parts):
            ids = torch.from_numpy(indices(count, parts, part))
            yield ids, {"features": x[ids][None]}

    result = torch.empty(count, config["model"]["parameters"]["out_dim"])
    for ids, prediction in SurfaceInference(model).predict(
        chunks, query_chunk_size=(config.get("infer") or {}).get("query_chunk_size")
    ):
        result[ids] = prediction["fields"][0].cpu()
    output = {}
    offset = 0
    for source in binding["targets"].values():
        width = sample["fields"][source].reshape(count, -1).shape[1]
        output[source] = normalization.inverse(source, result[:, offset : offset + width])
        offset += width
    return output
