"""Deterministic, backend-backed examples for every visualization method."""

from __future__ import annotations

import csv
import math
import os
import random
import urllib.parse
from datetime import datetime, timezone

from .catalog import FUNCTIONS, canonical_function
from .parameterRegistry import parameter_contract
from infrastructure.config import REPOSITORY_ROOT


DATA_DIR = str(REPOSITORY_ROOT / "resources" / "examples")
API_BASE = "http://127.0.0.1:8091"
TRAME_BASE = "http://127.0.0.1:8090"
TRAME_SECRET = os.environ.get("QODER_TRAME_SECRET", "wslink-secret")

# The data semantic type selects the eligible methods; the method owns the
# concrete renderer scene.  Keeping this mapping at method level prevents a
# scalar and vector method for the same kind from accidentally sharing a view.
TRAME_VIEW_BY_METHOD = {
    "scientific.raster-scalar@2.1.0": "raster",
    "scientific.raster-vector@2.1.0": "raster_vector",
    "scientific.volume-scalar@2.1.0": "volume",
    "scientific.volume-vector@2.1.0": "volume_vector",
    "scientific.field-scalar@2.1.0": "field",
    "scientific.field-vector@2.1.0": "field_vector",
    "scientific.points@2.0.0": "points",
    "scientific.trajectory@2.0.0": "trajectory",
}


def _trame_url(view: str) -> str:
    query = urllib.parse.urlencode({"sessionURL": "ws://127.0.0.1:8090/ws", "secret": TRAME_SECRET, "view": view})
    return f"{TRAME_BASE}/?{query}"


def _case(
    artifact_id: str,
    name: str,
    family: str,
    kind: str,
    function_id: str,
    renderer: str,
    *,
    fmt: str,
    description: str,
    takeaway: str,
    source_note: str = "AI4E VizReport 确定性工程样例 · 2026-08-25",
    source_url: str | None = None,
    file_name: str | None = None,
    linked: list[str] | None = None,
    validation: str = "passed",
    model_artifact_id: str | None = None,
) -> dict:
    case_type = "negative-validation" if validation == "blocked" else "file-fixture" if file_name else "open-source-reconstruction" if source_url else "generated-demo"
    case_type_label = {
        "negative-validation": "负面校验案例",
        "file-fixture": "文件型工程案例",
        "open-source-reconstruction": "开源算例轻量重建",
        "generated-demo": "确定性生成演示",
    }[case_type]
    return {
        "id": artifact_id, "name": name, "family": family, "kind": kind,
        "function_id": canonical_function(function_id), "renderer": renderer, "format": fmt,
        "file_name": file_name, "description": description, "takeaway": takeaway,
        "source_note": source_note, "source_url": source_url,
        "updated_at": "2026-08-25T00:00:00+08:00", "linked_artifact_ids": linked or [],
        "validation": validation, "case_type": case_type, "case_type_label": case_type_label,
        "model_artifact_id": model_artifact_id,
    }


NEURALFOIL = "https://github.com/peterdsharpe/NeuralFoil"
CFDBENCH = "https://github.com/luo-yining/CFDBench"
PHYSICSNEMO = "https://github.com/NVIDIA/physicsnemo"


