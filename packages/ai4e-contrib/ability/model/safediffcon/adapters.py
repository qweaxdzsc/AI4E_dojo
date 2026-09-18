"""SafeDiffCon 两种原生网络的显式构造，不依赖原仓库路径。"""


def build_model(*, case: str, dim: int = 64, ddim_steps: int = 50, device: str = "cpu"):
    """构造原版噪声预测模型；dim64 是三小时集成变体而非论文宽度。"""
    if dim < 8 or dim % 8 or not 1 <= ddim_steps <= 1000:
        raise ValueError("网络宽度须为8的正倍数，采样步数须在1–1000")
    if case == "burgers":
        from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

        from .burgers_unet import Unet2D

        unet = Unet2D(dim=dim, dim_mults=(1, 2, 4, 8), channels=3, resnet_block_groups=1)
        model = GaussianDiffusion(
            unet,
            seq_length=(16, 128),
            use_conv2d=True,
            temporal=True,
            train_on_padded_locations=False,
            is_condition_u0=True,
            is_condition_uT=True,
            condition_idx=10,
            is_condition_u0_zero_pred_noise=True,
            is_condition_uT_zero_pred_noise=True,
            sampling_timesteps=ddim_steps,
            ddim_sampling_eta=1.0,
        )
    elif case == "tokamak":
        from ai4e_contrib.ability.inference.safediffcon.tokamak import GaussianDiffusion

        from .tokamak_unet import Unet1D

        unet = Unet1D(dim=dim, dim_mults=(1, 2, 4, 8), channels=12, resnet_block_groups=1)
        model = GaussianDiffusion(
            unet,
            seq_length=128,
            nt=122,
            use_conv2d=False,
            temporal=False,
            guidance_u0=True,
            is_condition_u0=True,
            is_condition_uT=True,
            is_condition_u0_zero_pred_noise=True,
            is_condition_uT_zero_pred_noise=True,
            sampling_timesteps=ddim_steps,
            ddim_sampling_eta=1.0,
        )
    else:
        raise ValueError(f"未知控制案例: {case}")
    return model.to(device)
