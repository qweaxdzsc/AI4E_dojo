"""PCNO 分支监督目标；保留真实伴随场、裁剪前物理场及原损失日程。"""
import torch
from torch.nn import functional as F
from ai4e_core.abilities.constraint.spatiotemporal_field import compute_enhanced_gradient_loss, create_smooth_weight_map, weighted_mse
from ai4e_core.abilities.constraint.geothermal import physical_loss, compute_loss
from .protocol import ModelConfig


def loss_components(model, sample, *, branch, epoch, stats):
    """返回总损失和分项；井筒标量求解的梯度边界与作者一致。"""
    x, global_param = sample['spatial_params'], sample['global_params']
    pres, temp = sample['pres'], sample['temp']
    Twh_all, Hwh_all, Pinj_all = sample['Temp_wh'], sample['Heat_wh'], sample['P_inj']
    i, batch_size, train_mode, ep, stats_dev = 0, 1, branch, epoch, stats
    t_mean,t_std,p_mean,p_std = stats['temp_mean'],stats['temp_std'],stats['pres_mean'],stats['pres_std']
    input_i = x[i:i + batch_size]
    g_i = global_param[i:i + batch_size]
    Twh_t = Twh_all[i:i + batch_size]
    Hwh_t = Hwh_all[i:i + batch_size]
    Pinj_t = Pinj_all[i:i + batch_size]
    dis_inj = input_i[..., 8]
    dis_prod = input_i[..., 9]
    if train_mode == 'temp':
        true_value = temp[i:i + batch_size]
        clamp_min, clamp_max = (-2.0, 4.0)
        task_type = 'temperature'
    if train_mode == 'pres':
        true_value = pres[i:i + batch_size]
        clamp_min, clamp_max = (-3.0, 9.0)
        task_type = 'pressure'
    pred_value = model(input_i, g_i)
    pred_value = torch.nan_to_num(pred_value, nan=0.0, posinf=10000.0, neginf=-10000.0)
    if train_mode == 'temp':
        p_raw = pres[i:i + batch_size] * p_std + p_mean
        pred_T_raw = pred_value * t_std + t_mean
        T_true_raw = true_value * t_std + t_mean
    if train_mode == 'pres':
        pred_p_raw = pred_value * p_std + p_mean
        p_true_raw = true_value * p_std + p_mean
        T_raw = temp[i:i + batch_size] * t_std + t_mean
    pred_value = torch.clamp(pred_value, clamp_min, clamp_max)
    mse_loss = F.mse_loss(pred_value, true_value)
    grad_loss = compute_enhanced_gradient_loss(pred_value, true_value)
    w_map = create_smooth_weight_map(pred_value, true_value, dis_inj, dis_prod, task=task_type)
    weighted_loss = weighted_mse(pred_value, true_value, w_map)
    Pini, Tini, q_inj, T_inj, pwf, k, phi, d, Cp_r, lam_r, dz = ModelConfig.decode_inputs(input_i, g_i, stats_dev)
    loss_func = physical_loss(T_i=Tini, p_i=Pini, Cp_r=Cp_r, lam_r=lam_r, dz=dz, q_inj=q_inj, T_inj=T_inj, pwf=pwf, k=k, phi=phi, depth=d)
    if train_mode == 'temp':
        mse_mass, mse_energy, re_Twh, re_Ewh, re_Pinj = compute_loss(p_raw, pred_T_raw, loss_func, Twh_t, Hwh_t, Pinj_t)
        loss_phys = mse_energy
    if train_mode == 'pres':
        mse_mass, mse_energy, re_Twh, re_Ewh, re_Pinj = compute_loss(pred_p_raw, T_raw, loss_func, Twh_t, Hwh_t, Pinj_t)
        loss_phys = mse_mass
    loss_task = re_Twh + re_Ewh + re_Pinj
    ws = ModelConfig.loss_weights(ep, mse_loss, weighted_loss, grad_loss)
    w_mse, w_g, w_w = ws['w']
    w_phys = ws['w_phys']
    w_task = ws['w_task']
    loss = w_mse * mse_loss + w_w * weighted_loss + w_g * grad_loss + w_phys * loss_phys + w_task * loss_task
    return {"loss":loss,"mse":mse_loss,"gradient":grad_loss,"weighted":weighted_loss,"physics":loss_phys,"task":loss_task}


def build_objective(*, branch, stats):
    """构造可替换的标量目标；样本项携带真实轮次。"""
    def objective(model, item):
        sample, epoch = item
        return loss_components(model, sample, branch=branch, epoch=epoch, stats=stats)['loss']
    return objective
