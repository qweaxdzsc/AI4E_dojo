"""算子与真实网格的局部布局：固定传感器、逐样本查询和有序历史通道。"""

import math

from torch import nn

from ai4e_contrib.application.classic_networks.binding import batch as field_batch

from .configuration import component


def batch(arrays, ids, *, device, case, sample_points=None, point_sequence=False):
    """场取批复用既有身份连接，时间保持历史轴，不按空间点拆散FNO。"""
    return field_batch(
        arrays, ids, device=device, case=case, sample_points=sample_points, point_sequence=False
    )


def build_network(model):
    """配置只在局部解释，core模型不读取场来源或配置树。"""
    params = dict(model["parameters"])
    ci, co = model["in_channels"], model["out_channels"]
    if model["family"] == "fno":
        from ai4e_core.abilities.modeling.models.fno import FNO

        return FNO(ci * model.get("history", 1), co, **params)
    from ai4e_core.abilities.modeling.models.deeponet import DeepONet

    stride = params.pop("sensor_stride")
    if type(stride) is not int or stride < 1:
        raise ValueError("传感器步长须正整数")
    sensors = math.prod(len(range(0, n, stride)) for n in model["grid_shape"])
    return DeepONet(
        sensors * ci,
        model["spatial_dims"],
        out_channels=co,
        multi_output=None if co == 1 else "split_branch",
        **params,
    )


class OperatorField(nn.Module):
    """末轴场与中立网络之间显式转换；参数正常注册、传感器不跨样本变序。"""

    def __init__(self, network, model):
        super().__init__()
        self.network = network
        self.family = model["family"]
        self.grid_shape = tuple(model["grid_shape"])
        self.history = model.get("history", 1)
        self.sensor_stride = model["parameters"].get("sensor_stride", 1)

    def forward(self, input, valid=None, coordinates=None):
        """逐样本完整规则场预测，输出保留原空间轴和分量顺序。"""
        if self.history > 1:
            if input.ndim != 5 or input.shape[1] != self.history:
                raise ValueError("历史窗口与声明不一致")
            input = input.permute(0, 2, 3, 1, 4).flatten(-2)
        if tuple(input.shape[1:-1]) != self.grid_shape:
            raise ValueError("网格与模型固定布局不一致")
        if self.family == "fno":
            return self.network(input.movedim(-1, 1)).movedim(1, -1)
        if coordinates is None or coordinates.shape[:-1] != input.shape[:-1]:
            raise ValueError("查询坐标未与预测网格对齐")
        selection = (slice(None),) + (slice(None, None, self.sensor_stride),) * len(self.grid_shape)
        branch = input[selection].reshape(len(input), -1)
        query = coordinates.reshape(len(input), -1, len(self.grid_shape))
        output = self.network(branch, query, query_layout="per_sample")
        return output.reshape(len(input), *self.grid_shape, output.shape[-1])


def construct(cfg):
    """用户可替换整个网络构造器，局部数据布局保持显式。"""
    return OperatorField(component(cfg["components"]["model"])(cfg["model"]), cfg["model"])
