"""WDNO 作者数值定义；来源和抽取记录见 model/wdno/source.json。"""
import math
import torch
import torch.nn.functional as F
from random import random
from einops import reduce
from ai4e_contrib.ability.model.wdno.schedules import default, extract

class DenoisingObjective:
    def p_losses(self, x_start, t, noise = None):
        b, c, nt, nx = x_start.shape
        if self.is_super_model:
            if self.is_wavelet:
                N_downsample = int(math.log2(64 / nx))
            else:
                N_downsample = int(math.log2(128 / nx))
            coef_shape = [self.padded_shape[N_downsample][0] + 1, self.padded_shape[N_downsample][1]]# repeat the last timestep due to the odd number of timesteps
        else:
            coef_shape = self.padded_shape
        noise = default(noise, lambda: torch.randn_like(x_start))

        # noise sample
        x = self.q_sample(x_start = x_start, t = t, noise = noise)

        # if doing self-conditioning, 50% of the time, predict x_start from current set of times
        # and condition with unet with that
        # this technique will slow down training by 25%, but seems to lower FID significantly

        x_self_cond = None
        if self.self_condition and random() < 0.5:
            with torch.no_grad():
                x_self_cond = self.model_predictions(x, t).pred_x_start
                x_self_cond.detach_()

        # predict and take gradient step

        # 1. BEFORE MODEL_PREDICTION: SET INPUT
        if self.is_condition_pad:
            self.set_condition(x, 0, coef_shape, "pad")

        if self.is_condition_u0: # NOTE: u0 here means physical time t=0, while the u0 in guidance means the 0th step in diffusion
            if self.is_wavelet :
                self.set_condition(x, x_start[:, -1, :int(nt/2), :], coef_shape, 'u0')
            else:
                self.set_condition(x, x_start[:, 0, 0, :], coef_shape, 'u0')
                if len(x.shape) == 4:
                    pass
                else:
                    raise ValueError('Bad sample shape')
                
        if self.is_condition_uT: # NOTE: uT here means physical time t=T
            if self.is_wavelet :
                self.set_condition(x, x_start[:, -1, int(nt/2):, :], coef_shape, 'uT')
            else:
                if self.is_super_model:
                    self.set_condition(x, x_start[:, 0, coef_shape[0]-2:coef_shape[0], :], coef_shape, 'uT')
                else:
                    self.set_condition(x, x_start[:, 0, coef_shape[0]-1, :], coef_shape, 'uT')

        if self.is_condition_f:
            if self.is_wavelet:
                self.set_condition(x, x_start[:, 4:8], coef_shape, 'f')
            else:
                self.set_condition(x, x_start[:, 1], coef_shape, 'f')
        
        if self.is_super_model:
            # assert self.is_wavelet
            if self.is_wavelet:
                self.set_condition(x, x_start[:, 8:16], coef_shape, 'low')
            else:
                self.set_condition(x, x_start[:, 2:4], coef_shape, 'low')

        # 2. MODEL PREDICTION
        model_out = self.model(x, t, x_self_cond)

        # 3. AFTER MODEL_PREDICTION: SET OUTPUT AND TARGET
        if self.objective == 'pred_noise':
            target = noise
        elif self.objective == 'pred_x0':
            target = x_start
        elif self.objective == 'pred_v':
            v = self.predict_v(x_start, t, noise)
            target = v
        else:
            raise ValueError(f'unknown objective {self.objective}')
            
        if self.is_condition_pad:
            self.set_condition(noise, 0, coef_shape, "pad")

        if self.is_condition_u0:
            # not computing loss for the diffused state!
            if self.is_wavelet:
                self.set_condition(noise, torch.zeros_like(x[:, -1, :int(nt/2), :]), coef_shape, 'u0')
            else:
                self.set_condition(noise, torch.zeros_like(x[:, 0, 0, :]), x.shape, 'u0')
        
        if self.is_condition_uT:
            # not computing loss for the diffused state!
            if self.is_wavelet:
                self.set_condition(noise, torch.zeros_like(x[:, -1, int(nt/2):, :]), coef_shape, 'uT')
            else:
                if self.is_super_model:
                    self.set_condition(noise, torch.zeros_like(x[:, 0, :2, :]), coef_shape, 'uT')
                else:
                    self.set_condition(noise, torch.zeros_like(x[:, 0, 0, :]), coef_shape, 'uT')

        if self.is_condition_f:
            # not computing loss for the diffused state!
            if self.is_wavelet:
                self.set_condition(noise, torch.zeros_like(x[:, 4:8]), coef_shape, 'f')
            else:
                self.set_condition(noise, torch.zeros_like(x[:, 1]), coef_shape, 'f')

        if self.is_super_model:
            if self.is_wavelet:
                self.set_condition(noise, torch.zeros_like(x_start[:, 8:16]), coef_shape, 'low')
            else:
                self.set_condition(noise, torch.zeros_like(x_start[:, 2:4]), coef_shape, 'low')

        # 4. COMPUTE LOSS
        loss = F.mse_loss(model_out, target, reduction = 'none')
        loss = loss * self.loss_layer_weight.to(loss.device)
        loss = reduce(loss, 'b ... -> b', 'mean')

        loss = loss * extract(self.loss_weight, t, loss.shape)
        return loss.mean()

    def forward(self, img, *args, **kwargs):
        b, c, nt, nx, device, traj_size = *img.shape, img.device, self.traj_size
        # assert (nt, nx) == traj_size, f'traj size must be (nt, nx) of ({nt, nx})'
        # diffusion timestep
        t = torch.randint(0, self.num_timesteps, (b,), device=device).long()

        img = self.normalize(img)
        return self.p_losses(img, t, *args, **kwargs)
