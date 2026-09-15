"""Canonical data-semantics and visualization-method catalog.

A data semantic type answers "what is this data?" and exposes one or more
concrete visualization methods that answer "how can it be shown?". Every
method owns a default configuration, accepted formats, renderer and one
openable example.
"""

from __future__ import annotations

from collections import Counter


REVISION = "visual-report-engine-v2.2026-08-25-method-catalog"


FAMILIES = [
    {"id": "PLT", "label": "分析图表", "description": "比较、趋势、分布、不确定性与优化结果"},
    {"id": "FLD", "label": "场与体数据", "description": "规则栅格、三维体素或空间拓扑上的物理量"},
    {"id": "ENT", "label": "实体与关系", "description": "点集、轨迹以及节点—边关系"},
    {"id": "GEO", "label": "几何与网格", "description": "几何表面、边界与计算网格拓扑"},
    {"id": "ASSET", "label": "报告资产", "description": "Markdown、静态图像与视频结果"},
]


def _kind(kind_id: str, family: str, label: str, definition: str, method_ids: list[str], *, glyph: str, reference_example_ids: list[str] | None = None) -> dict:
    return {
        "id": kind_id, "family": family, "label": label, "definition": definition,
        "method_ids": method_ids, "default_function": method_ids[0], "glyph": glyph,
        "reference_example_ids": reference_example_ids or [],
    }


KINDS = [
    _kind("scalar", "PLT", "标量", "单个工程数值、目标比例或离散状态。", ["core.scalar-number@2.0.0", "chart.echarts-scalar@2.1.0"], glyph="scalar"),
    _kind("table", "PLT", "表格", "共享字段结构的记录集合。", ["table.perspective@2.0.0"], glyph="table", reference_example_ids=["A-1024", "A-1032"]),
    _kind("series", "PLT", "序列", "按时间、step 或有序坐标排列的数据。", ["chart.echarts-series@2.1.0"], glyph="series", reference_example_ids=["A-1025"]),
    _kind("distribution", "PLT", "分布", "原始样本或频数数据，关注集中、离散与长尾。", ["chart.echarts-distribution@2.1.0"], glyph="distribution"),
    _kind("ensemble", "PLT", "集合", "同一坐标系中的多个模型或样本成员。", ["chart.echarts-ensemble@2.1.0"], glyph="ensemble"),
    _kind("uncertainty", "PLT", "不确定性", "估计值及误差、区间或校准信息。", ["chart.echarts-uncertainty@2.1.0"], glyph="uncertainty"),
    _kind("matrix", "PLT", "矩阵", "带行列标签的二维数值矩阵。", ["chart.echarts-matrix@2.1.0"], glyph="matrix"),
    _kind("tensor", "PLT", "张量", "带命名轴或分量的多维数组。", ["chart.echarts-tensor@2.1.0"], glyph="tensor", reference_example_ids=["A-1026"]),
    _kind("optimization", "PLT", "优化", "包含候选方案、目标、约束与迭代的优化研究。", ["chart.echarts-optimization@2.1.0"], glyph="optimization"),
    _kind("raster", "FLD", "栅格场", "二维规则网格上的标量或矢量物理量。", ["scientific.raster-scalar@2.1.0", "scientific.raster-vector@2.1.0"], glyph="raster"),
    _kind("volume", "FLD", "体数据", "三维体素网格上的标量或矢量物理量。", ["scientific.volume-scalar@2.1.0", "scientific.volume-vector@2.1.0"], glyph="volume", reference_example_ids=["A-1028"]),
    _kind("field", "FLD", "物理场", "附着在规则或非规则空间拓扑上的标量或矢量场。", ["scientific.field-scalar@2.1.0", "scientific.field-vector@2.1.0"], glyph="field", reference_example_ids=["A-1108"]),
    _kind("point_set", "ENT", "点集", "带属性但没有连续时间关系的空间采样点。", ["scientific.points@2.0.0"], glyph="points"),
    _kind("trajectory", "ENT", "轨迹", "实体或粒子按时间、step 排列的空间路径。", ["scientific.trajectory@2.0.0"], glyph="trajectory", reference_example_ids=["A-1029"]),
    _kind("graph", "ENT", "关系图", "由节点与边组成的关系、依赖或流向结构。", ["chart.echarts-graph@2.1.0"], glyph="graph"),
    _kind("mesh", "GEO", "几何网格", "线、表面、实体边界或多部件装配几何。", ["scientific.mesh@2.0.0"], glyph="mesh", reference_example_ids=["A-1027", "A-1031", "A-1033", "A-1114"]),
    _kind("text_document", "ASSET", "文本文档", "报告说明、方法、结论和注释。", ["core.markdown@2.0.0"], glyph="document"),
    _kind("image", "ASSET", "静态图像", "可直接阅读或嵌入报告的图片。", ["media.image@2.0.0"], glyph="image"),
    _kind("video", "ASSET", "视频", "结果演化或实验过程回放。", ["media.video@2.0.0"], glyph="video"),
]


