"""PCNO 统计量、种子、原始250轮调度与分阶段损失权重。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import math
import random
import numpy as np
import torch

def denormalize(tensor, mean, std):
    """使用作者冻结统计量还原。"""
    return tensor * std + mean

class TrainConfig:
    """PCNO 统计量、种子、原始250轮调度与分阶段损失权重：TrainConfig；保留来源算法、参数与权重布局。"""

    @staticmethod
    def set_seed(seed=7):
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    @staticmethod
    def stats_to_device(stats, device):
        out = {}
        for k, v in stats.items():
            if isinstance(v, (list, tuple)):
                out[k] = torch.tensor(v, device=device, dtype=torch.float32)
            elif isinstance(v, (int, float)):
                out[k] = torch.tensor(v, device=device, dtype=torch.float32)
            else:
                try:
                    out[k] = torch.as_tensor(v, device=device, dtype=torch.float32)
                except Exception:
                    out[k] = v
        return out

class ModelConfig:
    """PCNO 统计量、种子、原始250轮调度与分阶段损失权重：ModelConfig；保留来源算法、参数与权重布局。"""

    @staticmethod
    def lr_lambda(base_lr, warmup_start_lr, warmup_end_lr, lr_mid, lr_min, warmup_steps, plateau_steps, cosine1_steps, cosine2_steps):

        def lr_lambda(current_step):
            if current_step < warmup_steps:
                lr_now = warmup_start_lr + (warmup_end_lr - warmup_start_lr) * (current_step / max(1, warmup_steps))
                return lr_now / base_lr
            elif current_step < warmup_steps + plateau_steps:
                return warmup_end_lr / base_lr
            elif current_step < warmup_steps + plateau_steps + cosine1_steps:
                progress = (current_step - warmup_steps - plateau_steps) / cosine1_steps
                cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
                lr_now = lr_mid + (warmup_end_lr - lr_mid) * cosine_decay
                return lr_now / base_lr
            else:
                progress = (current_step - warmup_steps - plateau_steps - cosine1_steps) / max(1, cosine2_steps)
                progress = min(max(progress, 0.0), 1.0)
                cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
                lr_now = lr_min + (lr_mid - lr_min) * cosine_decay
                return lr_now / base_lr
        return lr_lambda

    @staticmethod
    def scale(base, secondary):
        ratio = base.item() / (secondary.item() + 1e-08)
        return max(0.1, min(5.0, ratio))

    @staticmethod
    def loss_weights(ep, mse, w, g):
        if ep < 5:
            return dict(w=(1.0, 0.0, 0.0), w_phys=0.0, w_task=0.0)
        if ep < 20:
            w_w = 0.9 * ModelConfig.scale(mse, w)
            return dict(w=(1.0, 0.0, w_w), w_phys=0.0, w_task=0.0)
        if ep < 35:
            w_g = 0.3 * ModelConfig.scale(mse, g)
            w_w = 0.9 * ModelConfig.scale(mse, w)
            return dict(w=(0.9, w_g, w_w), w_phys=0.0, w_task=0.0)
        if ep < 50:
            w_g = 0.5 * ModelConfig.scale(mse, g)
            w_w = 1.0 * ModelConfig.scale(mse, w)
            return dict(w=(0.9, w_g, w_w), w_phys=0.0, w_task=0.0)
        if ep < 65:
            w_g = 0.7 * ModelConfig.scale(mse, g)
            w_w = 1.0 * ModelConfig.scale(mse, w)
            return dict(w=(0.8, w_g, w_w), w_phys=0.1, w_task=0.0)
        if ep < 80:
            w_g = 0.9 * ModelConfig.scale(mse, g)
            w_w = 1.1 * ModelConfig.scale(mse, w)
            return dict(w=(0.8, w_g, w_w), w_phys=0.2, w_task=0.0)
        if ep < 95:
            w_g = 1.1 * ModelConfig.scale(mse, g)
            w_w = 1.1 * ModelConfig.scale(mse, w)
            return dict(w=(0.7, w_g, w_w), w_phys=0.4, w_task=0.1)
        if ep < 110:
            w_g = 1.3 * ModelConfig.scale(mse, g)
            w_w = 1.3 * ModelConfig.scale(mse, w)
            return dict(w=(0.7, w_g, w_w), w_phys=0.6, w_task=0.2)
        w_g = 1.5 * ModelConfig.scale(mse, g)
        w_w = 1.5 * ModelConfig.scale(mse, w)
        return dict(w=(0.6, w_g, w_w), w_phys=0.8, w_task=0.3)

    @staticmethod
    def loss_weights_finetune():
        w_mse = 0.8
        w_g = 0.4
        w_w = 0.6
        return dict(w=(w_mse, w_g, w_w), w_phys=0.5, w_task=0.5)

    @staticmethod
    def decode_inputs(input_i, g_i, s):
        Pini = denormalize(input_i[..., 0], s['Pini_mean'], s['Pini_std'])
        Tini = denormalize(input_i[..., 1], s['Tini_mean'], s['Tini_std'])
        q_inj = torch.where(input_i[..., 3] != 0, input_i[..., 3] * s['qinj_std'] + s['qinj_mean'], torch.zeros_like(input_i[..., 1]))
        T_inj = torch.where(input_i[..., 4] != 0, input_i[..., 4] * s['Tinj_std'] + s['Tinj_mean'], torch.zeros_like(input_i[..., 2]))
        pwf = torch.where(input_i[..., 5] != 0, input_i[..., 5] * s['ppro_std'] + s['ppro_mean'], torch.zeros_like(input_i[..., 3]))
        k = denormalize(input_i[..., 6], s['perm_mean'], s['perm_std'])
        phi = denormalize(input_i[..., 7], s['poro_mean'], s['poro_std'])
        d = denormalize(g_i[..., 0], s['global_mean'][0], s['global_std'][0])
        Cp_r = denormalize(g_i[..., 1], s['global_mean'][1], s['global_std'][1])
        lam_r = denormalize(g_i[..., 2], s['global_mean'][2], s['global_std'][2])
        dz = denormalize(g_i[..., 3], s['global_mean'][3], s['global_std'][3])
        return (Pini, Tini, q_inj, T_inj, pwf, k, phi, d, Cp_r, lam_r, dz)
