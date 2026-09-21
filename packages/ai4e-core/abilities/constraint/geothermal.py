"""五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import math
import torch
from torch import nn
from torch.nn import functional as F
from ai4e_core.abilities.postproc.wellbore import extract_wellData, process_wellResult

class PDE_F:
    """五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：PDE_F；保留来源算法、参数与权重布局。"""

    @staticmethod
    def den(p, T):
        den_0 = 1000.11
        a = 7e-07
        b = 0.00088
        pr = 100
        Tr = 25
        return den_0 * torch.exp(a * (p - pr) - b * (T - Tr))

    @staticmethod
    def vis(T):
        """保留分段物性公式，仅屏蔽未选分支的非法自变量及梯度。"""
        cond1 = T < 40
        cond2 = (T >= 40) & (T < 100)
        cond3 = T >= 100
        T1 = torch.where(cond1, T, 0.0)
        T2 = torch.where(cond2, T, 40.0)
        T3 = torch.where(cond3, T, 100.0)
        val1 = 1.787 * torch.exp(T1 * (-0.033 + 0.0001962 * T1))
        val2 = 0.001 * (1 + 0.015512 * (T2 - 20)) ** (-1.572)
        val3 = 0.02414 * 10 ** (247.8 / (T3 + 133.15))
        result = torch.where(cond1, val1, torch.where(cond2, val2, val3))
        return result * 0.001

    @staticmethod
    def ent(T):
        A = -203.606
        B = 1523.29
        C = -3196.413
        D = 2474.455
        E = 3.855326
        F = -256.5478
        H_const = -285.8304
        t = (T + 273.15) / 1000
        H_val = A * t + B * t ** 2 / 2 + C * t ** 3 / 3 + D * t ** 4 / 4 - E / t + F - H_const
        H = H_val * 1000 / 0.01802
        return H

    @staticmethod
    def harmonic_mean_x(k, eps=1e-30):
        k_l = k[:, :-2, :, :, :]
        k_c = k[:, 1:-1, :, :, :]
        k_r = k[:, 2:, :, :, :]
        mean_k_l = 2.0 * k_c * k_l / (k_c + k_l + eps)
        mean_k_r = 2.0 * k_c * k_r / (k_c + k_r + eps)
        mean_k_l = mean_k_l[:, :, 1:-1, 1:-1, :]
        mean_k_r = mean_k_r[:, :, 1:-1, 1:-1, :]
        return (mean_k_l, mean_k_r)

    @staticmethod
    def harmonic_mean_y(k, eps=1e-30):
        k_d = k[:, :, :-2, :, :]
        k_c = k[:, :, 1:-1, :, :]
        k_u = k[:, :, 2:, :, :]
        mean_k_d = 2.0 * k_c * k_d / (k_c + k_d + eps)
        mean_k_u = 2.0 * k_c * k_u / (k_c + k_u + eps)
        mean_k_d = mean_k_d[:, 1:-1, :, 1:-1, :]
        mean_k_u = mean_k_u[:, 1:-1, :, 1:-1, :]
        return (mean_k_d, mean_k_u)

    @staticmethod
    def harmonic_mean_z(k, eps=1e-30):
        k_b = k[:, :, :, :-2, :]
        k_c = k[:, :, :, 1:-1, :]
        k_f = k[:, :, :, 2:, :]
        mean_k_b = 2.0 * k_c * k_b / (k_c + k_b + eps)
        mean_k_f = 2.0 * k_c * k_f / (k_c + k_f + eps)
        mean_k_b = mean_k_b[:, 1:-1, 1:-1, :, :]
        mean_k_f = mean_k_f[:, 1:-1, 1:-1, :, :]
        return (mean_k_b, mean_k_f)

    @staticmethod
    def harmonic_mean_v(k):
        k_l = k[..., 0:-2, :]
        k_c = k[..., 1:-1, :]
        k_u = k[..., 2:, :]
        mean_k_low = 2 * k_c * k_l / (k_c + k_l)
        mean_k_up = 2 * k_c * k_u / (k_c + k_u)
        mean_k_low = mean_k_low[..., 1:-1, :, :]
        mean_k_up = mean_k_up[..., 1:-1, :, :]
        return (mean_k_low, mean_k_up)

    @staticmethod
    def upstream_x(x, p):
        p_l = p[:, :-2, :, :, :]
        p_c = p[:, 1:-1, :, :, :]
        p_r = p[:, 2:, :, :, :]
        mat_r = p_r - p_c
        pd_r = (mat_r >= 0).float()
        x_r = x[:, 1:-1, :, :, :] * (1.0 - pd_r) + x[:, 2:, :, :, :] * pd_r
        x_r = x_r[:, :, 1:-1, 1:-1, :]
        mat_l = p_c - p_l
        pd_l = (mat_l >= 0).float()
        x_l = x[:, :-2, :, :, :] * (1.0 - pd_l) + x[:, 1:-1, :, :, :] * pd_l
        x_l = x_l[:, :, 1:-1, 1:-1, :]
        return (x_r, x_l)

    @staticmethod
    def upstream_y(x, p):
        p_d = p[:, :, 2:, :, :]
        p_c = p[:, :, 1:-1, :, :]
        p_u = p[:, :, :-2, :, :]
        mat_u = p_u - p_c
        pd_u = (mat_u >= 0).float()
        x_u = x[:, :, 1:-1, :, :] * (1.0 - pd_u) + x[:, :, :-2, :, :] * pd_u
        x_u = x_u[:, 1:-1, :, 1:-1, :]
        mat_d = p_d - p_c
        pd_d = (mat_d >= 0).float()
        x_d = x[:, :, 1:-1, :, :] * (1.0 - pd_d) + x[:, :, 2:, :, :] * pd_d
        x_d = x_d[:, 1:-1, :, 1:-1, :]
        return (x_u, x_d)

    @staticmethod
    def upstream_z(x, p):
        p_b = p[:, :, :, :-2, :]
        p_c = p[:, :, :, 1:-1, :]
        p_f = p[:, :, :, 2:, :]
        mat_f = p_f - p_c
        pd_f = (mat_f >= 0).float()
        x_f = x[:, :, :, 1:-1, :] * (1.0 - pd_f) + x[:, :, :, 2:, :] * pd_f
        x_f = x_f[:, 1:-1, 1:-1, :, :]
        mat_b = p_b - p_c
        pd_b = (mat_b >= 0).float()
        x_b = x[:, :, :, 1:-1, :] * (1.0 - pd_b) + x[:, :, :, :-2, :] * pd_b
        x_b = x_b[:, 1:-1, 1:-1, :, :]
        return (x_f, x_b)

class physical_loss(nn.Module):
    """五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：physical_loss；保留来源算法、参数与权重布局。"""

    def __init__(self, T_i, p_i, Cp_r, lam_r, dz, q_inj, pwf, T_inj, k, phi, depth, dt=24 * 3600 * 365, dx=10.0, dy=10.0):
        super().__init__()
        self.dx, self.dy, self.dt = (float(dx), float(dy), dt)
        self.T_i, self.p_i = (T_i, p_i)
        self.Cp_r, self.lam_r = (Cp_r, lam_r)
        self.pwf, self.k, self.d = (pwf, k, depth)
        self.dz = dz / 5.0
        self.q_inj, self.T_inj = (q_inj, T_inj)
        self.k_unit_conversion = 9.86923e-16
        self.cc = 0.249
        self.rw = 0.0762
        self.re = self.cc * math.sqrt((self.dx ** 2 + self.dy ** 2) / math.pi)
        self.log_re_rw = math.log(self.re / self.rw)
        self.block_v = dx * dy * self.dz
        self.fluid_v = self.block_v * phi
        self.rock_v = self.block_v - self.fluid_v
        self.lam_fluid = 56000.0 / (24 * 3600)
        self.lam_rock = lam_r / (24 * 3600)
        self.lam_eff = self.lam_fluid * (self.lam_rock / self.lam_fluid) ** 0.6354

    def phy_loss(self, p_pred, T_pred):
        device = p_pred.device
        S_c = (slice(None), slice(1, -1), slice(1, -1), slice(1, -1), slice(1, None))

        def pad_3D(x, mode='replicate'):
            x = x.permute(0, 4, 3, 2, 1)
            x = F.pad(x, (1, 1, 1, 1, 1, 1), mode=mode)
            x = x.permute(0, 4, 3, 2, 1)
            return x
        p_pred = pad_3D(p_pred)
        T_pred = pad_3D(T_pred)
        k_pad = pad_3D(self.k)
        pwf_pad = pad_3D(self.pwf)
        q_inj_pad = pad_3D(self.q_inj.to(device))
        T_inj_pad = pad_3D(self.T_inj.to(device))
        p_Pa = p_pred * 1000000.0
        p_kPa = p_Pa / 1000.0
        rho = torch.clamp(PDE_F.den(p_kPa, T_pred), 500.0, 2000.0)
        mu = torch.clamp(PDE_F.vis(T_pred), 0.0001, 10.0)
        h = PDE_F.ent(T_pred)
        h = torch.nan_to_num(h, nan=0.0, posinf=10000000.0, neginf=-10000000.0).clamp(-1000000.0, 1000000.0)
        k = (k_pad * self.k_unit_conversion).to(device=device)
        T_c, p_c, rho_c, mu_c, h_c, k_c = (T_pred[S_c], p_Pa[S_c], rho[S_c], mu[S_c], h[S_c], k[S_c])
        p_t, rho_t, mu_t, h_t, k_t = (p_Pa[..., 1:], rho[..., 1:], mu[..., 1:], h[..., 1:], k[..., 1:])
        dz_b = self.dz.to(device=k_c.device, dtype=k_c.dtype).view(-1, 1, 1, 1, 1)
        pwf_local = pwf_pad.to(device)[S_c] * -1.0 * 1000.0
        pwf_mask = (pwf_local != 0).to(p_c.dtype)
        q_inj = q_inj_pad[S_c] * 1001.7 / 24 / 3600
        H_inj = PDE_F.ent(T_inj_pad)[S_c]
        energy_inj = q_inj * H_inj
        I = 2.0 * math.pi * k_c * dz_b / self.log_re_rw
        inj_mask = (q_inj != 0).to(p_c.dtype)
        P_inj = q_inj / (I * (1.0 / mu_c)) / rho_c + p_c
        p_block = p_c * pwf_mask
        q_out = I * (1.0 / mu_c) * (pwf_local - p_block) * rho_c
        q_out = q_out * -1
        energy_out = q_out * h_c
        heat_pro = q_out * (h_c - H_inj)
        fluid_v = self.fluid_v.to(device=device, dtype=k_c.dtype)[..., 1:]
        rock_v = self.rock_v.to(device=device, dtype=k_c.dtype)[..., 1:]
        rho_next, rho_last = (rho[:, 1:-1, 1:-1, 1:-1, 1:], rho[:, 1:-1, 1:-1, 1:-1, :-1])
        T_next, T_last = (T_pred[:, 1:-1, 1:-1, 1:-1, 1:], T_pred[:, 1:-1, 1:-1, 1:-1, :-1])
        p_next, p_last = (p_Pa[:, 1:-1, 1:-1, 1:-1, 1:], p_Pa[:, 1:-1, 1:-1, 1:-1, :-1])
        h_next, h_last = (h[:, 1:-1, 1:-1, 1:-1, 1:], h[:, 1:-1, 1:-1, 1:-1, :-1])
        p_r, p_l = (p_Pa[:, 2:, 1:-1, 1:-1, 1:], p_Pa[:, 0:-2, 1:-1, 1:-1, 1:])
        p_u, p_d = (p_Pa[:, 1:-1, 0:-2, 1:-1, 1:], p_Pa[:, 1:-1, 2:, 1:-1, 1:])
        p_b, p_f = (p_Pa[:, 1:-1, 1:-1, 0:-2, 1:], p_Pa[:, 1:-1, 1:-1, 2:, 1:])
        T_r, T_l = (T_pred[:, 2:, 1:-1, 1:-1, 1:], T_pred[:, 0:-2, 1:-1, 1:-1, 1:])
        T_u, T_d = (T_pred[:, 1:-1, 0:-2, 1:-1, 1:], T_pred[:, 1:-1, 2:, 1:-1, 1:])
        T_b, T_f = (T_pred[:, 1:-1, 1:-1, 0:-2, 1:], T_pred[:, 1:-1, 1:-1, 2:, 1:])
        Ax, Ay, Az = (self.dy * dz_b, self.dx * dz_b, self.dx * self.dy)
        rho_r, rho_l = PDE_F.upstream_x(rho_t, p_t)
        rho_u, rho_d = PDE_F.upstream_y(rho_t, p_t)
        rho_f, rho_b = PDE_F.upstream_z(rho_t, p_t)
        mu_r, mu_l = PDE_F.upstream_x(mu_t, p_t)
        mu_u, mu_d = PDE_F.upstream_y(mu_t, p_t)
        mu_f, mu_b = PDE_F.upstream_z(mu_t, p_t)
        h_r, h_l = PDE_F.upstream_x(h_t, p_t)
        h_u, h_d = PDE_F.upstream_y(h_t, p_t)
        h_f, h_b = PDE_F.upstream_z(h_t, p_t)
        k_l, k_r = PDE_F.harmonic_mean_x(k_t)
        k_d, k_u = PDE_F.harmonic_mean_y(k_t)
        k_b, k_f = PDE_F.harmonic_mean_z(k_t)
        tx_r = rho_r / mu_r * k_r * (Ax / self.dx)
        tx_l = rho_l / mu_l * k_l * (Ax / self.dx)
        ty_u = rho_u / mu_u * k_u * (Ay / self.dy)
        ty_d = rho_d / mu_d * k_d * (Ay / self.dy)
        tz_b = rho_b / mu_b * k_b * (Az / self.dz)
        tz_f = rho_f / mu_f * k_f * (Az / self.dz)
        mass_flux = tx_r * (p_r - p_c) + tx_l * (p_l - p_c) + ty_u * (p_u - p_c) + ty_d * (p_d - p_c) + tz_f * (p_f - p_c) + tz_b * (p_b - p_c)
        mass_acc = (rho_next - rho_last) * fluid_v / self.dt
        mass_residual = mass_acc - mass_flux - (q_inj + q_out)
        mse_mass = torch.mean(torch.abs(mass_residual)) * 0.5
        energy_acc = (fluid_v * rho_next * (h_next - p_next / rho_next) + rock_v * (self.Cp_r * T_next) - (fluid_v * rho_last * (h_last - p_last / rho_last) + rock_v * (self.Cp_r * T_last))) / self.dt
        lam_r = rho_r / mu_r * h_r * k_r * (Ax / self.dx)
        lam_l = rho_l / mu_l * h_l * k_l * (Ax / self.dx)
        lam_u = rho_u / mu_u * h_u * k_u * (Ay / self.dy)
        lam_d = rho_d / mu_d * h_d * k_d * (Ay / self.dy)
        lam_b = rho_b / mu_b * h_b * k_b * (Az / self.dz)
        lam_f = rho_f / mu_f * h_f * k_f * (Az / self.dz)
        energy_conv = lam_r * (p_r - p_c) + lam_l * (p_l - p_c) + lam_u * (p_u - p_c) + lam_d * (p_d - p_c) + lam_f * (p_f - p_c) + lam_b * (p_b - p_c)
        energy_cond = self.lam_eff * ((T_r - T_c + T_l - T_c) * (Ax / self.dx) + (T_u - T_c + T_d - T_c) * (Ay / self.dy) + (T_f - T_c + T_b - T_c) * (Az / self.dz))
        energy_residual = energy_acc - energy_conv - energy_cond - (energy_inj - energy_out)
        mse_energy = torch.mean(torch.abs(energy_residual)) * 1e-08
        B = p_pred.shape[0]
        T_out_map = T_c
        q_out_map = q_out
        P_out_map = p_c
        heat_map = heat_pro
        Pinj_map = P_inj
        BHT_list = extract_wellData(T_out_map, pwf_mask)
        BHQ_list = extract_wellData(q_out_map, pwf_mask)
        BHP_list = extract_wellData(P_out_map / 1000000.0, pwf_mask)
        BHH_list = extract_wellData(heat_map, pwf_mask)
        dz_list = [float(self.d)] * B
        grad_T_list = [float(self.T_i.max().item() / self.d)] * B
        TC_list = self.lam_r
        Cp_list = self.Cp_r
        Temp_wh, Q_loss, Pres_wh, Enth_wh = process_wellResult(dz_list=dz_list, grad_T_list=grad_T_list, BHT_list=BHT_list, BHP_list=BHP_list, BHQ_list=BHQ_list, TC_list=TC_list, Cp_list=Cp_list)
        Heat_wh = [a - b for a, b in zip(BHH_list, Q_loss)]
        P_inj = extract_wellData(Pinj_map, inj_mask)
        return (mse_mass, mse_energy, Temp_wh, Heat_wh, P_inj, Enth_wh, q_out)

def compute_loss(p_out, T_out, loss_func, Temp_wh_t, Heat_wh_t, P_inj_t):
    """五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：compute_loss；保留来源算法、参数与权重布局。"""
    mse_mass, mse_energy, Temp_wh, Heat_wh, P_inj, Enth_wh, q_out = loss_func.phy_loss(p_out, T_out)

    def re_task(a, b, eps=1e-08):
        if torch.is_tensor(a) and torch.is_tensor(b):
            rel = torch.abs(a - b) / (torch.abs(b) + eps)
            return rel.mean()
        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            if len(a) == 0 or len(b) == 0:
                dev = mse_mass.device if hasattr(mse_mass, 'device') else 'cpu'
                return torch.tensor(0.0, device=dev)
            dev = a[0].device if torch.is_tensor(a[0]) else mse_mass.device if hasattr(mse_mass, 'device') else 'cpu'
            total_error = torch.tensor(0.0, device=dev)
            total_count = 0
            for x, y in zip(a, b):
                if not (torch.is_tensor(x) and torch.is_tensor(y)):
                    raise TypeError('Elements in list must be torch.Tensor')
                rel = torch.abs(x - y) / (torch.abs(y) + eps)
                total_error = total_error + rel.sum()
                total_count += rel.numel()
            if total_count == 0:
                return torch.tensor(0.0, device=dev)
            return total_error / float(total_count)
        raise TypeError(f're_task is not Tensor or list, but {type(a)} and {type(b)}')
    re_Twh = re_task(Temp_wh, Temp_wh_t) * 0.1
    re_Ewh = re_task(Heat_wh, Heat_wh_t) * 0.1
    re_Pinj = re_task(P_inj, P_inj_t) * 0.1
    return (mse_mass, mse_energy, re_Twh, re_Ewh, re_Pinj)