# Each registered method has exactly one method-level case. Scientific cases
# are small deterministic reconstructions inspired by the cited open-source
# benchmark, so the application never needs network access at runtime.
METHOD_CASES = {
    "CASE-SCALAR-NUMBER": _case("CASE-SCALAR-NUMBER", "NeuralFoil 升阻比", "PLT", "scalar", "core.scalar-number@2.0.0", "react", fmt="JSON", description="NACA 2412 在指定工况下的单值升阻比。", takeaway="升阻比 67.4，适合直接读取关键值。", source_note="基于 NeuralFoil 算例定义重建 · MIT License", source_url=NEURALFOIL),
    "CASE-SCALAR-BAR": _case("CASE-SCALAR-BAR", "NeuralFoil 升力系数达标率", "PLT", "scalar", "chart.echarts-scalar@2.1.0", "echarts-svg", fmt="JSON", description="当前升力系数相对设计目标的单柱比较。", takeaway="当前值比目标高 1.8%，柱状图强调与目标线的差异。", source_note="基于 NeuralFoil 算例定义重建 · MIT License", source_url=NEURALFOIL),
    "CASE-TABLE": _case("CASE-TABLE", "CFDBench 工况记录", "PLT", "table", "table.perspective@2.0.0", "perspective", fmt="CSV", description="圆柱绕流与管流基准的工况记录。", takeaway="表格保留几何、边界条件和雷诺数的逐行证据。", source_note="基于 CFDBench 工况定义重建 · 开源研究基准", source_url=CFDBENCH),
    "CASE-SERIES": _case("CASE-SERIES", "圆柱绕流探针压力", "PLT", "series", "chart.echarts-series@2.1.0", "echarts-svg", fmt="CSV", description="圆柱尾迹探针的周期压力序列。", takeaway="三个探针呈稳定相位差，可直接比较脱涡周期。", source_note="基于 CFDBench cylinder 算例定义重建", source_url=CFDBENCH),
    "CASE-DISTRIBUTION": _case("CASE-DISTRIBUTION", "喷流速度分布", "PLT", "distribution", "chart.echarts-distribution@2.1.0", "echarts-svg", fmt="CSV", description="喷流中心线速度样本与分箱统计。", takeaway="主体位于 285–325 m/s，右侧有高速长尾。", source_note="基于 PhysicsNeMo CFD 示例定义重建", source_url=PHYSICSNEMO),
    "CASE-ENSEMBLE": _case("CASE-ENSEMBLE", "湍流模型集合预测", "PLT", "ensemble", "chart.echarts-ensemble@2.1.0", "echarts-svg", fmt="CSV", description="十二个湍流模型成员的压降预测。", takeaway="下游成员分歧扩大，均值与范围带必须同时显示。", source_note="基于 PhysicsNeMo 外流场示例定义重建", source_url=PHYSICSNEMO),
    "CASE-UNCERTAINTY": _case("CASE-UNCERTAINTY", "翼型升力置信区间", "PLT", "uncertainty", "chart.echarts-uncertainty@2.1.0", "echarts-svg", fmt="JSON", description="攻角扫描中的均值和 95% 置信区间。", takeaway="12° 后区间显著变宽，失速区不确定性不能隐藏。", source_note="基于 NeuralFoil 翼型极曲线定义重建 · MIT License", source_url=NEURALFOIL),
    "CASE-MATRIX": _case("CASE-MATRIX", "风洞多传感器相关矩阵", "PLT", "matrix", "chart.echarts-matrix@2.1.0", "echarts-svg", fmt="JSON", description="压力、温度和振动通道的相关结构。", takeaway="P1–P3 高相关，温度与高频振动近似独立。", source_note="AI4E 风洞通道确定性演示"),
    "CASE-TENSOR": _case("CASE-TENSOR", "机翼应力张量切片", "PLT", "tensor", "chart.echarts-tensor@2.1.0", "echarts-svg", fmt="NPZ", description="带命名分量的二维应力张量切片。", takeaway="孔边出现应力集中，切片视图保留分量选择。", source_note="AI4E 结构计算确定性演示"),
    "CASE-OPTIMIZATION": _case("CASE-OPTIMIZATION", "叶型多目标优化", "PLT", "optimization", "chart.echarts-optimization@2.1.0", "echarts-svg", fmt="CSV", description="效率、压降和质量约束下的 Pareto 候选。", takeaway="D-17 位于 Pareto 膝点。", source_note="基于 NeuralFoil 翼型优化工作流重建 · MIT License", source_url=NEURALFOIL),
    "CASE-RASTER-SCALAR": _case("CASE-RASTER-SCALAR", "圆柱绕流二维压力场", "FLD", "raster", "scientific.raster-scalar@2.1.0", "trame-vtkjs", fmt="NPZ", description="二维规则网格上的压力标量。", takeaway="尾迹低压区沿中心线向下游延伸。", source_note="基于 CFDBench cylinder 算例定义重建", source_url=CFDBENCH),
    "CASE-RASTER-VECTOR": _case("CASE-RASTER-VECTOR", "圆柱绕流二维速度场", "FLD", "raster", "scientific.raster-vector@2.1.0", "trame-vtkjs", fmt="NPZ", description="u/v 两分量组成的二维速度场。", takeaway="流线和矢量揭示圆柱后方交替脱涡，单一色图无法表达方向。", source_note="基于 CFDBench u.npy / v.npy 数据约定重建", source_url=CFDBENCH),
    "CASE-VOLUME-SCALAR": _case("CASE-VOLUME-SCALAR", "外流场三维压力体", "FLD", "volume", "scientific.volume-scalar@2.1.0", "trame-vtkjs", fmt="VTI", description="三维体素网格上的压力标量。", takeaway="低压核心沿翼尖涡轴向延伸。", source_note="基于 NVIDIA PhysicsNeMo DoMINO 外气动示例定义重建", source_url=PHYSICSNEMO),
    "CASE-VOLUME-VECTOR": _case("CASE-VOLUME-VECTOR", "外流场三维速度体", "FLD", "volume", "scientific.volume-vector@2.1.0", "trame-vtkjs", fmt="VTI", description="三维体素网格上的速度矢量。", takeaway="流线显示翼尖涡的旋转方向和轴向输运。", source_note="基于 NVIDIA PhysicsNeMo external aerodynamics 示例定义重建", source_url=PHYSICSNEMO),
    "CASE-FIELD-SCALAR": _case("CASE-FIELD-SCALAR", "机翼表面压力场", "FLD", "field", "scientific.field-scalar@2.1.0", "trame-vtkjs", fmt="VTU", description="非规则表面网格上的压力系数。", takeaway="前缘上表面形成连续吸力峰。", source_note="基于 NVIDIA PhysicsNeMo XAeroNet 示例定义重建", source_url=PHYSICSNEMO),
    "CASE-FIELD-VECTOR": _case("CASE-FIELD-VECTOR", "机翼近壁速度场", "FLD", "field", "scientific.field-vector@2.1.0", "trame-vtkjs", fmt="VTU", description="非规则网格上的三分量速度。", takeaway="矢量方向揭示翼根附近的横向流动。", source_note="基于 NVIDIA PhysicsNeMo 外气动示例定义重建", source_url=PHYSICSNEMO),
    "CASE-POINT-SET": _case("CASE-POINT-SET", "喷口粒子瞬时点集", "ENT", "point_set", "scientific.points@2.0.0", "trame-vtkjs", fmt="Parquet", description="单帧粒子位置、温度与粒径。", takeaway="高温粒子集中在喷口轴线。", source_note="基于 PhysicsNeMo 流体示例定义重建", source_url=PHYSICSNEMO),
    "CASE-TRAJECTORY": _case("CASE-TRAJECTORY", "羽流粒子轨迹", "ENT", "trajectory", "scientific.trajectory@2.0.0", "trame-vtkjs", fmt="Parquet", description="粒子随时间的三维路径。", takeaway="轨迹显示羽流扩散和速度衰减。", source_note="AI4E 羽流确定性演示"),
    "CASE-GRAPH": _case("CASE-GRAPH", "CFD 仿真任务依赖图", "ENT", "graph", "chart.echarts-graph@2.1.0", "echarts-svg", fmt="JSON", description="网格、求解、后处理和报告装配的依赖。", takeaway="场结果是两个下游任务的共同依赖。", source_note="AI4E 工作流确定性演示"),
    "CASE-MESH": _case("CASE-MESH", "涡轮叶片几何网格", "GEO", "mesh", "scientific.mesh@2.0.0", "o3dv", fmt="VTU→GLB", description="从 VTU 提取纯几何表面并转换为 GLB。", takeaway="几何由 O3DV 独立显示，不混入物理场着色。", source_note="AI4E 涡轮叶片文件型案例", model_artifact_id="A-1027"),
    "CASE-TEXT-DOCUMENT": _case("CASE-TEXT-DOCUMENT", "风洞—CFD 对比方法", "ASSET", "text_document", "core.markdown@2.0.0", "browser-native", fmt="Markdown", description="可安全清洗并嵌入报告的方法说明。", takeaway="方法、假设和网格无关性结论保持可复制文本。"),
    "CASE-IMAGE": _case("CASE-IMAGE", "温度场固定视角快照", "ASSET", "image", "media.image@2.0.0", "browser-native", fmt="PNG", description="报告用固定相机静态图像。", takeaway="快照保留色标、单位、标题和来源。"),
    "CASE-VIDEO": _case("CASE-VIDEO", "羽流演化无声回放", "ASSET", "video", "media.video@2.0.0", "browser-native", fmt="MP4/H.264", description="规范化无声结果回放。", takeaway="回放展示羽流核心长度随时间变化。"),
}


