"""梯形参考坐标到物理导数的完整链式变换，不计算物理方程。"""


def physical_derivatives(*, xi, eta, u_xi, u_eta, u_xixi, u_xieta, u_etaeta):
    """映射 X=-1+eta/2+xi*(2-eta), Y=eta 的一二阶导数。

    固定 X 时 dxi/dY=(xi-1/2)/(2-eta)，其二阶项不能省略。
    输入可为 numpy 数组或 torch 张量；不搬运设备或断开梯度。
    """
    width = 2 - eta
    slope = (xi - 0.5) / width
    return {
        "u_x": u_xi / width,
        "u_y": u_eta + slope * u_xi,
        "u_xx": u_xixi / width**2,
        "u_yy": u_etaeta + 2 * slope * u_xieta + slope**2 * u_xixi + 2 * slope / width * u_xi,
    }
