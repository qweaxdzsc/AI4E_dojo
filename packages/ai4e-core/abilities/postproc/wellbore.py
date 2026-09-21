"""井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import math
import numpy as np
import torch
from iapws import IAPWS97

class WellboreModel:
    """井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：WellboreModel；保留来源算法、参数与权重布局。"""

    def __init__(self, flow_rate, R_TC, R_cp, tubing_id=0.18, tubing_od=0.2, angle=90, R_rho=2500, U=10, rough=1e-05):
        self.w = flow_rate
        self.d = tubing_id
        self.r_to = tubing_od / 2.0
        self.theta = np.radians(angle)
        self.k_e = R_TC
        self.rho_e = R_rho
        self.cp_e = R_cp
        self.g = 9.80665
        self.U_to = U
        self.eps = rough
        self.pump_depth = 1500.0
        self.pump_dp = 10.0

    def friction(self, rho_m, mu_m, v_m):
        Re = rho_m * abs(v_m) * self.d / mu_m
        if not np.isfinite(Re) or Re <= 0.0:
            return 0.0
        Re = float(Re)
        f = None
        Lambda = (self.eps / self.d) ** 1.1098 / 2.8257 + 7.149 / Re ** 0.8981
        if np.isfinite(Lambda) and Lambda > 0.0:
            term = self.eps / self.d / 3.7065 - 5.0452 / Re * np.log10(Lambda)
            if np.isfinite(term) and term > 0.0:
                logt = np.log10(term)
                if np.isfinite(logt):
                    f_candidate = 1.0 / (4.0 * logt ** 2)
                    if np.isfinite(f_candidate) and f_candidate >= 0.0:
                        f = float(f_candidate)
        if f is None:
            f_blasius = 0.3164 / Re ** 0.25
            if np.isfinite(f_blasius) and f_blasius >= 0.0:
                f = float(f_blasius)
            else:
                f = 0.0
        return f

    @staticmethod
    def ramey(t_D):
        if t_D <= 0.0:
            return 0.0
        inner = np.log(np.exp(-0.2) * t_D) + 1.5 - 0.3719 * np.exp(-t_D)
        return inner * np.sqrt(t_D)

    def select_flow_pattern(self, v_sg, v_sL, rho_g, rho_L, mu_g, mu_L, sigma):
        vm = v_sg + v_sL
        if vm <= 0.0 or rho_L <= rho_g:
            return ('single_phase', 1.0, 0.0, 0.0)
        g = self.g
        d = self.d
        v_inf_b = 1.53 * (g * sigma * (rho_L - rho_g) / rho_L ** 2) ** 0.25
        v_inf_T = 0.35 * np.sqrt(g * d * (rho_L - rho_g) / rho_L)
        v_gb = 0.429 * v_sL + 0.357 * v_inf_b
        if v_sg > v_gb and v_sg - v_gb > 1e-08:
            expo = np.exp(-0.1 * v_gb / (v_sg - v_gb))
            v_inf_avg = v_inf_b * (1.0 - expo) + v_inf_T * expo
        else:
            v_inf_avg = v_inf_b
        v_ann = 3.1 * (g * sigma * (rho_L - rho_g) / rho_L ** 2) ** 0.25
        C0_trial = 1.2
        v_inf_trial = v_inf_b if v_inf_T <= v_inf_b else v_inf_avg
        fg_trial = v_sg / (C0_trial * vm + v_inf_trial)
        fg_trial = float(np.clip(fg_trial, 0.0, 0.999))
        rho_m_trial = fg_trial * rho_g + (1.0 - fg_trial) * rho_L
        x_mass = fg_trial
        mu_m_trial = mu_g * x_mass + mu_L * (1.0 - x_mass)
        f_m = self.friction(rho_m_trial, mu_m_trial, vm)
        LHS = 2.0 * vm ** 1.2 * (f_m / (2.0 * d)) ** 0.4 * (rho_L / sigma) ** 0.6 * (0.4 * sigma / (g * (rho_L - rho_g))) ** 0.5
        RHS = 0.725 + 4.15 * np.sqrt(v_sg / vm)
        flow_regime = None
        if fg_trial > 0.85 and v_sg > v_ann:
            flow_regime = 'annular'
        else:
            if fg_trial < 0.25:
                flow_regime = 'bubbly'
            if v_sg > v_gb:
                flow_regime = 'slug'
                if v_sg > 1.08 * v_sL:
                    flow_regime = 'churn'
            if LHS > RHS:
                if fg_trial < 0.58:
                    flow_regime = 'dispersed_bubbly'
                if v_sg > 1.08 * v_sL:
                    flow_regime = 'churn'
        if flow_regime is None:
            flow_regime = 'bubbly'
        if flow_regime == 'bubbly':
            C0 = 1.2
            v_inf = v_inf_b
        elif flow_regime == 'slug':
            C0 = 1.2
            v_inf = v_inf_avg
        elif flow_regime == 'churn':
            C0 = 1.15
            v_inf = v_inf_avg
        elif flow_regime == 'dispersed_bubbly':
            C0 = 1.15
            v_inf = v_inf_b
        elif flow_regime == 'annular':
            C0 = 1.0
            v_inf = 0.0
        else:
            C0 = 1.0
            v_inf = 0.0
        fg = v_sg / (C0 * vm + v_inf)
        fg = float(np.clip(fg, 0.0, 0.999))
        return (flow_regime, C0, v_inf, fg)

    def solve_step(self, P_MPa, h_kJkg, T_ei_C, t_days, r_wb_m=None):
        P_MPa = float(P_MPa)
        h_kJkg = float(h_kJkg)
        T_ei_C = float(T_ei_C)
        if not np.isfinite(P_MPa):
            P_MPa = 10.0
        P_MPa = float(np.clip(P_MPa, 0.1, 80.0))
        if not np.isfinite(h_kJkg):
            h_kJkg = 1000.0
        h_kJkg = float(np.clip(h_kJkg, 100.0, 4000.0))
        if not np.isfinite(T_ei_C):
            T_ei_C = 100.0
        T_ei_C = float(np.clip(T_ei_C, 0.0, 350.0))
        T_K = T_ei_C + 273.15
        T_K = float(np.clip(T_K, 273.15, 1073.15))
        try:
            fluid = IAPWS97(P=P_MPa, h=h_kJkg)
        except NotImplementedError:
            try:
                fluid = IAPWS97(P=P_MPa, T=T_K)
                h_kJkg = fluid.h
            except NotImplementedError:
                fluid = IAPWS97(P=P_MPa, x=0)
                h_kJkg = fluid.h
        T_f_C = fluid.T - 273.15
        if P_MPa < 22.064 and np.isfinite(P_MPa):
            sat_L = IAPWS97(P=P_MPa, x=0)
            sat_g = IAPWS97(P=P_MPa, x=1)
            h_L, h_g = (sat_L.h, sat_g.h)
            if h_kJkg <= h_L:
                x = 0.0
                rho_L = rho_g = fluid.rho
                mu_L = mu_g = fluid.mu
                sigma = sat_L.sigma
                cp_mix_kJ = fluid.cp
            elif h_kJkg >= h_g:
                x = 1.0
                rho_L = rho_g = fluid.rho
                mu_L = mu_g = fluid.mu
                sigma = sat_L.sigma
                cp_mix_kJ = fluid.cp
            else:
                x = (h_kJkg - h_L) / (h_g - h_L)
                x = float(np.clip(x, 0.0, 1.0))
                rho_L, rho_g = (sat_L.rho, sat_g.rho)
                mu_L, mu_g = (sat_L.mu, sat_g.mu)
                sigma = sat_L.sigma
                cp_L_kJ = sat_L.cp
                cp_g_kJ = sat_g.cp
                cp_mix_kJ = x * cp_g_kJ + (1.0 - x) * cp_L_kJ
        else:
            x = 0.0
            rho_L = rho_g = fluid.rho
            mu_L = mu_g = fluid.mu
            sigma = 0.05
            cp_mix_kJ = fluid.cp
        A = np.pi * self.d ** 2 / 4.0
        if x <= 0.0:
            q_L = self.w / rho_L
            v_sL = q_L / A
            v_sg = 0.0
        elif x >= 1.0:
            q_g = self.w / rho_g
            v_sg = q_g / A
            v_sL = 0.0
        else:
            q_g = self.w * x / rho_g
            q_L = self.w * (1.0 - x) / rho_L
            v_sg = q_g / A
            v_sL = q_L / A
        v_m = v_sg + v_sL
        if x <= 0.0:
            f_g = 0.0
        elif x >= 1.0:
            f_g = 1.0
        else:
            flow_regime, C0, v_inf, f_g = self.select_flow_pattern(v_sg=v_sg, v_sL=v_sL, rho_g=rho_g, rho_L=rho_L, mu_g=mu_g, mu_L=mu_L, sigma=sigma)
        rho_m = rho_g * f_g + rho_L * (1.0 - f_g)
        mu_m = mu_g * x + mu_L * (1.0 - x)
        f_fric = self.friction(rho_m, mu_m, v_m)
        grad_fric_Pa_per_m = f_fric * rho_m * v_m ** 2 / (2.0 * self.d)
        grad_grav_Pa_per_m = rho_m * self.g * np.sin(self.theta)
        dp_dz_sf_MPa = -(grad_grav_Pa_per_m + grad_fric_Pa_per_m) / 1000000.0
        if r_wb_m is None:
            r_wb_m = self.r_to
        t_sec = t_days * 24.0 * 3600.0
        t_D = self.k_e * t_sec / (self.rho_e * self.cp_e * r_wb_m ** 2)
        T_D = self.ramey(t_D)
        cp_f = cp_mix_kJ * 1000.0
        L_R = 2.0 * np.pi / (self.w * cp_f) * (self.r_to * self.U_to * self.k_e) / (self.k_e + self.r_to * self.U_to * T_D)
        Q_wb_per_m = L_R * self.w * cp_f * (T_f_C - T_ei_C)
        grav_term_kJkg_per_m = -self.g * np.sin(self.theta) / 1000.0
        heat_term_kJkg_per_m = Q_wb_per_m / self.w / 1000.0
        dh_dz_no_acc = grav_term_kJkg_per_m - heat_term_kJkg_per_m
        return (dp_dz_sf_MPa, dh_dz_no_acc, v_m, rho_m, x, f_g, T_f_C, Q_wb_per_m)

    def simulate(self, depth, P_btm, Tf_btm, T_grad, T_surf=15, steps=40, t_days=0.0):
        P_btm = float(P_btm)
        Tf_btm = float(Tf_btm)
        if not np.isfinite(P_btm):
            P_btm = 10.0
        P_btm = float(np.clip(P_btm, 0.1, 80.0))
        if not np.isfinite(Tf_btm):
            Tf_btm = 100.0
        Tf_btm = float(np.clip(Tf_btm, 0.0, 350.0))
        Tf_btm_K = Tf_btm + 273.15
        Tf_btm_K = float(np.clip(Tf_btm_K, 273.15, 1073.15))
        try:
            fluid_btm = IAPWS97(P=P_btm, T=Tf_btm_K)
        except NotImplementedError:
            P_btm = float(np.clip(P_btm, 0.5, 50.0))
            Tf_btm_K = float(np.clip(Tf_btm_K, 300.0, 800.0))
            fluid_btm = IAPWS97(P=P_btm, T=Tf_btm_K)
        dz = depth / steps
        P_curr = P_btm
        h_curr = fluid_btm.h
        v_m_prev = None
        rho_ref = fluid_btm.rho
        P_surf_MPa = 0.1
        P_hydro_MPa = P_surf_MPa + rho_ref * self.g * depth / 1000000.0
        use_pump = P_btm < P_hydro_MPa
        pump_applied = False
        z_list = []
        P_list = []
        T_list = []
        h_list = []
        Q_per_m_list = []
        for i in range(steps + 1):
            z_curr = depth - i * dz
            T_ei = T_surf + T_grad * z_curr
            dp_dz_sf_MPa, dh_dz_no_acc, v_m, rho_m, x, f_g, T_f_C, Q_loss = self.solve_step(P_curr, h_curr, T_ei, t_days)
            z_list.append(z_curr)
            P_list.append(P_curr)
            T_list.append(T_f_C)
            h_list.append(h_curr)
            Q_per_m_list.append(Q_loss)
            if i < steps:
                if v_m_prev is None:
                    dv_dz = 0.0
                else:
                    dv_dz = (v_m - v_m_prev) / dz
                acc_term_MPa_per_m = rho_m * v_m * dv_dz / 1000000.0
                dp_dz = dp_dz_sf_MPa - acc_term_MPa_per_m
                dh_dz = dh_dz_no_acc - v_m * dv_dz / 1000.0
                P_curr += dp_dz * dz
                h_curr += dh_dz * dz
                v_m_prev = v_m
                if use_pump and (not pump_applied):
                    z_next = z_curr - dz
                    if z_curr >= self.pump_depth and z_next <= self.pump_depth:
                        P_curr += self.pump_dp
                        pump_applied = True
                if P_curr < 1:
                    P_curr = 1
        T_wellhead = T_list[-1]
        P_wellhead = P_list[-1]
        h_wellhead = h_curr
        Q_loss_total = sum(Q_per_m_list) * dz
        return (T_wellhead, P_wellhead, Q_loss_total, h_wellhead)

def wellbore_model_run(BHT, BHP, depth, T_grad, m_dot, R_TC, R_cp):
    """井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：wellbore_model_run；保留来源算法、参数与权重布局。"""
    well = WellboreModel(flow_rate=m_dot, R_TC=R_TC, R_cp=R_cp)
    T_wh, P_wh, Q_loss_total, h_wh = well.simulate(depth=depth, P_btm=BHP, Tf_btm=BHT, T_grad=T_grad)
    return (T_wh, P_wh, Q_loss_total, h_wh)

def extract_wellData(field, mask):
    """井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：extract_wellData；保留来源算法、参数与权重布局。"""
    B, X, Y, Z, T = field.shape
    device = field.device
    dtype = field.dtype
    if mask.dim() == 5:
        mask = mask.any(dim=-1)
    elif mask.dim() == 4:
        mask = mask.bool()
    result = []
    for b in range(B):
        field_b = field[b]
        mask_b = mask[b]
        active_xy = mask_b.any(dim=2)
        coords_xy = torch.nonzero(active_xy, as_tuple=False)
        well_ts_list = []
        for coord_xy in coords_xy:
            x, y = coord_xy.tolist()
            mask_z = mask_b[x, y, :]
            if not mask_z.any():
                continue
            ts_blocks = field_b[x, y, mask_z, :]
            ts = ts_blocks.mean(dim=0)
            well_ts_list.append(ts)
        if well_ts_list:
            well_ts_tensor = torch.stack(well_ts_list, dim=0)
        else:
            well_ts_tensor = torch.zeros(0, T, device=device, dtype=dtype)
        result.append(well_ts_tensor)
    return result

def process_wellResult(dz_list, grad_T_list, BHT_list, BHP_list, BHQ_list, TC_list, Cp_list):
    """井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：process_wellResult；保留来源算法、参数与权重布局。"""
    Twh_list = []
    Q_loss_list = []
    Pwh_list = []
    hwh_list = []
    for sample_idx in range(len(BHT_list)):
        bht_tensor = BHT_list[sample_idx]
        bhq_tensor = BHQ_list[sample_idx]
        bhp_tensor = BHP_list[sample_idx]
        grad_T = float(grad_T_list[sample_idx])
        depth = float(dz_list[sample_idx])
        TC_tensor = TC_list[sample_idx]
        Cp_tensor = Cp_list[sample_idx]
        R_TC = float(TC_tensor.mean().item())
        R_cp = float(Cp_tensor.mean().item())
        N_i, Tn = bht_tensor.shape
        T_outs = torch.zeros(N_i, Tn, dtype=bht_tensor.dtype, device=bht_tensor.device)
        Q_losses = torch.zeros(N_i, Tn, dtype=bht_tensor.dtype, device=bht_tensor.device)
        Pwh = torch.zeros(N_i, Tn, dtype=bht_tensor.dtype, device=bht_tensor.device)
        hwh = torch.zeros(N_i, Tn, dtype=bht_tensor.dtype, device=bht_tensor.device)
        for well_idx in range(N_i):
            for t in range(Tn):
                T0 = float(bht_tensor[well_idx, t].item())
                m_dot = float(bhq_tensor[well_idx, t].item())
                P_btm = float(bhp_tensor[well_idx, t].item())
                T_wh, P_wh, Q_loss_total, h_wh = wellbore_model_run(BHT=T0, BHP=P_btm, depth=depth, T_grad=grad_T, m_dot=m_dot, R_TC=R_TC, R_cp=R_cp)
                T_outs[well_idx, t] = T_wh
                Q_losses[well_idx, t] = Q_loss_total
                Pwh[well_idx, t] = P_wh
                hwh[well_idx, t] = h_wh
        Twh_list.append(T_outs)
        Q_loss_list.append(Q_losses)
        Pwh_list.append(Pwh)
        hwh_list.append(hwh)
    return (Twh_list, Q_loss_list, Pwh_list, hwh_list)