# Existing engineering assets remain valid links and use the new method IDs.
CASES = {
    **METHOD_CASES,
    "A-1101": _case("A-1101", "推进效率关键指标", "PLT", "scalar", "chart.echarts-scalar@2.1.0", "echarts-svg", fmt="JSON", description="设计点推进效率与目标线。", takeaway="当前效率高于 90% 目标。"),
    "A-1024": _case("A-1024", "机翼表面压力分布（CFD）", "PLT", "table", "table.perspective@2.0.0", "perspective", fmt="CSV", file_name="cfd_wing_pressure_surface.csv", description="CFD 表面测点记录。", takeaway="前缘吸力峰值集中在上表面。"),
    "A-1025": _case("A-1025", "风洞皮托管压力时序", "PLT", "series", "chart.echarts-series@2.1.0", "echarts-svg", fmt="CSV", file_name="wind_tunnel_ts_pitot.csv", description="九通道风洞传感器时序。", takeaway="主振荡在多个通道同步出现。"),
    "A-1102": _case("A-1102", "喷流速度样本分布", "PLT", "distribution", "chart.echarts-distribution@2.1.0", "echarts-svg", fmt="CSV", description="喷流速度样本。", takeaway="分布存在高速长尾。"),
    "A-1103": _case("A-1103", "湍流模型集合预测", "PLT", "ensemble", "chart.echarts-ensemble@2.1.0", "echarts-svg", fmt="CSV", description="十二个湍流模型成员。", takeaway="下游成员分歧扩大。"),
    "A-1104": _case("A-1104", "升力系数置信区间", "PLT", "uncertainty", "chart.echarts-uncertainty@2.1.0", "echarts-svg", fmt="JSON", description="攻角扫描及置信区间。", takeaway="失速后区间变宽。"),
    "A-1105": _case("A-1105", "多传感器相关矩阵", "PLT", "matrix", "chart.echarts-matrix@2.1.0", "echarts-svg", fmt="JSON", description="多通道相关矩阵。", takeaway="压力通道高度相关。"),
    "A-1026": _case("A-1026", "应力张量（循环 118）", "PLT", "tensor", "chart.echarts-tensor@2.1.0", "echarts-svg", fmt="NPZ", file_name="stress_tensor_cycle118.npz", description="带命名分量的应力切片。", takeaway="孔边出现应力集中。"),
    "A-1106": _case("A-1106", "叶型多目标优化", "PLT", "optimization", "chart.echarts-optimization@2.1.0", "echarts-svg", fmt="CSV", description="叶型优化候选。", takeaway="D-17 位于 Pareto 膝点。"),
    "A-1107": _case("A-1107", "燃烧稳定性二维栅格", "FLD", "raster", "scientific.raster-scalar@2.1.0", "trame-vtkjs", fmt="NPZ", description="二维燃烧稳定性标量场。", takeaway="不稳定区形成连续带。"),
    "A-1028": _case("A-1028", "燃烧室温度体数据", "FLD", "volume", "scientific.volume-scalar@2.1.0", "trame-vtkjs", fmt="VTI", file_name="combustor_temp_volume.vti", description="温度体素。", takeaway="高温核心位于中轴。"),
    "A-1108": _case("A-1108", "涡轮叶片压力场", "FLD", "field", "scientific.field-scalar@2.1.0", "trame-vtkjs", fmt="VTU", file_name="turbine_blade_mesh.vtu", linked=["A-1027"], description="叶片表面压力场。", takeaway="吸力面中前段为低压核心。"),
    "A-1109": _case("A-1109", "喷口粒子瞬时点集", "ENT", "point_set", "scientific.points@2.0.0", "trame-vtkjs", fmt="Parquet", description="单帧粒子点集。", takeaway="高温粒子集中在轴线。"),
    "A-1029": _case("A-1029", "羽流粒子轨迹", "ENT", "trajectory", "scientific.trajectory@2.0.0", "trame-vtkjs", fmt="Parquet", file_name="particle_traj_plume.parquet", description="粒子轨迹。", takeaway="羽流扩散且速度衰减。"),
    "A-1110": _case("A-1110", "仿真任务依赖图", "ENT", "graph", "chart.echarts-graph@2.1.0", "echarts-svg", fmt="JSON", description="仿真工作流 DAG。", takeaway="场结果是关键依赖。"),
    "A-1027": _case("A-1027", "涡轮叶片几何网格", "GEO", "mesh", "scientific.mesh@2.0.0", "o3dv", fmt="VTU→GLB", file_name="turbine_blade_mesh.vtu", linked=["A-1108"], description="纯几何表面。", takeaway="GEO 只表达几何与拓扑。"),
    "A-1031": _case("A-1031", "机翼表面几何（PLY）", "GEO", "mesh", "scientific.mesh@2.0.0", "o3dv", fmt="PLY", file_name="wing_surface_geometry.ply", description="机翼三角网格。", takeaway="表面连续且法线一致。"),
    "A-1033": _case("A-1033", "拉瓦尔喷管几何（OBJ）", "GEO", "mesh", "scientific.mesh@2.0.0", "o3dv", fmt="OBJ", file_name="nozzle_geometry.obj", description="喷管边界几何。", takeaway="收缩段与扩张段清晰。"),
    "A-1114": _case("A-1114", "聚变站几何", "GEO", "mesh", "scientific.mesh@2.0.0", "o3dv", fmt="GLB", file_name="fusion_station_geometry.glb", description="聚变站多部件装配。", takeaway="可检查 140 个几何体。"),
    "A-1111": _case("A-1111", "仿真方法说明", "ASSET", "text_document", "core.markdown@2.0.0", "browser-native", fmt="Markdown", description="方法说明。", takeaway="文本可复制。"),
    "A-1112": _case("A-1112", "温度场固定视角快照", "ASSET", "image", "media.image@2.0.0", "browser-native", fmt="PNG", description="静态快照。", takeaway="保留色标和单位。"),
    "A-1113": _case("A-1113", "羽流演化无声回放", "ASSET", "video", "media.video@2.0.0", "browser-native", fmt="MP4/H.264", description="无声结果回放。", takeaway="展示羽流核心变化。"),
    "A-1030": _case("A-1030", "加热板表面（错误声明为场）", "FLD", "field", "scientific.field-scalar@2.1.0", "trame-vtkjs", fmt="STL", file_name="heater_plate_field.stl", description="STL 不含场变量。", takeaway="应改为 GEO/mesh 或补充场数据。", validation="blocked"),
}


