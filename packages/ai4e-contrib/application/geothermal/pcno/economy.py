"""发布字段到地热经济输入的连接；井级取均值和求和按原源码。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import numpy as np
import torch
import pandas as pd
from ai4e_core.abilities.postproc.geothermal_economics import level_cost, score_tech_econ

def technical_results(qout, sp, gp, Twh_list, Hwh_list, Ewh_list, Pinj_list, stats):
    """发布字段到地热经济输入的连接；井级取均值和求和按原源码：technical_results；保留来源算法、参数与权重布局。"""
    B = qout.shape[0]
    Tpro_year, Tpro_avg = ([], [])
    Hpro_year, Hpro_avg = ([], [])
    Qpro_year, Pinj_year = ([], [])
    Enwh_avg = []
    well_num = []
    inj_depth_case_list, pro_depth_case_list = ([], [])
    well_map = sp[..., 2]
    for i in range(B):
        wm = well_map[i, ..., 0]
        inj_mask_xyz = wm == 1
        prod_mask_xyz = wm == -1
        inj_mask_xy = inj_mask_xyz.any(dim=2)
        prod_mask_xy = prod_mask_xyz.any(dim=2)
        num_inj = inj_mask_xy.sum().item()
        num_prod = prod_mask_xy.sum().item()
        well_num.append([num_inj, num_prod])
        depth = gp[i, 0] * stats['global_std'][0] + stats['global_mean'][0]
        dz = gp[i, 3] * stats['global_std'][3] + stats['global_mean'][3]
        dz_layer = dz / 5.0
        inj_mask_xyz_f = inj_mask_xyz.float()
        inj_z_count = inj_mask_xyz_f.sum(dim=2)
        inj_z_count = inj_z_count.clamp_min(1.0)
        prod_mask_xyz_f = prod_mask_xyz.float()
        prod_z_count = prod_mask_xyz_f.sum(dim=2)
        prod_z_count = prod_z_count.clamp_min(1.0)
        n_z_wells = prod_z_count[prod_mask_xy]
        well_depths = depth - dz_layer * (5.0 - n_z_wells)
        inj_depth_case_list.append(float(depth))
        pro_depth_case_list.append(float(well_depths.mean().item() if torch.is_tensor(well_depths) else well_depths.mean()))
        Twh_i = Twh_list[i]
        Hwh_i = Hwh_list[i] / 1000000.0
        Ewh_i = Ewh_list[i]
        Pinj_i = Pinj_list[i]

        def to_np(x):
            if isinstance(x, torch.Tensor):
                return x.detach().cpu().numpy()
            return np.asarray(x)
        Twh_i = to_np(Twh_i)
        Hwh_i = to_np(Hwh_i)
        Ewh_i = to_np(Ewh_i)
        Pinj_i = to_np(Pinj_i)
        T_vals, H_vals, E_vals, Q_vals, Pinj_vals = ([], [], [], [], [])
        for j in range(20):
            q_j = qout[i, ..., j]
            q_prod_xyz = q_j * prod_mask_xyz_f
            Q_xy_sum = q_prod_xyz.sum(dim=2)
            Q_xy_mean = Q_xy_sum / prod_z_count
            Qpro_wells = Q_xy_mean[prod_mask_xy]
            Q_vals.append(Qpro_wells.sum().item())
            T_vals.append(float(Twh_i[:, j].mean()))
            H_vals.append(float(Hwh_i[:, j].sum()))
            E_vals.append(float(Ewh_i[:, j].mean()))
            Pinj_vals.append(float(Pinj_i[:, j].mean()))
        Tpro_year.append(T_vals)
        Hpro_year.append(H_vals)
        Qpro_year.append(Q_vals)
        Pinj_year.append(Pinj_vals)
        Tpro_avg.append(float(np.mean(T_vals)))
        Hpro_avg.append(float(np.mean(H_vals)))
        Enwh_avg.append(float(np.mean(E_vals)))
    temp_year = np.array(Tpro_year)
    temp_avg = np.array(Tpro_avg).reshape(-1, 1)
    heat_year = np.array(Hpro_year)
    heat_avg = np.array(Hpro_avg).reshape(-1, 1)
    rate_year = np.array(Qpro_year)
    Enwh_avg = np.array(Enwh_avg)
    Pinj_year = np.array(Pinj_year)
    well_num = np.array(well_num, dtype=int)
    inj_depth_case = np.array(inj_depth_case_list).reshape(-1, 1)
    pro_depth_case = np.array(pro_depth_case_list).reshape(-1, 1)
    well_dep = np.concatenate([inj_depth_case, pro_depth_case], axis=1)
    return (temp_year, temp_avg, heat_year, heat_avg, rate_year, Enwh_avg, Pinj_year, well_num, well_dep)

def ensure_column(arr):
    """发布字段到地热经济输入的连接；井级取均值和求和按原源码：ensure_column；保留来源算法、参数与权重布局。"""
    return np.array(arr).reshape(-1)


def evaluate_economy(pred, raw, stats, T_threshold=75, CF=0.85):
    """只消费固定预测；Temp_drop 保留作者首例平均温度基准，不解释为物理初温降幅。"""
    pres_a = pred['Pres']
    Twh_a = pred['Twh']
    Hwh_a = pred['Hwh']
    Ewh_a = pred['Ewh']
    Pinj_a = pred['Pinj']
    qout_a = pred['Qout']
    s_a = raw['spatial_params']
    g_a = raw['global_params']
    T_y, T_a, H_y, H_a, q_y, E_a, P_y, N_w, D_w = technical_results(qout_a, s_a, g_a, Twh_a, Hwh_a, Ewh_a, Pinj_a, stats)
    LCOH_a, LCOE_a, heat_a, power_a, power_y_a = level_cost(T_y, T_a, H_y, H_a, E_a, q_y, N_w, D_w, T_threshold, CF)
    
    power_avg_y_a = np.mean(power_y_a, axis=1, keepdims=True)
    
    last_year_temp_a = T_y[:, -1].reshape(-1, 1)
    temp_drop_a = (T_a[0, ..., 0].mean() - last_year_temp_a) / T_a[0, ..., 0].mean()
    
    lcoh_score_a, heat_score_a = score_tech_econ(LCOH_a, heat_a, P_y, pres_a)
    t_h_score_a = lcoh_score_a + heat_score_a
    
    lcoe_score_a, power_score_a = score_tech_econ(LCOE_a, power_a, P_y, pres_a)
    t_e_score_a = lcoe_score_a + power_score_a
    
    
    df = pd.DataFrame({
        'LCOH': ensure_column(LCOH_a),
        'LCOH_score': ensure_column(lcoh_score_a),
        'Ava_Heat/MW': ensure_column(H_a),
        'Sum_Heat/GWh': ensure_column(heat_a) / 1000,
        'Heat_score': ensure_column(heat_score_a),
        'Total_Heat_score': ensure_column(t_h_score_a),
        'LCOE': ensure_column(LCOE_a),
        'LCOE_score': ensure_column(lcoe_score_a),
        'Ava_Power/MW': ensure_column(power_avg_y_a),
        'Sum_Power/GWh': ensure_column(power_a) / 1000,
        'Power_score': ensure_column(power_score_a),
        'Total_Power_score': ensure_column(t_e_score_a),
        'Temp_drop': ensure_column(temp_drop_a),
        'Pinj/MPa': ensure_column(P_y.mean(axis=1, keepdims=True) / 1e6),
        'Tpro/degC': ensure_column(T_a)
    })
    
    df = df.round(4)
    return df
