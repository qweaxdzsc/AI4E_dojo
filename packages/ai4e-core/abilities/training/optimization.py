"""显式设备、可换优化器与单次参数更新。"""

import math
import warnings
from contextlib import nullcontext

import torch


class Lion(torch.optim.Optimizer):
    """符号动量优化器；本仓实现，不引入第三方优化器包。"""

    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0.0):
        if not math.isfinite(lr) or lr <= 0:
            raise ValueError("学习率必须有限且为正")
        if not 0 <= betas[0] < 1 or not 0 <= betas[1] < 1:
            raise ValueError("beta 必须位于 [0,1)")
        if not math.isfinite(weight_decay) or weight_decay < 0:
            raise ValueError("权重衰减必须有限且非负")
        super().__init__(params, {"lr": lr, "betas": betas, "weight_decay": weight_decay})

    @torch.no_grad()
    def step(self, closure=None):
        """按 Lion 规则更新参数。"""
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()
        for group in self.param_groups:
            lr, (beta1, beta2), decay = group["lr"], group["betas"], group["weight_decay"]
            parameters, gradients, averages = [], [], []
            for parameter in group["params"]:
                if parameter.grad is None:
                    continue
                if parameter.grad.is_sparse:
                    raise RuntimeError("Lion 不支持稀疏梯度")
                state = self.state[parameter]
                if "exp_avg" not in state:
                    state["exp_avg"] = torch.zeros_like(parameter)
                parameters.append(parameter)
                gradients.append(parameter.grad)
                averages.append(state["exp_avg"])
            if not parameters:
                continue
            # 与默认 Lion 批量路径保持相同算子顺序，避免长期 sign 更新放大舍入差异。
            torch._foreach_mul_(parameters, 1 - lr * decay)
            updates = torch._foreach_mul(averages, beta1)
            torch._foreach_add_(updates, gradients, alpha=1 - beta1)
            updates = tuple(value.sign_() for value in updates)
            torch._foreach_add_(parameters, updates, alpha=-lr)
            torch._foreach_mul_(averages, beta2)
            torch._foreach_add_(averages, gradients, alpha=1 - beta2)
        return loss


def resolve_device(name: str) -> torch.device:
    """解析设备名。

    ``auto`` 按 CUDA、MPS、CPU 选择；找不到加速器时警告并回退 CPU，训练继续。
    ``gpu`` 映射为 ``cuda``。点名设备不可用时报错，不静默回退。
    """
    mapped = "cuda" if str(name) == "gpu" else str(name)
    if mapped == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        warnings.warn(
            "未检测到 CUDA 或 MPS，自动选择回退到 CPU，将继续运行", UserWarning, stacklevel=2
        )
        return torch.device("cpu")
    device = torch.device(mapped)
    if device.type not in {"cpu", "cuda", "mps"}:
        raise ValueError("仅支持 CPU/CUDA/MPS")
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA 不可用")
    if device.type == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS 不可用")
    return device


def build_optimizer(name, parameters, *, lr, weight_decay=0.0, betas=None):
    """按名构造 Adam、AdamW 或 Lion；非法种类失败。"""
    kind = str(name).lower()
    pair = tuple(betas or (0.9, 0.99))
    if kind == "adam":
        return torch.optim.Adam(parameters, lr=lr, weight_decay=weight_decay, betas=pair)
    if kind == "adamw":
        return torch.optim.AdamW(parameters, lr=lr, weight_decay=weight_decay, betas=pair)
    if kind == "lion":
        return Lion(parameters, lr=lr, weight_decay=weight_decay, betas=pair)
    raise ValueError(f"未知优化器种类: {name}")


def parameter_groups(model, *, weight_decay: float, policy: str = "exclude_bias_norm"):
    """偏置和一维参数不衰减；与官方默认优化器分组规则一致。"""
    if policy == "all":
        return [{"params": list(model.parameters()), "weight_decay": weight_decay}]
    if policy != "exclude_bias_norm":
        raise ValueError("未知权重衰减分组策略")
    decay, no_decay = [], []
    for name, value in model.named_parameters():
        if value.requires_grad:
            (no_decay if name.endswith(".bias") or value.ndim <= 1 else decay).append(value)
    return [
        {"params": decay, "weight_decay": weight_decay},
        {"params": no_decay, "weight_decay": 0.0},
    ]


def update(
    model,
    optimizer,
    step,
    batch,
    *,
    clip: float | None = 1.0,
    scaler=None,
    scheduler=None,
    accumulate: int = 1,
    accumulation_reduction: str = "mean",
    accum_index: int = 0,
    stability: bool = False,
) -> tuple:
    """循环独占清梯度、反向、解除缩放、裁剪与更新，返回有效更新标记。

    累积未满不 step；跳步不推进调度。mean 按累积步均分，sum 保留梯度和。
    """
    if clip is not None and (not math.isfinite(clip) or clip <= 0):
        raise ValueError("梯度裁剪阈值必须有限且为正")
    if accumulate < 1:
        raise ValueError("梯度累积步必须为正")
    if accumulation_reduction not in {"sum", "mean"}:
        raise ValueError("梯度累积归约必须为 sum 或 mean")
    first = accum_index % accumulate == 0
    last = (accum_index % accumulate) == accumulate - 1
    if first:
        optimizer.zero_grad(set_to_none=True)
    with torch.autocast("cuda") if scaler is not None else nullcontext():
        result = step(model, batch)
        loss = result["loss"]
    if not torch.isfinite(loss):
        raise ValueError("训练损失非有限")
    scaled = loss / accumulate if accumulation_reduction == "mean" else loss
    advanced = False
    if scaler is None:
        scaled.backward()
        if last:
            norm = _gradient_norm(model, clip, error_if_nonfinite=True)
            if stability:
                result["diagnostics"] = _stability(model, norm, None)
            optimizer.step()
            if scheduler is not None:
                scheduler.step()
            advanced = True
        return result, advanced
    before = scaler.get_scale()
    scaler.scale(scaled).backward()
    if last:
        scaler.unscale_(optimizer)
        norm = _gradient_norm(model, clip, error_if_nonfinite=False)
        if stability:
            result["diagnostics"] = _stability(model, norm, scaler)
        scaler.step(optimizer)
        scaler.update()
        advanced = scaler.get_scale() >= before
        if advanced and scheduler is not None:
            scheduler.step()
    return result, advanced


def _gradient_norm(model, clip, *, error_if_nonfinite):
    """关闭裁剪时只检查范数，不对梯度做乘法以保留原生更新算术。"""
    if clip is not None:
        return torch.nn.utils.clip_grad_norm_(
            model.parameters(), clip, error_if_nonfinite=error_if_nonfinite
        )
    gradients = [p.grad.detach() for p in model.parameters() if p.grad is not None]
    if not gradients:
        raise ValueError("训练没有任何参数梯度")
    norm = torch.linalg.vector_norm(torch.stack([g.norm() for g in gradients]))
    if error_if_nonfinite and not torch.isfinite(norm):
        raise ValueError("梯度非有限")
    return norm


def _stability(model, gradient_norm, scaler):
    """解除缩放后、裁剪前的梯度范数及更新前参数范数。"""
    with torch.no_grad():
        norm = torch.linalg.vector_norm(
            torch.stack([p.detach().float().norm() for p in model.parameters()])
        )
    return {
        "gradient_norm_before_clip": float(gradient_norm),
        "parameter_norm": float(norm),
        "scale": float(scaler.get_scale()) if scaler is not None else None,
    }
