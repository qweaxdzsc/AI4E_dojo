"""直接使用 PyTorch 张量的物理方程；不求导、不归约、不改变计算空间。"""

import math

import torch


def _fields(**fields):
    """禁止场与导数间隐式广播或设备、精度混用。"""
    first = next(iter(fields.values()))
    if not isinstance(first, torch.Tensor) or not first.is_floating_point() or not first.numel():
        raise ValueError("场必须是非空浮点张量")
    for name, value in fields.items():
        if not isinstance(value, torch.Tensor) or (
            value.shape != first.shape or value.device != first.device or value.dtype != first.dtype
        ):
            raise ValueError(f"{name}: 场与导数的 shape/device/dtype 必须一致")
    return first


def _coefficient(value, field, name, *, positive=False, nonnegative=False):
    """系数仅允许 Python 标量、同设备精度的零维或逐点张量。"""
    if isinstance(value, torch.Tensor):
        if value.shape not in (torch.Size([]), field.shape):
            raise ValueError(f"{name}: 系数必须为标量或与场形状一致")
        if value.device != field.device or value.dtype != field.dtype:
            raise ValueError(f"{name}: 系数 device/dtype 必须与场一致")
        valid = torch.isfinite(value).all()
        if positive:
            valid = valid & (value > 0).all()
        if nonnegative:
            valid = valid & (value >= 0).all()
        if not bool(valid):
            raise ValueError(f"{name}: 系数非有限或不满足物理取值范围")
    elif (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or (not math.isfinite(value) or (positive and value <= 0) or (nonnegative and value < 0))
    ):
        raise ValueError(f"{name}: 系数非有限或不满足物理取值范围")
    return value


def advection(*, u_t, u_x, velocity):
    """一维常系数对流残差 u_t + velocity*u_x。"""
    field = _fields(u_t=u_t, u_x=u_x)
    return u_t + _coefficient(velocity, field, "velocity") * u_x


def diffusion(*, u_t, u_xx, diffusivity, u_yy=None):
    """一维或二维各向同性扩散残差；输入为物理坐标导数。"""
    fields = {"u_t": u_t, "u_xx": u_xx}
    if u_yy is not None:
        fields["u_yy"] = u_yy
    field = _fields(**fields)
    alpha = _coefficient(diffusivity, field, "diffusivity", nonnegative=True)
    return u_t - alpha * (u_xx if u_yy is None else u_xx + u_yy)


def convection_diffusion(*, u_t, u_x, u_xx, velocity, diffusivity):
    """一维对流扩散残差 u_t + velocity*u_x - diffusivity*u_xx。"""
    _fields(u_t=u_t, u_x=u_x, u_xx=u_xx)
    return (
        advection(u_t=u_t, u_x=u_x, velocity=velocity)
        - _coefficient(diffusivity, u_t, "diffusivity", nonnegative=True) * u_xx
    )


def burgers(*, u, u_t, u_x, u_xx, convection_coefficient=1.0, viscosity=0.01):
    """黏性 Burgers 残差 u_t + mu*u*u_x - nu*u_xx。"""
    _fields(u=u, u_t=u_t, u_x=u_x, u_xx=u_xx)
    mu = _coefficient(convection_coefficient, u, "convection_coefficient")
    nu = _coefficient(viscosity, u, "viscosity", nonnegative=True)
    return u_t + mu * u * u_x - nu * u_xx


def navier_stokes_2d(
    *,
    u,
    v,
    u_t,
    v_t,
    u_x,
    u_y,
    v_x,
    v_y,
    p_x,
    p_y,
    u_xx,
    u_yy,
    v_xx,
    v_yy,
    density=1.0,
    kinematic_viscosity=0.01,
):
    """二维非定常不可压 NS；常密度/常运动黏度、物理压力、无体积力。

    返回 continuity/momentum_x/momentum_y 逐点残差。压力基准与初边界条件
    属于完整问题装配；本函数不隐式补充这些条件。
    """
    _fields(
        u=u,
        v=v,
        u_t=u_t,
        v_t=v_t,
        u_x=u_x,
        u_y=u_y,
        v_x=v_x,
        v_y=v_y,
        p_x=p_x,
        p_y=p_y,
        u_xx=u_xx,
        u_yy=u_yy,
        v_xx=v_xx,
        v_yy=v_yy,
    )
    rho = _coefficient(density, u, "density", positive=True)
    nu = _coefficient(kinematic_viscosity, u, "kinematic_viscosity", nonnegative=True)
    if isinstance(rho, torch.Tensor) and rho.ndim != 0:
        raise ValueError("NS density 必须为空间常量，逐点变密度需另一方程")
    if isinstance(nu, torch.Tensor) and nu.ndim != 0:
        raise ValueError("NS kinematic_viscosity 必须为空间常量")
    return {
        "continuity": u_x + v_y,
        "momentum_x": u_t + u * u_x + v * u_y + p_x / rho - nu * (u_xx + u_yy),
        "momentum_y": v_t + u * v_x + v * v_y + p_y / rho - nu * (v_xx + v_yy),
    }
