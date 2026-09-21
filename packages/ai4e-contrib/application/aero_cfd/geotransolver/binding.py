"""外流域和 GeoTransolver 的语义连接；数值计算及执行由 core 提供。"""

import torch

from ai4e_contrib.ability.model.geotransolver import GeoTransolver
from ai4e_contrib.application.geotransolver import build_optimizer
from ai4e_core.abilities.constraint.supervised import supervised
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler
from ai4e_core.applications.aero_cfd.infer.point_prediction import predict_point_sample
from ai4e_core.applications.aero_cfd.trainprep.point_inputs import (
    collate_point_samples,
    decode_point_outputs,
)
from ai4e_core.applications.aero_cfd.trainprep.point_inputs import (
    prepare_point_sample as prepare_sample,
)

SOURCE = "Dojo/geotransolver-aero-v1"
collate = collate_point_samples
prepare_inputs = prepare_sample


def training_parameters(config: dict) -> dict:
    """从明确的数据规格推导网络输入输出维度。"""
    specs = config["model"]["data_specs"]
    domains = specs["domains"]
    return {
        **config["model"]["parameters"],
        "domains": domains,
        "functional_dim": tuple(
            specs["position_dim"] + sum(v["feature_dim"].values()) for v in domains.values()
        ),
        "out_dim": tuple(sum(v["output_dims"].values()) for v in domains.values()),
        "geometry_dim": specs["position_dim"],
        "global_dim": sum(specs.get("conditioning_dims", {}).values()) or None,
    }


def construct(*, domains, **parameters):
    """构造共享块、多投影网络，声明仅用于解码与结构身份。"""
    model = GeoTransolver(**parameters)
    model.aero_domains = domains
    model.aero_parameters = parameters
    return model


def describe(model) -> dict:
    """返回与路径无关的结构及字段顺序身份。"""
    return {"model_version": 1, "parameters": model.aero_parameters, "domains": model.aero_domains}


construct.describe = describe


def predict(model, inputs):
    """将模型输出映射为显式监督字段。"""
    return decode_point_outputs(model(**inputs), model.aero_domains)


def loss(model, batch, config):
    """选用 core 监督损失，贡献层不重写损失算术。"""
    return supervised(
        predict(model, batch["inputs"]), batch["targets"], config["model"]["supervision"]
    )


def predict_stream(model, points, **context):
    """绑定网络指定流入口。"""
    return model.forward_stream(points, **context)


def predict_sample(model, sample, config, normalization, *, preparation_id):
    """连接 core 全点预测，学习上下文不持久化。"""
    return predict_point_sample(model, sample, config, normalization, predict_stream=predict_stream)


def optimizer_factory(model, settings):
    """选择现有二维 Muon、其他 AdamW 的互斥参数策略。"""
    return build_optimizer(
        model, lr=settings["learning_rate"], weight_decay=settings["weight_decay"]
    )


def scheduler_factory(optimizer, settings, *, updates_per_epoch):
    """按真实完整轮次推进阶梯日程，不随短训预算缩放。"""
    return EpochBoundaryScheduler(
        torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=settings["step_size"], gamma=settings["gamma"]
        ),
        updates_per_epoch,
    )
