"""WDNO 作者数值定义；来源和抽取记录见 model/wdno/source.json。"""
import torch
from torch import nn

def tensor_to_coef(coef_tensor, shape):
    '''
    input: [N, more than 2*(1+3), padded, padded]
    '''
    u_Yl = coef_tensor[:, None, 0, :shape[-2], :shape[-1]]
    u_Yh = coef_tensor[:, None, 1:4, :shape[-2], :shape[-1]]
    f_Yl = coef_tensor[:, None, 4, :shape[-2], :shape[-1]]
    f_Yh = coef_tensor[:, None, 5:8, :shape[-2], :shape[-1]]
    Yl = torch.cat((u_Yl, f_Yl), dim=1)
    Yh = [torch.cat((u_Yh, f_Yh), dim=1)]
    return Yl, Yh

def coef_to_tensor(Yl, Yh, pad = False):
    '''
    return: repeat Yh[i] 2**i times 
    if pad: [Yl.shape[0], Yl.shape[1], 1+3*J, 64, 64]
    else: [Yl.shape[0], Yl.shape[1], 1+3*J, Yh[0].shape[-2]+2**(J-1)-1 (because Yh[0].shape[-2]%2=1), Yh[0].shape[-1] (because Yh[0].shape[-1]%2=0)]
    '''
    J = len(Yh)
    coef_tensor = torch.zeros(Yl.shape[0], Yl.shape[1], 1+3*J, Yh[0].shape[-2]+2**(J-1)-1, Yh[0].shape[-1], device=Yl.device)
    Yl_repeat = Yl.unsqueeze(-2).unsqueeze(-1).repeat(1, 1, 1, 2**(J-1), 1, 2**(J-1))\
                .reshape(Yl.shape[0], Yl.shape[1], 2**(J-1)*Yl.shape[2], 2**(J-1)*Yl.shape[3]).clone()
    coef_tensor[:, :, 0] = Yl_repeat
    for i in range(J):
        Yh_repeat = Yh[i].unsqueeze(-2).unsqueeze(-1).repeat(1, 1, 1, 1, 2**i, 1, 2**i)\
            .reshape(Yh[i].shape[0], Yh[i].shape[1], Yh[i].shape[2], 2**i*Yh[i].shape[3], 2**i*Yh[i].shape[4]).clone()
        coef_tensor[:, :, 1+3*i:1+3*(i+1)] = torch.cat((Yh_repeat, Yh_repeat[:, :, :, [-1]].repeat(1, 1, 1, 2**(J-1)-2**i, 1)), dim=3)
    if pad:
        upsample_t = int(coef_tensor.shape[-2] / 40)
        upsample_x = int(coef_tensor.shape[-1] / 60)
        coef_tensor = nn.functional.pad(coef_tensor, (0, 64*upsample_x - coef_tensor.shape[-1], 0, 64*upsample_t - coef_tensor.shape[-2]), 'constant', 0)
    return coef_tensor