def _round(value: float, digits: int = 3) -> float:
    return round(float(value), digits)


def _series_payload() -> dict:
    xs = [_round(i * 0.025) for i in range(41)]
    series = []
    for channel, phase, offset in (("P1", 0.0, 0.0), ("P2", 0.45, -0.7), ("P3", 0.9, -0.3)):
        series.append({"name": channel, "values": [_round(112 + offset + 5.8 * math.sin(2 * math.pi * 3.8 * x + phase), 2) for x in xs]})
    return {"x": xs, "x_label": "时间 (s)", "y_label": "压力 (kPa)", "series": series}


def _distribution_payload() -> dict:
    rng = random.Random(1102)
    values = [rng.gauss(302, 13) for _ in range(180)] + [rng.gauss(337, 8) for _ in range(25)]
    bins = list(range(250, 371, 10))
    return {"bins": bins, "counts": [sum(1 for value in values if bins[i] <= value < bins[i + 1]) for i in range(len(bins) - 1)], "sample_size": len(values), "unit": "m/s"}


def _ensemble_payload() -> dict:
    xs = [_round(i / 20, 2) for i in range(21)]
    members = [[_round(0.25 + 0.8 * x + 0.08 * math.sin(x * 5 + member) + member * 0.006 * x * x) for x in xs] for member in range(12)]
    return {"x": xs, "members": members, "mean": [_round(sum(row[i] for row in members) / len(members)) for i in range(len(xs))], "lower": [min(row[i] for row in members) for i in range(len(xs))], "upper": [max(row[i] for row in members) for i in range(len(xs))], "unit": "Δp / q"}


