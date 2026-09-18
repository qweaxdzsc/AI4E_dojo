"""WDNO 作者数值定义；来源和抽取记录见 model/wdno/source.json。"""
import math
import torch
from torch import nn
from pytorch_wavelets import DWTInverse, DWT1DForward
from .layout import tensor_to_coef
from .multiscale import upsample_coef

def get_wavelet_super_preprocess(
    rescaler=70, 
    is_super_model=False,
    N_downsample=0,
    mode='zero',
    wave_type='bior2.4',
    is_condition_u0=True,
    is_condition_uT=True,
):
    if rescaler is None:
        raise NotImplementedError('Should specify rescaler. If no rescaler is not used, specify 1.')

    def preprocess(db):
        data = db['coef']
        nonlocal N_downsample
        N_downsample = 0 if not is_super_model else N_downsample
        w_u = data[N_downsample][:, 0][:40000]
        w_f = data[N_downsample][:, 1][:40000]
        if is_super_model:
            w_u_sub = data[N_downsample+1][:, 0][:40000]
            w_f_sub = data[N_downsample+1][:, 1][:40000]
        ori_shape = list(db['ori_shape'])
        ori_shape[0] = math.ceil(ori_shape[0]/2**N_downsample)
        ori_shape[1] = math.ceil(ori_shape[1]/2**N_downsample)
            
        N = w_u.size(0)
        nt = w_f.size(-2)
        nx = w_f.size(-1)
        shape = w_f.shape[2:]

        # pad f for stack 
        pad_t, pad_x = int(64 / 2**N_downsample), int(64 / 2**N_downsample)
        
        w_uf = torch.cat((w_u, w_f), dim=1) # assuming dim 0 is N_samples e.g. [40000, 8, 41, 60]
        w_uf = nn.functional.pad(w_uf, (0, pad_x - nx, 0, pad_t - nt), 'constant', 0)
        data = w_uf # [40000, 8, 64, 64]

        if is_super_model: # low-resolution
            w_uf_sub = torch.cat((upsample_coef(w_u_sub, shape), upsample_coef(w_f_sub, shape)), dim=1) # e.g. [40000, 8, 21*2, 60]
            w_uf_sub = nn.functional.pad(w_uf_sub, (0, pad_x - w_uf_sub.shape[-1], 0, pad_t - w_uf_sub.shape[-2]), 'constant', 0)
            data = w_uf
            data[:, :, nt, :] = data[:, :, nt-1, :] # repeat the last timestep due to the odd number of timesteps
            # data = w_uf - w_uf_sub
            data = torch.cat((data, w_uf_sub), dim=1)
        
        if is_condition_u0 or is_condition_uT: # 1d wavelet transformation pf u0, uT
            ifm = DWTInverse(mode=mode, wave=wave_type).to(data.device)
            Yl, Yh = tensor_to_coef(w_uf[:, :8], shape)
            u_f = ifm((Yl, Yh))[:, :, :ori_shape[-2], :ori_shape[-1]]
            u, f = u_f[:, 0], u_f[:, 1, :ori_shape[-2]-1]

            # concatenate W_u0, W_uT
            xfm1d = DWT1DForward(J=1, mode=mode, wave=wave_type).to(data.device)
            Yl0, Yh0 = xfm1d(u[:, [0, -1], :ori_shape[-1]])
            W_condition = torch.zeros_like(data[:, [0]]) # (N, 1, (W_u0)+(W_uT), pad_x)
            n_repeat = int(pad_t / 4)
            if is_condition_u0:
                W_condition[:, :, :n_repeat, :nx] = Yl0[:, [0]].unsqueeze(1).expand(N, 1, n_repeat, nx)
                W_condition[:, :, n_repeat:n_repeat*2, :nx] = Yh0[0][:, [0]].unsqueeze(1).expand(N, 1, n_repeat, nx)
            if is_condition_uT:
                W_condition[:, :, n_repeat*2:n_repeat*3, :nx] = Yl0[:, [1]].unsqueeze(1).expand(N, 1, n_repeat, nx)
                W_condition[:, :, n_repeat*3:n_repeat*4, :nx] = Yh0[0][:, [1]].unsqueeze(1).expand(N, 1, n_repeat, nx)
            data = torch.cat((data, W_condition), dim=1) 

        data = data / rescaler
        return data, list(shape), list(ori_shape)

    return preprocess
