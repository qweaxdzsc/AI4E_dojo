"""WDNO 基础预测的局部网络/扩散连接。"""

from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
from ai4e_contrib.ability.model.wdno.unet import Unet2D
from ai4e_contrib.ability.transform.wdno.burgers import scale


def network(options: dict):
    """构造可替换去噪网络，参数名称沿用作者实现。"""
    return Unet2D(
        dim=options["dim"],
        dim_mults=tuple(options["dim_mults"]),
        channels=9,
        out_dim=9,
        resnet_block_groups=options["groups"],
    )


def diffusion(options: dict, construct=network):
    """小波/通道/条件语义在局部连接声明，不让训练循环解释。"""
    return GaussianDiffusion(
        construct(options),
        seq_length=(64, 64),
        is_wavelet=True,
        padded_shape=[41, 60],
        ori_shape=[81, 120],
        pad_mode="periodization",
        wave_type="bior2.4",
        is_super_model=False,
        upsample_t=0,
        upsample_x=0,
        timesteps=1000,
        sampling_timesteps=options["ddim_steps"],
        ddim_sampling_eta=1,
        beta_schedule="cosine",
        loss_layer_weight=scale(),
        is_condition_pad=True,
        is_condition_u0=True,
        is_condition_uT=False,
        is_condition_f=True,
    )


def objective(model, values):
    """默认目标调用原条件扩散算术，允许 recipe 直接替换。"""
    return model(values)
