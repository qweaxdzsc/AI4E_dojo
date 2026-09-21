"""五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import torch
from torch.nn import functional as F

def compute_enhanced_gradient_loss(pred, target, eps=0.0001, max_rel=80.0):
    """五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：compute_enhanced_gradient_loss；保留来源算法、参数与权重布局。"""

    def _relative_grad_loss(pred_grad, target_grad, eps=0.0001, max_rel=None):
        diff2 = (pred_grad - target_grad) ** 2
        den = target_grad ** 2 + eps
        rel = diff2 / den
        if max_rel is not None:
            rel = torch.clamp(rel, 0.0, max_rel)
        rel = torch.log1p(rel)
        w = torch.abs(target_grad)
        w_mean = w.mean(dim=(1, 2, 3, 4), keepdim=True) + eps
        w_norm = w / w_mean
        loss = (w_norm * rel).mean()
        return loss
    pred_grad_x = pred[:, :, 1:, :, :] - pred[:, :, :-1, :, :]
    target_grad_x = target[:, :, 1:, :, :] - target[:, :, :-1, :, :]
    rel_x_loss = _relative_grad_loss(pred_grad_x, target_grad_x, eps=eps, max_rel=max_rel)
    pred_grad_y = pred[:, 1:, :, :, :] - pred[:, :-1, :, :, :]
    target_grad_y = target[:, 1:, :, :, :] - target[:, :-1, :, :, :]
    rel_y_loss = _relative_grad_loss(pred_grad_y, target_grad_y, eps=eps, max_rel=max_rel)
    pred_grad_z = pred[:, :, :, 1:, :] - pred[:, :, :, :-1, :]
    target_grad_z = target[:, :, :, 1:, :] - target[:, :, :, :-1, :]
    rel_z_loss = _relative_grad_loss(pred_grad_z, target_grad_z, eps=eps, max_rel=max_rel)
    pred_grad_t = pred[:, :, :, :, 1:] - pred[:, :, :, :, :-1]
    target_grad_t = target[:, :, :, :, 1:] - target[:, :, :, :, :-1]
    rel_t_loss = _relative_grad_loss(pred_grad_t, target_grad_t, eps=eps, max_rel=max_rel)
    first_order_loss = rel_x_loss + rel_y_loss + 0.3 * rel_z_loss + rel_t_loss
    total_loss = first_order_loss
    total_loss = torch.nan_to_num(total_loss, nan=0.0, posinf=10000.0, neginf=0.0)
    return total_loss

def create_smooth_weight_map(pred, target, dist_inj, dist_prod, sigma=3.0, task='pressure', alpha_base=1.0, epsilon=0.0001):
    """五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：create_smooth_weight_map；保留来源算法、参数与权重布局。"""
    if dist_prod is None or task != 'pressure':
        dist = dist_inj
    else:
        dist = torch.minimum(dist_inj, dist_prod)
    dist = torch.sqrt(dist ** 2 + 1e-06)
    dist_weight = torch.exp(-dist ** 2 / (2 * sigma ** 2))
    dist_weight = 0.2 + 0.8 * dist_weight
    rel_err = F.smooth_l1_loss(pred, target, reduction='none')
    mean_rel_err = rel_err.mean(dim=(1, 2, 3, 4), keepdim=True) + epsilon
    rel_norm = rel_err / mean_rel_err
    rel_norm = torch.log1p(rel_norm)
    alpha = alpha_base
    weight = dist_weight * (1.0 + alpha * rel_norm)
    if task == 'temperature':
        inj_mask = (dist_inj < 0.5).float()
        weight = weight * (1.0 + 1.5 * inj_mask)
    if task == 'pressure' and dist_prod is not None:
        inj_mask = (dist_inj < 0.5).float()
        prod_mask = (dist_prod < 0.5).float()
        well_mask = (inj_mask + prod_mask).clamp(0, 1)
        weight = weight * (1.0 + 1.5 * well_mask)
    w_mean = weight.mean(dim=(1, 2, 3, 4), keepdim=True).detach()
    weight = weight / (w_mean + 1e-06)
    weight = torch.nan_to_num(weight, nan=0.0, posinf=1.0, neginf=0.0)
    return weight

def weighted_mse(pred, target, weight):
    """五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：weighted_mse；保留来源算法、参数与权重布局。"""
    return torch.mean(weight * (pred - target) ** 2)