def _uncertainty_payload() -> dict:
    angle = list(range(-4, 17, 2))
    mean = [_round(0.12 + 0.095 * a - max(0, a - 12) ** 2 * 0.025) for a in angle]
    width = [_round(0.035 + max(0, a - 10) * 0.014) for a in angle]
    return {"x": angle, "mean": mean, "lower": [_round(m - w) for m, w in zip(mean, width)], "upper": [_round(m + w) for m, w in zip(mean, width)], "confidence": 0.95}


def _matrix_payload() -> dict:
    labels = ["P1", "P2", "P3", "P4", "T1", "Vx"]
    matrix = [[1.00, 0.94, 0.91, 0.62, 0.18, 0.31], [0.94, 1.00, 0.93, 0.59, 0.14, 0.29], [0.91, 0.93, 1.00, 0.57, 0.16, 0.34], [0.62, 0.59, 0.57, 1.00, 0.23, 0.44], [0.18, 0.14, 0.16, 0.23, 1.00, 0.08], [0.31, 0.29, 0.34, 0.44, 0.08, 1.00]]
    return {"labels": labels, "matrix": matrix, "range": [-1, 1]}


def _heatmap(rows: int, cols: int, seed: int, mode: str = "field") -> dict:
    rng = random.Random(seed)
    values = []
    vectors = []
    for y in range(rows):
        row, vector_row = [], []
        for x in range(cols):
            xn, yn = x / max(1, cols - 1), y / max(1, rows - 1)
            if mode == "tensor":
                value = 240 + 310 * math.exp(-((xn - 0.48) ** 2 + (yn - 0.52) ** 2) / 0.025)
            else:
                value = -1.6 * math.exp(-((xn - 0.28) ** 2 + (yn - 0.52) ** 2) / 0.04) + 1.2 * math.exp(-((xn - 0.82) ** 2 + (yn - 0.5) ** 2) / 0.08)
            u, v = 1 - 0.75 * math.exp(-((xn - 0.45) ** 2 + (yn - 0.5) ** 2) / 0.035), 0.42 * math.sin(2 * math.pi * xn) * math.exp(-((yn - 0.5) ** 2) / 0.12)
            row.append(_round(value + rng.uniform(-0.02, 0.02)))
            vector_row.append([_round(u), _round(v), 0.0])
        values.append(row); vectors.append(vector_row)
    return {"values": values, "vectors": vectors, "rows": rows, "cols": cols}