def _fn(fid: str, family: str, kind: str, label: str, description: str, renderer: str, accepted_formats: list[str], example_id: str, *, offline: bool = True) -> dict:
    function_id, version = fid.split("@", 1)
    return {
        "id": fid, "function_id": function_id, "version": version, "family": family,
        "label": label, "description": description, "compatible_kinds": [kind],
        "renderer": renderer, "accepted_formats": accepted_formats, "example_id": example_id,
        "status": "available", "capabilities": {"interactive": True, "static": True, "offline": offline},
    }


FUNCTIONS = [
    _fn("core.scalar-number@2.0.0", "PLT", "scalar", "数值指标", "直接显示一个关键值、单位和目标差异。", "react", ["JSON", "CSV", "TSV", "Parquet"], "CASE-SCALAR-NUMBER"),
    _fn("chart.echarts-scalar@2.1.0", "PLT", "scalar", "标量柱状图", "用单柱、目标线和标签比较当前值与基准。", "echarts-svg", ["JSON", "CSV", "TSV", "Parquet"], "CASE-SCALAR-BAR"),
    _fn("table.perspective@2.0.0", "PLT", "table", "交互数据表", "虚拟化浏览、筛选、排序和透视结构化记录。", "perspective", ["CSV", "TSV", "JSON", "Parquet", "Arrow"], "CASE-TABLE"),
    _fn("chart.echarts-series@2.1.0", "PLT", "series", "序列趋势图", "比较时间、步数或坐标上的连续变化。", "echarts-svg", ["CSV", "TSV", "JSON", "Parquet"], "CASE-SERIES"),
    _fn("chart.echarts-distribution@2.1.0", "PLT", "distribution", "分布图", "显示直方分布、集中区间与长尾。", "echarts-svg", ["CSV", "JSON", "Parquet", "NPZ", "NPY"], "CASE-DISTRIBUTION"),
    _fn("chart.echarts-ensemble@2.1.0", "PLT", "ensemble", "集合带状图", "同时显示集合成员、均值和范围带。", "echarts-svg", ["CSV", "JSON", "NPZ", "NetCDF"], "CASE-ENSEMBLE"),
    _fn("chart.echarts-uncertainty@2.1.0", "PLT", "uncertainty", "不确定性区间图", "显示估计值、上下界与置信水平。", "echarts-svg", ["CSV", "JSON", "NPZ"], "CASE-UNCERTAINTY"),
    _fn("chart.echarts-matrix@2.1.0", "PLT", "matrix", "矩阵热力图", "用有序色阶读取二维矩阵结构。", "echarts-svg", ["CSV", "JSON", "NPZ", "NPY"], "CASE-MATRIX"),
    _fn("chart.echarts-tensor@2.1.0", "PLT", "tensor", "张量切片图", "选择分量和切片读取多维张量。", "echarts-svg", ["NPZ", "NPY", "HDF5", "NetCDF"], "CASE-TENSOR"),
    _fn("chart.echarts-optimization@2.1.0", "PLT", "optimization", "优化候选图", "比较目标、约束和 Pareto 候选。", "echarts-svg", ["CSV", "JSON", "Parquet"], "CASE-OPTIMIZATION"),
    _fn("scientific.raster-scalar@2.1.0", "FLD", "raster", "二维标量栅格", "用色图和等值线显示二维标量场。", "trame-vtkjs", ["NPZ", "NPY", "VTI", "TIFF", "NetCDF"], "CASE-RASTER-SCALAR", offline=False),
    _fn("scientific.raster-vector@2.1.0", "FLD", "raster", "二维矢量栅格", "用箭头、流线和幅值着色显示二维速度场。", "trame-vtkjs", ["NPZ", "NPY", "VTI", "NetCDF"], "CASE-RASTER-VECTOR", offline=False),
    _fn("scientific.volume-scalar@2.1.0", "FLD", "volume", "三维标量体", "用体渲染、等值面和正交切片显示温度或压力。", "trame-vtkjs", ["VTI", "NRRD", "NIfTI", "NPZ", "NetCDF"], "CASE-VOLUME-SCALAR", offline=False),
    _fn("scientific.volume-vector@2.1.0", "FLD", "volume", "三维矢量体", "用流线、箭头和幅值切片显示三维速度场。", "trame-vtkjs", ["VTI", "NPZ", "NetCDF"], "CASE-VOLUME-VECTOR", offline=False),
    _fn("scientific.field-scalar@2.1.0", "FLD", "field", "拓扑标量场", "在曲面或非规则网格上显示压力、温度、势场等标量。", "trame-vtkjs", ["VTU", "VTS", "VTM", "VTK", "CGNS", "NPZ"], "CASE-FIELD-SCALAR", offline=False),
    _fn("scientific.field-vector@2.1.0", "FLD", "field", "拓扑矢量场", "在空间拓扑上显示速度矢量、流线与幅值。", "trame-vtkjs", ["VTU", "VTS", "VTM", "VTK", "CGNS", "NPZ"], "CASE-FIELD-VECTOR", offline=False),
    _fn("scientific.points@2.0.0", "ENT", "point_set", "三维点集", "按属性着色和缩放空间采样点。", "trame-vtkjs", ["CSV", "Parquet", "PLY", "VTU"], "CASE-POINT-SET", offline=False),
    _fn("scientific.trajectory@2.0.0", "ENT", "trajectory", "三维轨迹", "播放实体路径并按物理量着色。", "trame-vtkjs", ["CSV", "Parquet", "JSON", "VTU"], "CASE-TRAJECTORY", offline=False),
    _fn("chart.echarts-graph@2.1.0", "ENT", "graph", "关系图", "显示节点、边、方向和依赖层级。", "echarts-svg", ["JSON", "CSV", "GraphML"], "CASE-GRAPH"),
    _fn("scientific.mesh@2.0.0", "GEO", "mesh", "三维几何查看", "旋转、缩放并检查几何表面、边线和装配部件。", "o3dv", ["STL", "PLY", "OBJ", "GLB", "VTU→GLB", "VTS→GLB", "VTM→GLB"], "CASE-MESH"),
    _fn("core.markdown@2.0.0", "ASSET", "text_document", "文档阅读", "安全渲染结构化文本和 Markdown。", "browser-native", ["Markdown", "TXT"], "CASE-TEXT-DOCUMENT"),
    _fn("media.image@2.0.0", "ASSET", "image", "图像查看", "显示原始图片、说明和替代文本。", "browser-native", ["PNG", "JPEG", "SVG", "WebP", "TIFF"], "CASE-IMAGE"),
    _fn("media.video@2.0.0", "ASSET", "video", "视频播放", "播放结果演化并保留 poster 与时间范围。", "browser-native", ["MP4/H.264", "WebM", "MOV"], "CASE-VIDEO"),
]


