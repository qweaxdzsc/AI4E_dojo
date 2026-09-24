"""经典场预测的局部布局、模型构造、取批及监督连接。"""

import numpy as np
import torch
from torch import nn

from .configuration import component


def build_network(model):
    """创建中立网络，参数通过局部配置显式传递，不改变核心协议。"""
    from ai4e_core.abilities.modeling.models import cnn, resnet, unet
    from ai4e_core.abilities.modeling.models.gnn import GraphNetwork
    from ai4e_core.abilities.modeling.models.mlp import MLP
    from ai4e_core.abilities.modeling.models.rnn import RNN
    from ai4e_core.abilities.modeling.models.transformer import PatchTransformer

    family, dims = model["family"], model["spatial_dims"]
    ci, co, params = model["in_channels"], model["out_channels"], dict(model["parameters"])
    if family == "mlp":
        return MLP(ci, co, **params)
    if family == "rnn":
        return RNN(ci, co, **params)
    if family in {"cnn", "resnet", "unet"}:
        module, name = {"cnn": (cnn, "CNN"), "resnet": (resnet, "ResNet"), "unet": (unet, "UNet")}[
            family
        ]
        return getattr(module, name + str(dims) + "d")(ci, co, **params)
    if family == "transformer":
        return PatchTransformer(ci, co, **params)
    if family == "gnn":
        return GraphNetwork(ci, dims + 1, co, **params)
    raise ValueError("自定义模型需要components.model构造器")


class FieldModel(nn.Module):
    """局部适配规则场、图与真实序列；所有学习参数注册到network。"""

    def __init__(self, network, family, spatial_dims):
        super().__init__()
        self.network, self.family, self.spatial_dims = network, family, spatial_dims

    def forward(self, input, valid=None, coordinates=None):
        """返回末轴场或点批序列末时刻，mask语义由此局部连接转换。"""
        value = input
        if self.family in {"cnn", "unet", "resnet"}:
            return self.network(value.movedim(-1, 1)).movedim(1, -1)
        if self.family == "transformer":
            return self.network(value, valid_mask=valid)
        if self.family == "rnn":
            output, _ = self.network(value)
            return output[:, -1]
        if self.family == "gnn":
            from ai4e_core.abilities.geometry.grid_graph import grid_edges
            from ai4e_core.abilities.geometry.mesh_graph import edge_features, induced_subgraph

            predictions = []
            edges = grid_edges(tuple(value.shape[1:-1]), device=value.device)
            for x, mask, coords in zip(value, valid, coordinates, strict=True):
                x, mask, coords = (
                    x.reshape(-1, x.shape[-1]),
                    mask.reshape(-1),
                    coords.reshape(-1, self.spatial_dims),
                )
                ids = torch.nonzero(mask, as_tuple=False).flatten()
                local_edges, ids = induced_subgraph(edges, ids, node_count=len(mask))
                features = edge_features(coords[ids], local_edges)
                y = self.network(x[ids], features, local_edges)
                prediction = y.new_zeros((len(mask), y.shape[-1])).index_copy(0, ids, y)
                predictions.append(prediction.reshape(*value.shape[1:-1], y.shape[-1]))
            return torch.stack(predictions)
        return self.network(value)


def construct(cfg):
    """按普通构造器接入完整网络；布局适配不进入网络能力。"""
    network = component(cfg["components"]["model"])(cfg["model"])
    return FieldModel(network, cfg["model"]["family"], cfg["model"]["spatial_dims"])


def batch(arrays, ids, *, device, case, sample_points=None, point_sequence=True):
    """同索引取特征/目标/mask；循环输入按真实时间轴组织为Q×T×C。"""
    indices = np.asarray(ids)
    item = {
        name: torch.from_numpy(np.array(arrays[name][indices], copy=True)).to(device)
        for name in ("input", "target", "valid", "physical_input")
    }
    for name in ("input", "target", "physical_input"):
        item[name] = item[name].float()
    item["valid"] = item["valid"].bool()
    if case == "double_cylinder" and point_sequence:
        x = item["input"].permute(0, 2, 3, 1, 4).reshape(-1, 3, 4)
        y = item["target"].reshape(-1, 4)
        chosen = torch.arange(len(y), device=device)
        if sample_points is not None:
            chosen = torch.randperm(len(y), device=device)[:sample_points]
        return {
            "input": x[chosen],
            "target": y[chosen],
            "valid": torch.ones(len(chosen), dtype=torch.bool, device=device),
        }
    if case != "double_cylinder":
        item["coordinates"] = item["physical_input"][..., : 2 if case == "darcy" else 3]
    return item


def objective(model, item):
    """有效域归一化MSE；失效占位永不参与损失或梯度。"""
    prediction = model(item["input"], item["valid"], item.get("coordinates"))
    if prediction.shape != item["target"].shape or not item["valid"].any():
        raise ValueError("预测/目标形状或监督有效域不符")
    return (prediction[item["valid"]] - item["target"][item["valid"]]).square().mean()