def _optimization_payload() -> dict:
    points = []
    for index in range(28):
        points.append({"id": f"D-{index + 1:02d}", "efficiency": _round(0.78 + 0.18 * index / 27 + 0.012 * math.sin(index * 1.7)), "loss": _round(0.18 - 0.11 * index / 27 + 0.01 * math.cos(index * 1.2)), "pareto": index in {12, 16, 20, 24, 27}})
    return {"points": points, "recommended": "D-17"}


def _table_payload() -> dict:
    path = os.path.join(DATA_DIR, "cfd_wing_pressure_surface.csv")
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as handle:
            rows = []
            for index, row in enumerate(csv.DictReader(handle)):
                rows.append({key: row[key] for key in list(row)[:8]})
                if index >= 39: break
            return {"columns": list(rows[0]) if rows else [], "rows": rows, "total_rows": 150000}
    rows = [{"case": "cylinder", "re": 100 + index * 20, "inlet_u": _round(0.8 + index * 0.04), "grid": f"{128 + index * 8}×64"} for index in range(20)]
    return {"columns": list(rows[0]), "rows": rows, "total_rows": len(rows)}


def _points_payload() -> dict:
    rng = random.Random(1109)
    points = []
    for index in range(220):
        x = rng.random() * 2.2; spread = 0.08 + 0.18 * x
        points.append({"id": index, "x": _round(x), "y": _round(rng.gauss(0, spread)), "z": _round(rng.gauss(0, spread)), "temperature": _round(1200 - 280 * x + rng.gauss(0, 35), 1)})
    return {"points": points, "unit": "m"}


def _trajectory_payload() -> dict:
    return {"tracks": [[[_round(step / 12), _round((track - 6.5) * 0.018 * (1 + step / 12) + 0.02 * math.sin(step * 0.5 + track)), _round(520 - step * 9 - track * 2, 1)] for step in range(24)] for track in range(14)], "dimensions": ["x", "y", "velocity"]}


def _graph_payload() -> dict:
    return {"nodes": [{"id": "mesh", "label": "网格生成", "stage": 0}, {"id": "solver", "label": "流场求解", "stage": 1}, {"id": "field", "label": "场结果", "stage": 2}, {"id": "stats", "label": "统计摘要", "stage": 2}, {"id": "viz", "label": "可视化", "stage": 3}, {"id": "report", "label": "报告装配", "stage": 4}], "links": [["mesh", "solver"], ["solver", "field"], ["solver", "stats"], ["field", "viz"], ["stats", "viz"], ["viz", "report"]]}