# Old persisted identifiers are accepted only at the storage/API boundary.
FUNCTION_ALIASES = {
    "core.kpi-card@2.0.0": "core.scalar-number@2.0.0",
    "scientific.raster@2.0.0": "scientific.raster-scalar@2.1.0",
    "scientific.volume@2.0.0": "scientific.volume-scalar@2.1.0",
    "scientific.field@2.0.0": "scientific.field-scalar@2.1.0",
    "chart.plotly-series@2.1.0": "chart.echarts-series@2.1.0",
    "chart.plotly-distribution@2.1.0": "chart.echarts-distribution@2.1.0",
    "chart.plotly-ensemble@2.1.0": "chart.echarts-ensemble@2.1.0",
    "chart.plotly-uncertainty@2.1.0": "chart.echarts-uncertainty@2.1.0",
    "chart.plotly-matrix@2.1.0": "chart.echarts-matrix@2.1.0",
    "chart.tensor-slices@2.0.0": "chart.echarts-tensor@2.1.0",
    "chart.plotly-optimization@2.1.0": "chart.echarts-optimization@2.1.0",
    "graph.react-flow@2.0.0": "chart.echarts-graph@2.1.0",
}


def canonical_function(function_id: str) -> str:
    """把历史方法标识规范为当前目录中的稳定标识。"""

    return FUNCTION_ALIASES.get(function_id, function_id)


