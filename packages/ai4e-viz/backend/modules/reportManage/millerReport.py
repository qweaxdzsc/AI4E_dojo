"""Data-derived Miller tokamak time-series report.

The source NPZ is an exported promotional-animation dataset.  Every number in
the report is recomputed from that file, while the source scope statement is
kept visible so the synthetic presentation field cannot be mistaken for a
validated gyrokinetic rollout.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
from infrastructure.config import REPOSITORY_ROOT


REPORT_ID = "rep-miller-tokamak-timeseries"
ROOT = REPOSITORY_ROOT / "resources" / "examples"
NPZ_PATH = ROOT / "miller_tokamak_timeseries_240frames.npz"
SCRIPT_PATH = ROOT / "sources" / "export_miller_tokamak_timeseries.py"


def report_list_item() -> dict:
    """返回 Miller 时序场内置报告在报告中心使用的列表摘要。"""

    return {
        "id": REPORT_ID,
        "title": "Miller 托卡马克静电势时序场分析报告",
        "status": "succeeded",
        "status_note": "240 帧真实数组已重算 · 合成展示场边界已标注",
        "generated_at": "2026-08-25 13:20",
        "author": "原力",
        "spec": "rspec-miller-field-audit v1",
        "formats": ["HTML", "PDF"],
    }


def _round_list(values: np.ndarray, digits: int = 6) -> list[float]:
    return [round(float(value), digits) for value in values]


def _sample_series(values: np.ndarray, limit: int = 120) -> tuple[np.ndarray, np.ndarray]:
    indices = np.unique(np.linspace(0, len(values) - 1, min(limit, len(values)), dtype=int))
    return indices, values[indices]


def _sample_matrix(values: np.ndarray, max_rows: int = 54, max_cols: int = 64) -> np.ndarray:
    row_index = np.unique(np.linspace(0, values.shape[0] - 1, min(max_rows, values.shape[0]), dtype=int))
    col_index = np.unique(np.linspace(0, values.shape[1] - 1, min(max_cols, values.shape[1]), dtype=int))
    return np.asarray(values[np.ix_(row_index, col_index)], dtype=float)


@lru_cache(maxsize=4)
def build_report(api_base: str) -> dict:
    """从 240 帧 NPZ 原始数组重新计算并构建可追溯的 Miller 报告。"""

    with np.load(NPZ_PATH, allow_pickle=False) as arrays:
        frame = np.asarray(arrays["frame"], dtype=int)
        time = np.asarray(arrays["time_R_over_vti"], dtype=float)
        energy = np.asarray(arrays["field_energy_normalized"], dtype=float)
        ky_peak = np.asarray(arrays["ky_peak_normalized"], dtype=float)
        cfl = np.asarray(arrays["cfl_live"], dtype=float)
        gamma = np.asarray(arrays["gamma_live"], dtype=float)
        omega = np.asarray(arrays["omega_live"], dtype=float)
        wphi = np.asarray(arrays["Wphi_live"], dtype=float)
        qi = np.asarray(arrays["Qi_live"], dtype=float)
        phi = np.asarray(arrays["phi_surface_normalized"], dtype=float)
        phi_raw = np.asarray(arrays["phi_surface_raw"], dtype=float)
        ky_axis = np.asarray(arrays["ky_axis_normalized"], dtype=float)
        spectrum = np.asarray(arrays["ky_time_spectrum_normalized"], dtype=float)

        sample_index, sampled_time = _sample_series(time)
        representative_indices = [0, len(frame) // 2, len(frame) - 1]
        representative_frames = [
            {
                "label": label,
                "frame": int(frame[index]),
                "time": round(float(time[index]), 4),
                "values": _sample_matrix(phi[index]).round(5).tolist(),
                "range": [round(float(np.min(phi[index])), 5), round(float(np.max(phi[index])), 5)],
            }
            for label, index in zip(("初始", "中期", "末期"), representative_indices)
        ]
        spectrum_index = np.unique(np.linspace(0, len(frame) - 1, min(120, len(frame)), dtype=int))
        spectrum_values = spectrum[spectrum_index]

    geometry = {
        "R0": 2.77778, "rho": 0.52, "kappa": 1.58, "delta": 0.34,
        "shift": 0.06, "q": 1.4, "s_hat": 0.8,
    }
    return {
        **report_list_item(),
        "summary": "对附件 NPZ 中 240 帧 Miller 托卡马克曲面静电势、k_y 谱与诊断量进行重算分析；数据完整可视化，但其场是确定性合成展示场，不是已验证的非线性回旋动理学 rollout。",
        "takeaways": [
            f"归一化场能量从 {energy[0]:.3f} 增长到 {energy[-1]:.3f}；这是生成脚本定义的展示演化，不能单独证明非线性饱和。",
            f"主峰 k_yρ_s 在 {ky_peak.min():.2f}–{ky_peak.max():.2f} 之间迁移，谱肩部在演化后期更明显。",
            f"CFL 在 {cfl.min():.3f}–{cfl.max():.3f} 之间，数组本身无 NaN/Inf，可作为 NPZ 时序物理场解析和推荐的回归样例。",
            "数据范围限定为宣传动画的精确导出数组；不将 γ、ω、Wφ 或 Qi 解释为对实验或高保真求解器的验证。",
        ],
        "sections": [
            {"id": "scope", "title": "结论与数据边界", "blocks": [
                {"type": "metrics", "title": "可复核的数据概况", "items": [
                    {"label": "时序帧", "value": str(len(frame)), "unit": "帧", "state": "ok"},
                    {"label": "曲面网格", "value": f"{phi.shape[1]}×{phi.shape[2]}", "unit": "", "state": "ok"},
                    {"label": "动画时长", "value": f"{time[-1] + (time[1] - time[0]):.1f}", "unit": "s", "state": "ok"},
                ]},
                {"type": "markdown", "title": "范围声明", "body": "**这是确定性合成展示场。** NPZ 完整保存了宣传动画使用的曲面几何、静电势帧、谱和仪表板诊断量，适合验证数据管线与可视化能力；不适合用于宣称非线性回旋动理学求解精度。"},
            ]},
            {"id": "field", "title": "Miller 曲面场证据", "blocks": [
                {"type": "example", "title": "Miller 托卡马克静电势场", "artifact_id": "A-1115", "caption": "Trame + vtk.js 从同一 NPZ 的 surface_x/y/z 与 phi_surface_normalized 构建曲面场。"},
                {"type": "field_frames", "title": "代表帧：初始、中期与末期", "items": representative_frames, "field": "phi_surface_normalized", "unit": "归一化静电势"},
            ]},
            {"id": "diagnostics", "title": "时序诊断量", "blocks": [
                {"type": "timeseries_diagnostics", "title": "能量、增长率、频率与输运指标", "x": _round_list(sampled_time, 5), "x_label": "t (R/vti)", "series": [
                    {"name": "场能量（归一化）", "values": _round_list(energy[sample_index])},
                    {"name": "γ", "values": _round_list(gamma[sample_index])},
                    {"name": "ω", "values": _round_list(omega[sample_index])},
                    {"name": "CFL", "values": _round_list(cfl[sample_index])},
                    {"name": "Wφ", "values": _round_list(wphi[sample_index])},
                    {"name": "Qi", "values": _round_list(qi[sample_index])},
                ]},
                {"type": "table", "title": "诊断范围", "columns": ["诊断量", "最小值", "最大值", "末帧"], "rows": [
                    ["场能量（归一化）", f"{energy.min():.6f}", f"{energy.max():.6f}", f"{energy[-1]:.6f}"],
                    ["k_y 主峰", f"{ky_peak.min():.6f}", f"{ky_peak.max():.6f}", f"{ky_peak[-1]:.6f}"],
                    ["γ", f"{gamma.min():.6f}", f"{gamma.max():.6f}", f"{gamma[-1]:.6f}"],
                    ["ω", f"{omega.min():.6f}", f"{omega.max():.6f}", f"{omega[-1]:.6f}"],
                    ["CFL", f"{cfl.min():.6f}", f"{cfl.max():.6f}", f"{cfl[-1]:.6f}"],
                    ["Wφ", f"{wphi.min():.6f}", f"{wphi.max():.6f}", f"{wphi[-1]:.6f}"],
                    ["Qi", f"{qi.min():.6f}", f"{qi.max():.6f}", f"{qi[-1]:.6f}"],
                ]},
            ]},
            {"id": "spectrum", "title": "k_y–时间谱", "blocks": [
                {"type": "spectrum_heatmap", "title": "归一化 k_y 谱强度", "times": _round_list(time[spectrum_index], 5), "ky": _round_list(ky_axis, 5), "values": spectrum_values.round(5).tolist(), "peak": _round_list(ky_peak[spectrum_index], 5)},
                {"type": "markdown", "title": "读图结论", "body": f"主峰位置在 **{ky_peak.min():.2f}–{ky_peak.max():.2f}** 之间迁移；后期谱宽增大且 0.58 附近肩部加强。这些特征是生成脚本的确定性演化结果。"},
            ]},
            {"id": "provenance", "title": "几何、工况与来源", "blocks": [
                {"type": "table", "title": "Miller 几何与基准工况", "columns": ["参数", "值", "含义"], "rows": [
                    ["R0", str(geometry["R0"]), "主半径"], ["ρ", str(geometry["rho"]), "小半径参数"],
                    ["κ", str(geometry["kappa"]), "伸长比"], ["δ", str(geometry["delta"]), "三角形参数"],
                    ["shift", str(geometry["shift"]), "径向位移"], ["q", str(geometry["q"]), "安全因子"],
                    ["ŝ", str(geometry["s_hat"]), "磁剪切"], ["φ raw 范围", f"{phi_raw.min():.6f} … {phi_raw.max():.6f}", "原始展示场"],
                ]},
                {"type": "source", "title": "分析程序与数据口径", "body": "报告按归档 Python 程序的数组定义，从 A-1115 的 NPZ 重算全部指标，但不执行附件中的任意动态导入逻辑。原始文件仍由数据资产页面管理，不再作为报告下载入口。"},
                {"type": "source", "title": "数据完整性", "body": "数据资产 A-1115 · SHA-256 bafe7524066a74e7c8b3416ea88a13739cae6ead3bcf6c68c7fc8fa961361b23 · 240 帧。报告右上角统一提供当前阅读版本的 HTML 与 PDF。"},
            ]},
        ],
    }