def example_payload(artifact_id: str, api_base: str = API_BASE) -> dict:
    """生成指定确定性案例的前端可视化载荷。"""

    case = CASES[artifact_id]
    kind, method_id = case["kind"], case["function_id"]
    api_base = api_base.rstrip("/")
    if method_id == "core.scalar-number@2.0.0":
        data = {"value": 67.4, "unit": "L/D", "target": 65.0, "delta": 2.4, "status": "above-target"}
    elif kind == "scalar":
        data = {"value": 91.8, "unit": "%", "target": 90.0, "delta": 1.8, "status": "above-target"}
    elif kind == "table": data = _table_payload()
    elif kind == "series": data = _series_payload()
    elif kind == "distribution": data = _distribution_payload()
    elif kind == "ensemble": data = _ensemble_payload()
    elif kind == "uncertainty": data = _uncertainty_payload()
    elif kind == "matrix": data = _matrix_payload()
    elif kind == "tensor": data = _heatmap(18, 26, 1026, "tensor") | {"channels": ["σxx", "σxy", "σyy"], "unit": "MPa"}
    elif kind == "optimization": data = _optimization_payload()
    elif kind == "raster": data = _heatmap(22, 36, 1107) | {"unit": "m/s" if method_id.endswith("vector@2.1.0") else "Cp", "field_role": "vector" if method_id.endswith("vector@2.1.0") else "scalar"}
    elif kind in {"volume", "field"}: data = _heatmap(20, 32, 1028 if kind == "volume" else 1108) | {"unit": "m/s" if method_id.endswith("vector@2.1.0") else "Pa", "field_role": "vector" if method_id.endswith("vector@2.1.0") else "scalar"}
    elif kind == "point_set": data = _points_payload()
    elif kind == "trajectory": data = _trajectory_payload()
    elif kind == "graph": data = _graph_payload()
    elif kind == "text_document": data = {"markdown": "# 风洞—CFD 对比方法\n\n采用相同攻角、马赫数与参考压力。CFD 结果按测压孔位置插值，报告保留原始单位与缺测标记。\n\n## 网格无关性\n\n中等网格与精细网格的升力系数差异为 **0.7%**。"}
    elif kind == "image": data = {"url": f"{api_base}/api/example-assets/A-1112", "alt": "固定视角温度场快照，高温核心位于中轴。"}
    elif kind == "video": data = {"url": f"{api_base}/api/example-assets/A-1113", "poster_url": f"{api_base}/api/example-assets/A-1112", "duration_s": 4.0, "silent": True}
    elif kind == "mesh":
        model_id = case.get("model_artifact_id") or artifact_id
        model_case = CASES.get(model_id, case)
        data = {"model_url": f"{api_base}/api/artifact/{model_id}/file/{model_case['file_name']}"} if model_case["format"] in {"PLY", "OBJ"} else {"model_url": f"{api_base}/api/artifact/{model_id}/representation/o3dv.glb"}
    else: data = {}

    if case["renderer"] == "trame-vtkjs":
        view = TRAME_VIEW_BY_METHOD[method_id]
        render = {"owner": "trame-vtkjs", "label": "Trame + vtk.js", "mode": "iframe", "url": _trame_url(view)}
    elif case["renderer"] == "o3dv": render = {"owner": "o3dv", "mode": "model", "url": data.get("model_url"), "fallback_url": f"{api_base}/api/example-assets/A-1027-snapshot"}
    elif case["renderer"] == "browser-native": render = {"owner": "browser-native", "mode": kind}
    else: render = {"owner": case["renderer"], "mode": "inline"}
    function = next(item for item in FUNCTIONS if item["id"] == method_id)
    defaults = parameter_contract(function)["default_parameters"]
    return {
        "artifact": case,
        "resolved_spec": {"function_id": method_id, "kind": kind, "params": defaults, "frozen_at": datetime.now(timezone.utc).isoformat()},
        "renderer": render, "data": data,
        "connection": {"state": "live", "updated_at": case["updated_at"]},
    }


assert {item["example_id"] for item in FUNCTIONS} == set(METHOD_CASES)