RENDERER_BINDINGS = {
    "scientific.mesh@2.0.0": {
        "owner": "o3dv", "label": "Online3DViewer", "formats": ["STL", "PLY", "OBJ", "GLB"],
        "converted_formats": ["VTU", "VTS", "VTM"], "static_fallback": "o3dv-fixed-camera-snapshot",
    },
    **{
        method_id: {"owner": "trame-vtkjs", "label": "Trame + vtk.js"}
        for method_id in (
            "scientific.raster-scalar@2.1.0", "scientific.raster-vector@2.1.0",
            "scientific.volume-scalar@2.1.0", "scientific.volume-vector@2.1.0",
            "scientific.field-scalar@2.1.0", "scientific.field-vector@2.1.0",
        )
    },
}


_FUNCTION_BY_ID = {item["id"]: item for item in FUNCTIONS}
for _kind_item in KINDS:
    _kind_item["example_ids"] = [_FUNCTION_BY_ID[method_id]["example_id"] for method_id in _kind_item["method_ids"]]
    _kind_item["examples"] = [
        {
            "id": _FUNCTION_BY_ID[method_id]["example_id"], "name": _FUNCTION_BY_ID[method_id]["label"],
            "method_id": method_id, "case_type": "open-source-reconstruction",
            "case_type_label": "开源算例轻量重建",
        }
        for method_id in _kind_item["method_ids"]
    ]


COUNTS = {"families": len(FAMILIES), "kinds": len(KINDS), "functions": len(FUNCTIONS)}


def validate_catalog() -> None:
    """启动时校验5家族、19类型、23方法及案例绑定不变量。"""

    assert COUNTS == {"families": 5, "kinds": 19, "functions": 23}
    assert len({item["id"] for item in KINDS}) == 19
    assert len({item["id"] for item in FUNCTIONS}) == 23
    assert len({item["example_id"] for item in FUNCTIONS}) == 23
    assert all(item["accepted_formats"] and item["example_id"] for item in FUNCTIONS)
    assert all(method_id in _FUNCTION_BY_ID for item in KINDS for method_id in item["method_ids"])
    assert all(_FUNCTION_BY_ID[method_id]["compatible_kinds"] == [item["id"]] for item in KINDS for method_id in item["method_ids"])
    assert Counter(item["family"] for item in KINDS) == Counter({"PLT": 9, "FLD": 3, "ENT": 3, "GEO": 1, "ASSET": 3})
    assert RENDERER_BINDINGS["scientific.mesh@2.0.0"]["owner"] == "o3dv"


validate_catalog()


def catalog_response() -> dict:
    """返回数据家族和语义类型目录响应。"""

    return {"revision": REVISION, "counts": COUNTS, "families": FAMILIES, "kinds": KINDS, "updated_at": "2026-08-25T00:00:00+08:00"}


def function_response() -> dict:
    """返回可视化方法与渲染器绑定响应。"""

    return {
        "revision": REVISION, "counts": COUNTS, "families": FAMILIES, "kinds": KINDS,
        "functions": FUNCTIONS, "renderer_bindings": RENDERER_BINDINGS,
        "updated_at": "2026-08-25T00:00:00+08:00",
    }
