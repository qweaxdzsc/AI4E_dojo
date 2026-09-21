"""地热二十年技术经济计算；保留原成本、折现与评分公式。

源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。
"""

import numpy as np
import torch

def utilization_eff(Enthalpy):
    """地热二十年技术经济计算；保留原成本、折现与评分公式：utilization_eff；保留来源算法、参数与权重布局。"""
    return 7.8795 * np.log(Enthalpy) - 45.651

def cap_cost(depth, well_number, enthalpy, avg_heat, stimulation=None):
    """地热二十年技术经济计算；保留原成本、折现与评分公式：cap_cost；保留来源算法、参数与权重布局。"""

    def to_float(x):
        if torch.is_tensor(x):
            if x.numel() == 1:
                return x.item()
            return float(x.reshape(-1)[0])
        if isinstance(x, np.ndarray):
            if x.size == 1:
                return float(x.item())
            return float(x.reshape(-1)[0])
        return float(x)
    md_inj = to_float(depth[0])
    md_pro = to_float(depth[1])
    wn_inj = to_float(well_number[0])
    wn_pro = to_float(well_number[1])
    enthalpy = to_float(enthalpy)
    avg_heat = to_float(avg_heat)
    ue = utilization_eff(enthalpy)
    if ue > 0:
        avg_power = avg_heat * ue * 0.01
    else:
        avg_power = 0
    avg_heat_kw = avg_heat * 1000
    avg_power_kw = avg_power * 1000
    c_well_inj = round((1.72e-07 * md_inj ** 2 + 0.0023 * md_inj - 0.62) * wn_inj, 2)
    c_well_pro = round((1.72e-07 * md_pro ** 2 + 0.0023 * md_pro - 0.62) * wn_pro, 2)
    c_well = c_well_inj + c_well_pro
    c_hp = round(avg_heat_kw * 150 * 1e-06, 2)
    c_pp = round(avg_power_kw * (2000 * np.exp(-0.0045 * (avg_power - 5))) * 1e-06, 2)
    c_stimulation = round(0.3 * c_well if stimulation else 0.0, 2)
    c_fluid_distribution = round(avg_heat_kw * 50 * 1e-06, 2)
    c_exploration = round(1.12 * (1 + 0.6 * c_well), 2)
    c_pp_t = round(c_well + c_pp + c_stimulation + c_fluid_distribution + c_exploration, 2)
    c_hp_t = round(c_well + c_hp + c_stimulation + c_fluid_distribution + c_exploration, 2)
    return (c_pp_t, c_hp_t, c_well, c_pp, c_hp, c_stimulation, c_fluid_distribution, c_exploration)

def ope_cost(y_temp, y_heat, y_fluid_rate, capital_plant, capital_pump, capital_well):
    """地热二十年技术经济计算；保留原成本、折现与评分公式：ope_cost；保留来源算法、参数与权重布局。"""
    y_power = y_heat * utilization_eff(y_temp)
    if y_heat < 12.5:
        labor_hp = 236
    else:
        labor_hp = 589 * np.log(y_heat / 5) - 304
    if y_power < 2.5:
        labor_pp = 236
    else:
        labor_pp = 589 * np.log(y_power) - 304
    o_pp = round(0.75 * labor_pp * 0.001 + 0.015 * capital_plant, 2)
    o_hp = round(0.75 * labor_hp * 0.001 + 0.015 * capital_pump, 2)
    o_well_pp = round(0.25 * labor_pp * 0.001 + 0.01 * capital_well, 2)
    o_well_hp = round(0.25 * labor_hp * 0.001 + 0.01 * capital_pump, 2)
    o_water_mu = round(y_fluid_rate * 24 * 3600 * 365 * 0.001 * 0.66 * 1e-06, 2)
    o_year_pp = round(o_pp + o_well_pp, 2)
    o_year_hp = round(o_hp + o_well_hp, 2)
    return (o_year_pp, o_year_hp, o_pp, o_hp, o_water_mu)

