"""有效域场监督、空间梯度和来源交错散度的可微损失原语。"""

from torch.nn import functional as F

from .continuity import staggered_divergence, weighted_mean_square


def interior_mask(mask, layers=3):
    """腐蚀二维有效域并排除外边界；不对物理值人工清零。"""
    shape = mask.shape
    flat = mask.reshape(-1, 1, *shape[-2:]).float()
    padded = F.pad(flat, (layers,) * 4, value=0)
    eroded = -F.max_pool2d(-padded, 2 * layers + 1, stride=1)
    return eroded.reshape(shape).bool()


def field_losses(prediction, target, mask, *, mean, scale, gradient_scale, velocity=True):
    """标准化数据/梯度误差与物理速度散度；无效域不能当零残差。"""
    error = prediction - target
    data = weighted_mean_square(error, mask[..., None])
    dx = error[..., 1:, :, :] - error[..., :-1, :, :]
    dy = error[..., :, 1:, :] - error[..., :, :-1, :]
    gradient = (
        weighted_mean_square(dx, (mask[..., 1:, :] & mask[..., :-1, :])[..., None])
        + weighted_mean_square(dy, (mask[..., :, 1:] & mask[..., :, :-1])[..., None])
    ) / 2
    divergence = prediction.new_zeros(())
    if velocity:
        physical = prediction * scale + mean
        div = staggered_divergence(physical[..., :2])
        valid = mask[..., :-1, :-1] & mask[..., 1:, :-1] & mask[..., :-1, 1:]
        divergence = weighted_mean_square(div / gradient_scale, valid)
    return {"data": data, "gradient": gradient, "divergence": divergence}