def level_cost(temp_year, temp_avg, heat_year, heat_avg, enth_avg, rate_year, well_num, well_dep, T_threshold, CF):
    """地热二十年技术经济计算；保留原成本、折现与评分公式：level_cost；保留来源算法、参数与权重布局。"""
    heat_total, power_total, LCOH, LCOE, power_year = ([], [], [], [], [])
    for i in range(temp_avg.shape[0]):
        cc_pp_t, cc_hp_t, cc_well, cc_pp, cc_hp, cc_sti, cc_flu, cc_exp = cap_cost(well_dep[i], well_num[i], enth_avg[i], heat_avg[i])
        om_all_pp = 0.0
        om_all_hp = 0.0
        for j in range(20):
            om_year_pp, om_year_hp, om_pp, om_hp, om_wat = ope_cost(temp_year[i, j], heat_year[i, j], rate_year[i, j], cc_pp, cc_hp, cc_well)
            om_ann_pp = om_year_pp / (1 + 0.1) ** j
            om_all_pp += om_ann_pp
            om_ann_hp = om_year_hp / (1 + 0.1) ** j
            om_all_hp += om_ann_hp
        om_pp = om_all_pp + om_wat * 20
        om_hp = om_all_hp + om_wat * 20
        c_pp_all = cc_pp_t + om_pp
        c_hp_all = cc_hp_t + om_hp
        heat_all, power_all = (0, 0)
        heat_case = heat_year[i]
        temp_case = temp_year[i]
        heat_y0 = heat_case[0] * CF * 365 * 24 / 2
        ue = utilization_eff(enth_avg[i]) * 0.025
        ue = ue if ue > 0 else 0.0
        power_case = []
        for y in range(20):
            p_case = heat_case[y] * ue
            power_case.append(p_case)
        power_case = np.array(power_case).reshape(-1, 1)
        power_year.append(power_case.flatten())
        power_y0 = power_case[0] * CF * 365 * 24 / 2
        for z in range(19):
            heat_prod_year = (heat_case[z] + heat_case[z + 1]) * CF * 365 * 24 / 2
            heat_prod_year = heat_prod_year / (1 + 0.1) ** z
            heat_all += heat_prod_year
            power_prod_year = (power_case[z] + power_case[z + 1]) * 365 * 24 / 2
            power_prod_year = power_prod_year / (1 + 0.1) ** z
            power_all += power_prod_year
        heat_all = heat_y0 + heat_all
        heat_total.append(heat_all)
        power_all = power_y0 + power_all
        power_total.append(power_all)
        lcoh = c_hp_all * 1000000.0 / heat_all
        LCOH.append(lcoh)
        if temp_year[i, -1] < T_threshold:
            LCOE.append(0)
        else:
            lcoe = c_pp_all * 1000000.0 / (power_all * 1000.0)
            LCOE.append(float(np.asarray(lcoe).item()))
    LCOH = np.array(LCOH).reshape(-1, 1)
    LCOE = np.array(LCOE).reshape(-1, 1)
    heat_all = np.array(heat_total).reshape(-1, 1)
    power_all = np.array(power_total).reshape(-1, 1)
    power_year = np.array(power_year)
    return (LCOH, LCOE, heat_all, power_all, power_year)

def score_tech_econ(eco_para, tech_para, Pinj, P):
    """地热二十年技术经济计算；保留原成本、折现与评分公式：score_tech_econ；保留来源算法、参数与权重布局。"""
    eco_para = np.asarray(eco_para).reshape(-1)
    tech_para = np.asarray(tech_para).reshape(-1)
    Pinj_year = np.asarray(Pinj) / 1000000.0
    Pinj_max = Pinj_year.max(axis=1)
    eco_score = np.zeros_like(eco_para, dtype=float)
    tech_score = np.zeros_like(tech_para, dtype=float)
    eco_valid_mask = (eco_para > 0) & np.isfinite(eco_para)
    if eco_valid_mask.any():
        eco_valid = eco_para[eco_valid_mask]
        eco_min = eco_valid.min()
        eco_max = eco_valid.max()
        eco_range = eco_max - eco_min
        eco_score[eco_valid_mask] = 5.0 * (eco_max - eco_valid) / eco_range
    tech_valid_mask = (tech_para > 0) & np.isfinite(tech_para)
    if tech_valid_mask.any():
        tech_valid = tech_para[tech_valid_mask]
        tech_min = tech_valid.min()
        tech_max = tech_valid.max()
        tech_range = tech_max - tech_min
        tech_score[tech_valid_mask] = 5.0 * (tech_valid - tech_min) / tech_range
    eco_score = np.round(eco_score, 3)
    tech_score = np.round(tech_score, 3)
    return (eco_score, tech_score)
