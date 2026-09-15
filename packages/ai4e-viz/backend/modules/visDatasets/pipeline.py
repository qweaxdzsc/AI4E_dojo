"""数据集文件解析、画像、检测和可视化推荐的数据处理管线。

本文件属于 visDatasets 一级模块：它读取已登记文件并产生画像、质量诊断及推荐输入，
不注册 Router、不创建 Server。公开 HTTP 适配位于本模块 api.py；跨模块协作只使用目标
模块公开门面。重型 VTK 依赖保持延迟导入，避免普通表格接口启动时加载图形运行时。
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import urllib.parse
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import HTTPException

from infrastructure.config import REPOSITORY_ROOT, runtime_paths
from modules.reportManage.gradShafranovReport import ROOT as GS_ROOT
from modules.visConvertor import convert_to_glb
from modules.visIO import latest_visualization
from modules.visTaskManage.catalog import FUNCTIONS, KINDS, canonical_function
from modules.visTaskManage.examples import CASES
from modules.visTaskManage.parameterRegistry import enrich_recommendations, normalize_and_validate

from modules.dataAssets import (
    get_artifact, list_artifacts as stored_artifacts, save_analysis,
    save_analysis_error, upsert_artifact,
)


DATA_DIR = str(REPOSITORY_ROOT / "resources" / "examples")
UPLOAD_DIR = str(runtime_paths().objects / "datasets")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 可解析文件型Artifact；其余十九类案例由visTaskManage.examples提供确定性payload。
REGISTRY = {
    "A-1024": {"file": "cfd_wing_pressure_surface.csv", "format": "CSV", "declared_kind": "table", "name": "机翼表面压力分布（CFD）"},
    "A-1025": {"file": "wind_tunnel_ts_pitot.csv", "format": "CSV", "declared_kind": "timeseries", "name": "风洞皮托管压力时序"},
    "A-1026": {"file": "stress_tensor_cycle118.npz", "format": "NPZ", "declared_kind": "tensor", "name": "应力张量（循环 118）"},
    "A-1027": {"file": "turbine_blade_mesh.vtu", "format": "VTU", "declared_kind": "mesh", "name": "涡轮叶片几何网格"},
    "A-1108": {"file": "turbine_blade_mesh.vtu", "format": "VTU", "declared_kind": "field", "name": "涡轮叶片压力场"},
    "A-1028": {"file": "combustor_temp_volume.vti", "format": "VTI", "declared_kind": "volume", "name": "燃烧室温度体数据"},
    "A-1029": {"file": "particle_traj_plume.parquet", "format": "Parquet", "declared_kind": "trajectory", "name": "羽流粒子轨迹"},
    "A-1030": {"file": "heater_plate_field.stl", "format": "STL", "declared_kind": "field", "name": "加热板表面（声明为场）"},
    "A-1031": {"file": "wing_surface_geometry.ply", "format": "PLY", "declared_kind": "mesh", "name": "机翼表面几何（PLY）"},
    "A-1032": {"file": "simulation_log_raw.csv", "format": "CSV", "declared_kind": "table", "name": "仿真运行日志（未整理）"},
    "A-1033": {"file": "nozzle_geometry.obj", "format": "OBJ", "declared_kind": "mesh", "name": "拉瓦尔喷管几何（OBJ）"},
    "A-1114": {"file": "fusion_station_geometry.glb", "format": "GLB", "declared_kind": "mesh", "name": "聚变站几何"},
    "A-1115": {"file": "miller_tokamak_timeseries_240frames.npz", "format": "NPZ", "declared_kind": "field", "name": "Miller 托卡马克静电势时序场"},
}
# 可视化引擎/图表映射（供推荐与前端跳转）
API_BASE = "http://127.0.0.1:8091"
TRAME_BASE = os.environ.get("QODER_TRAME_BASE", "http://127.0.0.1:8090")
TRAME_PORT = urllib.parse.urlparse(TRAME_BASE).port or 8090
TRAME_SECRET = os.environ.get("QODER_TRAME_SECRET", "wslink-secret")
TRAME_VIEW = {"A-1108": "field", "A-1028": "volume", "A-1029": "trajectory", "A-1115": "miller_field"}
TRAME_SNAPSHOT_ASSET = {
    "A-1028": "A-1028-trame-snapshot",
    "A-1029": "A-1029-trame-snapshot",
    "A-1108": "A-1108-trame-snapshot",
}


def _trame_url(view: str) -> str:
    """Build a direct wslink URL; without sessionURL the client calls a missing launcher."""

    parsed = urllib.parse.urlparse(TRAME_BASE)
    websocket_scheme = "wss" if parsed.scheme == "https" else "ws"
    websocket_netloc = parsed.netloc or f"127.0.0.1:{TRAME_PORT}"
    query = urllib.parse.urlencode(
        {
            "sessionURL": f"{websocket_scheme}://{websocket_netloc}/ws",
            "secret": TRAME_SECRET,
            "view": view,
        }
    )
    return f"{TRAME_BASE}/?{query}"


# --------------------------------------------------------------- VTK lazy import
def _vtk():
    import vtk

    return vtk


# --------------------------------------------------------------- 解析器
def _col_profile(s: pd.Series) -> dict:
    prof = {"dtype": str(s.dtype), "missing": round(float(s.isna().mean()) * 100, 3), "unique": int(s.nunique())}
    if pd.api.types.is_numeric_dtype(s):
        prof.update(min=float(np.nanmin(s)), max=float(np.nanmax(s)), mean=float(np.nanmean(s)))
    return prof


def parse_csv(fp: str) -> dict:
    """解析 CSV 的列画像、时序特征、轨迹结构和数据质量信号。"""

    df = pd.read_csv(fp, low_memory=False)
    cols = list(df.columns)
    col_profiles = {c: _col_profile(df[c]) for c in cols}
    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    text_cols = [
        c for c in cols
        if not pd.api.types.is_numeric_dtype(df[c])
        and not pd.api.types.is_datetime64_any_dtype(df[c])
        and (df[c].dtype == object or pd.api.types.is_string_dtype(df[c]))
    ]
    # 自由文本列：高基数字符串（非枚举类别），是"未整理日志"的典型特征
    freetext_cols = [c for c in text_cols if col_profiles[c]["unique"] > 40]

    # 轨迹模式：particle/轨迹 id + frame + x/y/z
    lower = {c.lower(): c for c in cols}
    traj_keys = {"particle_id", "frame", "x", "y", "z"}
    is_traj = traj_keys.issubset(set(lower))
    # 时间列检测：支持数值时间、datetime dtype 和可解析的字符串时间戳。
    time_col = None
    for cand in ("time", "t", "timestamp", "datetime"):
        if cand in lower:
            c = lower[cand]
            vals = df[c].dropna()
            parsed_time = pd.to_datetime(vals.head(256), errors="coerce") if not pd.api.types.is_numeric_dtype(vals) else None
            if pd.api.types.is_numeric_dtype(vals) or pd.api.types.is_datetime64_any_dtype(vals) or (parsed_time is not None and parsed_time.notna().mean() > 0.9):
                time_col = c
                break
    n_channels = len([c for c in numeric_cols if c != time_col])

    if is_traj:
        inferred = "trajectory"
        n_traj = int(df[lower["particle_id"]].nunique())
        n_frame = int(df[lower["frame"]].nunique())
        spatial = {
            "bbox": [[float(df[a].min()), float(df[a].max())] for a in (lower["x"], lower["y"], lower["z"])],
        }
        summary = f"{n_traj} 条轨迹 × {n_frame} 帧 · {len(df):,} 行"
    elif time_col is not None and n_channels >= 2:
        inferred = "timeseries"
        spatial = None
        summary = f"{len(df):,} 采样点 × {n_channels} 通道（时间列 {time_col}）"
    else:
        inferred = "table"
        spatial = None
        summary = f"{len(df):,} 行 × {len(cols)} 列"

    # 结构化程度：无时间列且含多列自由文本 / 文本占比过高 → 未整理日志
    level_col = next((lower[key] for key in ("level", "severity", "log_level") if key in lower), None)
    is_log = level_col is not None or {"module", "message"}.issubset(lower) or {"module", "free_text"}.issubset(lower)
    level_counts = df[level_col].astype(str).value_counts().head(12).to_dict() if level_col else {}
    messy = (
        time_col is None
        and not is_traj
        and (len(freetext_cols) >= 2 or (len(text_cols) >= 3 and len(text_cols) / len(cols) >= 0.25))
    )
    large = len(df) > 100_000

    return {
        "format": "CSV",
        "inferred_kind": inferred,
        "rows": len(df),
        "columns": cols,
        "column_profiles": col_profiles,
        "numeric_columns": numeric_cols,
        "text_columns": text_cols,
        "freetext_columns": freetext_cols,
        "time_column": time_col,
        "n_channels": n_channels,
        "large": large,
        "messy": messy,
        "is_log": is_log,
        "level_column": level_col,
        "level_counts": {str(key): int(value) for key, value in level_counts.items()},
        "spatial": spatial,
        "summary": summary,
    }


def parse_npz(fp: str) -> dict:
    """解析 NPZ 数组形状、范围、有限性以及 Miller 时序场特征。"""

    with np.load(fp, allow_pickle=False) as z:
        miller_required = {
            "frame", "time_R_over_vti", "surface_x", "surface_y", "surface_z",
            "phi_surface_raw", "phi_surface_normalized",
        }
        is_miller = miller_required.issubset(z.files)
        coordinate_names = {
            "R", "Z", "x", "y", "z", "time", "theta_rad", "zeta_rad",
            "surface_x", "surface_y", "surface_z", "surface_R", "theta_cross_rad",
            "cross_R_minus_R0", "cross_Z",
        }
        time_names = {"frame", "time_R_over_vti", "phase_rad"}
        arrays = {}
        main_shape, main_name = None, None
        for k in z.files:
            a = z[k]
            role = "coordinate" if k in coordinate_names else "time" if k in time_names else "metadata" if k == "metadata_json" else "value"
            info = {"shape": list(a.shape), "dtype": str(a.dtype), "role": role}
            if np.issubdtype(a.dtype, np.number) and a.size:
                info.update(range=[float(np.nanmin(a)), float(np.nanmax(a))], nan_count=int(np.isnan(a).sum()) if np.issubdtype(a.dtype, np.floating) else 0)
            arrays[k] = info
            if role == "value" and a.ndim >= 2 and (main_shape is None or a.size > np.prod(main_shape or [0])):
                main_shape, main_name = list(a.shape), k
        is_gs = {"R", "Z", "psi", "j_phi", "pde_residual", "plasma_mask"}.issubset(z.files)
        if is_gs:
            main_name = "psi"
        elif is_miller:
            main_name = "phi_surface_normalized"
        if main_name is None:
            main_name = z.files[0]
        a = z[main_name]
        if is_miller:
            inferred = "field"
        elif is_gs or a.ndim == 2:
            inferred = "raster"
        elif a.ndim >= 3:
            inferred = "tensor"
        else:
            inferred = "table"
        metadata = {}
        if "metadata_json" in z.files:
            try:
                metadata = json.loads(str(z["metadata_json"].item()))
            except (TypeError, ValueError, json.JSONDecodeError):
                metadata = {"parse_warning": "metadata_json 不是有效 JSON"}
        field_arrays = [
            key for key, value in arrays.items()
            if value["role"] == "value"
            and (len(value["shape"]) == 2 or (is_miller and len(value["shape"]) == 3 and value["shape"][0] == int(z["frame"].size)))
        ]
        result = {
            "format": "NPZ",
            "inferred_kind": inferred,
            "arrays": arrays,
            "main_array": main_name,
            "field_arrays": field_arrays,
            "vector_arrays": [key for key in arrays if key.lower() in {"u", "v", "w", "ux", "uy", "uz", "velocity_x", "velocity_y", "velocity_z"}],
            "coordinate_arrays": [key for key, value in arrays.items() if value["role"] == "coordinate"],
            "time_arrays": [key for key, value in arrays.items() if value["role"] == "time"],
            "is_grad_shafranov": is_gs,
            "is_miller_tokamak": is_miller,
            "shape": list(a.shape),
            "ndim": int(a.ndim),
            "dtype": str(a.dtype),
            "range": [float(np.nanmin(a)), float(np.nanmax(a))],
            "mean": float(np.nanmean(a)),
            "nan_count": int(np.isnan(a).sum()) if np.issubdtype(a.dtype, np.floating) else 0,
            "units": str(z["units"]) if "units" in z.files else None,
            "metadata": metadata,
            "summary": f"{'Miller 托卡马克时序物理场' if is_miller else 'G-S 二维场' if is_gs else str(a.ndim) + ' 维数组'} {' × '.join(map(str, a.shape))} · {a.dtype}",
        }
        if is_miller:
            frames = int(z["frame"].size)
            topology_shape = list(np.asarray(z["surface_x"]).shape)
            fps = int(metadata.get("fps", 24))
            result.update({
                "temporal_field": True,
                "frames": frames,
                "fps": fps,
                "duration_seconds": float(metadata.get("duration_seconds", frames / max(fps, 1))),
                "topology_shape": topology_shape,
                "diagnostic_arrays": [
                    name for name in ("field_energy_normalized", "ky_peak_normalized", "gamma_live", "omega_live", "cfl_live", "Wphi_live", "Qi_live")
                    if name in z.files
                ],
                "solver_case": metadata.get("solver_case", {}),
                "miller_geometry": metadata.get("miller_geometry", {}),
                "scope": metadata.get("scope"),
                "summary": f"Miller 托卡马克时序标量场 · {frames} 帧 · {topology_shape[0]} × {topology_shape[1]} 曲面网格 · {metadata.get('duration_seconds', frames / max(fps, 1)):g} s",
            })
        return result


def parse_json(fp: str) -> dict:
    """解析 JSON 文档的顶层结构和记录规模。"""

    with open(fp, encoding="utf-8") as handle:
        value = json.load(handle)
    if isinstance(value, list):
        records = [item for item in value if isinstance(item, dict)]
        columns = sorted({key for item in records[:200] for key in item})
        return {"format": "JSON", "inferred_kind": "table", "rows": len(records), "columns": columns, "summary": f"JSON 记录 {len(records):,} 行 × {len(columns)} 列", "records_preview": records[:20]}
    if isinstance(value, dict):
        numeric = [key for key, item in value.items() if isinstance(item, (int, float)) and not isinstance(item, bool)]
        return {"format": "JSON", "inferred_kind": "table", "rows": len(value), "columns": list(value), "numeric_columns": numeric, "summary": f"JSON 指标对象 · {len(value)} 个顶层字段", "records_preview": [{"metric": key, "value": item if isinstance(item, (str, int, float, bool)) or item is None else json.dumps(item, ensure_ascii=False)} for key, item in list(value.items())[:80]]}
    return {"format": "JSON", "inferred_kind": "scalar", "summary": "JSON 标量", "value": value}


def parse_image(fp: str) -> dict:
    """读取图片格式、尺寸和颜色模式等预览元数据。"""

    from PIL import Image

    with Image.open(fp) as image:
        return {"format": image.format or "IMAGE", "inferred_kind": "image", "width": image.width, "height": image.height, "mode": image.mode, "summary": f"图像 {image.width} × {image.height} · {image.mode}"}


def parse_text_document(fp: str) -> dict:
    """解析 Markdown 或 HTML 文档的文本规模。"""

    raw = Path(fp).read_text(encoding="utf-8", errors="replace")
    return {"format": Path(fp).suffix.lstrip(".").upper(), "inferred_kind": "text_document", "characters": len(raw), "summary": f"文本文档 · {len(raw):,} 字符"}


def parse_checkpoint(fp: str) -> dict:
    """登记模型检查点的文件级画像，不执行不可信模型代码。"""

    return {"format": "PT", "inferred_kind": "text_document", "metadata_only": True, "blocked_reason": "模型 checkpoint 只允许 metadata-only 检查；不会执行 pickle 反序列化。", "summary": f"PyTorch checkpoint · {os.path.getsize(fp):,} bytes · 未执行反序列化"}


def parse_vti(fp: str) -> dict:
    """解析 VTI 规则体数据的维度、间距和场变量范围。"""

    vtk = _vtk()
    r = vtk.vtkXMLImageDataReader()
    r.SetFileName(fp)
    r.Update()
    img = r.GetOutput()
    dims = list(img.GetDimensions())
    sc = img.GetPointData().GetScalars()
    field_vars = []
    point_data = img.GetPointData()
    for index in range(point_data.GetNumberOfArrays()):
        array = point_data.GetArray(index)
        field_vars.append({"name": array.GetName(), "components": array.GetNumberOfComponents(), "range": [float(value) for value in array.GetRange()]})
    name = sc.GetName() if sc else None
    rng = [float(x) for x in sc.GetRange()] if sc else None
    origin = list(img.GetOrigin())
    spacing = list(img.GetSpacing())
    extent_mm = [d * s for d, s in zip(dims, spacing)]
    return {
        "format": "VTI",
        "inferred_kind": "volume",
        "dimensions": dims,
        "voxels": int(np.prod(dims)),
        "scalar_array": name,
        "field_variables": field_vars,
        "vector_arrays": [item["name"] for item in field_vars if item["components"] in {2, 3}],
        "scalar_range": rng,
        "origin": origin,
        "spacing": spacing,
        "extent_mm": extent_mm,
        "summary": f"体数据 {' × '.join(map(str, dims))} 体素 · 标量 {name} [{rng[0]:.0f}, {rng[1]:.0f}]" if rng else f"体数据 {dims}",
    }


def _parse_vtk_dataset(fp: str, kind: str) -> dict:
    vtk = _vtk()
    if kind == "VTU":
        r = vtk.vtkXMLUnstructuredGridReader()
    else:
        r = vtk.vtkXMLPolyDataReader()
    r.SetFileName(fp)
    r.Update()
    ds = r.GetOutput()
    n_pts, n_cells = ds.GetNumberOfPoints(), ds.GetNumberOfCells()
    bounds = list(ds.GetBounds())
    pd_, cd_ = ds.GetPointData(), ds.GetCellData()
    field_vars = []
    for src, loc in ((pd_, "point"), (cd_, "cell")):
        for i in range(src.GetNumberOfArrays()):
            arr = src.GetArray(i)
            field_vars.append(
                {"name": arr.GetName(), "location": loc, "components": arr.GetNumberOfComponents(), "range": [float(x) for x in arr.GetRange()]}
            )
    has_field = len(field_vars) > 0
    return {
        "format": kind,
        "inferred_kind": "field" if has_field else "mesh",
        "points": n_pts,
        "cells": n_cells,
        "bounds": bounds,
        "field_variables": field_vars,
        "has_field": has_field,
        "summary": f"网格 {n_pts:,} 点 · {n_cells:,} 单元 · {'含 ' + str(len(field_vars)) + ' 个场变量' if has_field else '无场变量（纯几何）'}",
    }


def parse_vtk_structured_or_multiblock(fp: str, kind: str) -> dict:
    """解析 VTK 结构化或多块数据集并汇总拓扑和数组信息。"""

    vtk = _vtk()
    reader = vtk.vtkXMLStructuredGridReader() if kind == "VTS" else vtk.vtkXMLMultiBlockDataReader()
    reader.SetFileName(fp)
    reader.Update()
    root = reader.GetOutputDataObject(0)
    datasets = []
    if isinstance(root, vtk.vtkDataSet):
        datasets = [root]
    else:
        iterator = root.NewIterator()
        iterator.VisitOnlyLeavesOn()
        iterator.SkipEmptyNodesOn()
        iterator.InitTraversal()
        while not iterator.IsDoneWithTraversal():
            current = iterator.GetCurrentDataObject()
            if isinstance(current, vtk.vtkDataSet):
                datasets.append(current)
            iterator.GoToNextItem()
    if not datasets:
        raise ValueError(f"{kind} 不含可解析的数据块")
    field_variables = []
    bounds = [float("inf"), float("-inf"), float("inf"), float("-inf"), float("inf"), float("-inf")]
    for dataset in datasets:
        current = dataset.GetBounds()
        for axis in range(3):
            bounds[axis * 2] = min(bounds[axis * 2], current[axis * 2])
            bounds[axis * 2 + 1] = max(bounds[axis * 2 + 1], current[axis * 2 + 1])
        for source, location in ((dataset.GetPointData(), "point"), (dataset.GetCellData(), "cell")):
            for index in range(source.GetNumberOfArrays()):
                array = source.GetArray(index)
                name = array.GetName() or f"array-{index}"
                if not any(item["name"] == name and item["location"] == location for item in field_variables):
                    field_variables.append({"name": name, "location": location, "components": array.GetNumberOfComponents(), "range": [float(value) for value in array.GetRange()]})
    points = sum(dataset.GetNumberOfPoints() for dataset in datasets)
    cells = sum(dataset.GetNumberOfCells() for dataset in datasets)
    return {"format": kind, "inferred_kind": "mesh", "points": points, "cells": cells, "blocks": len(datasets), "bounds": bounds, "field_variables": field_variables, "has_field": bool(field_variables), "summary": f"{kind} {len(datasets)} 块 · {points:,} 点 · {cells:,} 单元"}


def parse_stl(fp: str) -> dict:
    """解析 STL 几何边界并识别无物理场变量的纯几何事实。"""

    vtk = _vtk()
    r = vtk.vtkSTLReader()
    r.SetFileName(fp)
    r.Update()
    ds = r.GetOutput()
    n_pts, n_cells = ds.GetNumberOfPoints(), ds.GetNumberOfCells()
    return {
        "format": "STL",
        "inferred_kind": "mesh",
        "points": n_pts,
        "cells": n_cells,
        "bounds": list(ds.GetBounds()),
        "field_variables": [],
        "has_field": False,
        "summary": f"纯几何网格 {n_pts:,} 点 · {n_cells:,} 单元 · 无场变量",
    }


def parse_ply(fp: str) -> dict:
    """解析 PLY 点面规模、边界和可供 O3DV 消费的几何属性。"""

    vtk = _vtk()
    r = vtk.vtkPLYReader()
    r.SetFileName(fp)
    r.Update()
    ds = r.GetOutput()
    n_pts, n_cells = ds.GetNumberOfPoints(), ds.GetNumberOfCells()
    return {
        "format": "PLY",
        "inferred_kind": "mesh",
        "points": n_pts,
        "cells": n_cells,
        "bounds": list(ds.GetBounds()),
        "field_variables": [],
        "has_field": False,
        "summary": f"纯几何网格 {n_pts:,} 点 · {n_cells:,} 单元 · 无场变量",
    }


def parse_obj(fp: str) -> dict:
    """解析 OBJ 几何的顶点、面和空间边界。"""

    vtk = _vtk()
    r = vtk.vtkOBJReader()
    r.SetFileName(fp)
    r.Update()
    ds = r.GetOutput()
    n_pts, n_cells = ds.GetNumberOfPoints(), ds.GetNumberOfCells()
    return {
        "format": "OBJ",
        "inferred_kind": "mesh",
        "points": n_pts,
        "cells": n_cells,
        "bounds": list(ds.GetBounds()),
        "field_variables": [],
        "has_field": False,
        "summary": f"纯几何网格 {n_pts:,} 点 · {n_cells:,} 单元 · 无场变量",
    }


def parse_glb(fp: str) -> dict:
    """校验 GLB 文件头并返回浏览器几何表现画像。"""

    """Inspect a GLB scene without converting or executing embedded content."""
    import trimesh

    scene = trimesh.load(fp, file_type="glb", force="scene", process=False)
    geometries = list(scene.geometry.values())
    points = sum(len(geometry.vertices) for geometry in geometries if hasattr(geometry, "vertices"))
    cells = sum(len(geometry.faces) for geometry in geometries if hasattr(geometry, "faces"))
    bounds = np.asarray(scene.bounds, dtype=float)
    if bounds.shape != (2, 3):
        raise ValueError("GLB 不含有效的三维包围盒")
    flat_bounds = [
        float(bounds[0, 0]), float(bounds[1, 0]),
        float(bounds[0, 1]), float(bounds[1, 1]),
        float(bounds[0, 2]), float(bounds[1, 2]),
    ]
    return {
        "format": "GLB",
        "inferred_kind": "mesh",
        "mesh_structure": "multiblock" if len(geometries) > 1 else "surface",
        "geometries": len(geometries),
        "points": points,
        "cells": cells,
        "bounds": flat_bounds,
        "field_variables": [],
        "has_field": False,
        "summary": f"GLB 装配体 {len(geometries):,} 个几何体 · {points:,} 顶点 · {cells:,} 三角面",
    }


def parse_parquet(fp: str) -> dict:
    """解析 Parquet 表结构，并识别时序或三维轨迹语义。"""

    df = pd.read_parquet(fp)
    cols = list(df.columns)
    lower = {c.lower(): c for c in cols}
    traj_keys = {"particle_id", "frame", "x", "y", "z"}
    is_traj = traj_keys.issubset(set(lower))
    col_profiles = {c: _col_profile(df[c]) for c in cols}
    if is_traj:
        n_traj = int(df[lower["particle_id"]].nunique())
        n_frame = int(df[lower["frame"]].nunique())
        inferred = "trajectory"
        spatial = {"bbox": [[float(df[lower[a]].min()), float(df[lower[a]].max())] for a in ("x", "y", "z")]}
        summary = f"{n_traj} 条轨迹 × {n_frame} 帧 · {len(df):,} 行"
    else:
        inferred = "table"
        spatial = None
        summary = f"{len(df):,} 行 × {len(cols)} 列"
    return {
        "format": "Parquet",
        "inferred_kind": inferred,
        "rows": len(df),
        "columns": cols,
        "column_profiles": col_profiles,
        "spatial": spatial,
        "summary": summary,
    }


PARSERS = {
    "CSV": parse_csv,
    "NPZ": parse_npz,
    "VTI": parse_vti,
    "VTU": lambda fp: _parse_vtk_dataset(fp, "VTU"),
    "VTP": lambda fp: _parse_vtk_dataset(fp, "VTP"),
    "VTS": lambda fp: parse_vtk_structured_or_multiblock(fp, "VTS"),
    "VTM": lambda fp: parse_vtk_structured_or_multiblock(fp, "VTM"),
    "STL": parse_stl,
    "PLY": parse_ply,
    "OBJ": parse_obj,
    "GLB": parse_glb,
    "Parquet": parse_parquet,
    "PARQUET": parse_parquet,
    "JSON": parse_json,
    "PNG": parse_image,
    "JPEG": parse_image,
    "JPG": parse_image,
    "MD": parse_text_document,
    "MARKDOWN": parse_text_document,
    "HTML": parse_text_document,
    "PT": parse_checkpoint,
}


FAMILY_BY_KIND = {
    "scalar": "PLT", "table": "PLT", "series": "PLT", "timeseries": "PLT",
    "distribution": "PLT", "ensemble": "PLT", "uncertainty": "PLT", "matrix": "PLT",
    "tensor": "PLT", "optimization": "PLT", "raster": "FLD", "volume": "FLD",
    "field": "FLD", "point_set": "ENT", "trajectory": "ENT", "graph": "ENT",
    "mesh": "GEO", "text_document": "ASSET", "image": "ASSET", "video": "ASSET",
}

FORMAT_BY_EXTENSION = {
    "csv": "CSV", "npz": "NPZ", "json": "JSON", "vti": "VTI", "vtu": "VTU",
    "vtp": "VTP", "vts": "VTS", "vtm": "VTM", "stl": "STL", "ply": "PLY",
    "obj": "OBJ", "parquet": "Parquet", "pq": "Parquet", "png": "PNG",
    "jpg": "JPEG", "jpeg": "JPEG", "md": "MD", "markdown": "MARKDOWN",
    "html": "HTML", "htm": "HTML", "pt": "PT", "glb": "GLB",
}

_seeded_db_key = None
_digest_cache: dict[str, tuple[float, int, str]] = {}


def _sha256(path: str) -> str:
    stat = os.stat(path)
    cached = _digest_cache.get(path)
    if cached and cached[:2] == (stat.st_mtime, stat.st_size):
        return cached[2]
    value = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    digest = value.hexdigest()
    _digest_cache[path] = (stat.st_mtime, stat.st_size, digest)
    return digest


def _seed_artifacts() -> None:
    global _seeded_db_key
    db_key = os.environ.get("QODER_ASSET_DB", os.environ.get("QODER_SPEC_DB", "default"))
    if _seeded_db_key == db_key:
        return
    for artifact_id, meta in REGISTRY.items():
        path = os.path.join(DATA_DIR, meta["file"])
        if not os.path.exists(path):
            continue
        case = CASES.get(artifact_id, {})
        upsert_artifact({
            "artifact_id": artifact_id,
            "name": meta["name"],
            "file_name": meta["file"],
            "file_path": path,
            "format": meta["format"],
            "sha256": _sha256(path),
            "size_bytes": os.path.getsize(path),
            "declared_kind": meta["declared_kind"],
            "detected_kind": case.get("kind") or meta["declared_kind"],
            "family": case.get("family") or FAMILY_BY_KIND.get(meta["declared_kind"]),
            "source": "builtin",
            "parse_status": "queued",
            "validation_status": "error" if case.get("validation") == "blocked" else "pending",
        })

    manifest_path = GS_ROOT / "manifest.json"
    if manifest_path.exists():
        for model, label in ((key, key.replace("_", "–").upper()) for key in (
            "cnn_kan", "cnn_mlp", "fno_kan", "fno_mlp", "kan_kan", "mlp_mlp", "transformer_kan", "transformer_mlp"
        )):
            for suffix, file_name, kind in (("TRAIN", "metrics.csv", "series"), ("SUMMARY", "comparison_summary.json", "table")):
                path = GS_ROOT / "models" / model / file_name
                upsert_artifact({
                    "artifact_id": f"GS-{suffix}-{model.upper().replace('_', '-')}", "name": f"G-S {label} {'训练历史' if suffix == 'TRAIN' else '跨几何汇总'}",
                    "file_name": file_name, "file_path": str(path), "format": FORMAT_BY_EXTENSION[path.suffix.lstrip('.')],
                    "sha256": _sha256(str(path)), "size_bytes": path.stat().st_size, "declared_kind": kind,
                    "detected_kind": kind, "family": FAMILY_BY_KIND[kind], "dataset_id": "gs-pino-audit", "source": "gs-fixture",
                })
        for geometry in ("circular", "low_elongation", "medium_elongation", "high_elongation", "extreme_elongation", "negative_triangularity", "large_plasma", "small_plasma"):
            for solver, file_name in (("PINO", "pino_inference.npz"), ("TRAD", "traditional_inference.npz")):
                path = GS_ROOT / "cases" / geometry / file_name
                upsert_artifact({
                    "artifact_id": f"GS-{solver}-{geometry.upper().replace('_', '-')}", "name": f"G-S CNN–MLP {geometry.replace('_', ' ')} · {solver}",
                    "file_name": file_name, "file_path": str(path), "format": "NPZ", "sha256": _sha256(str(path)),
                    "size_bytes": path.stat().st_size, "declared_kind": "raster", "detected_kind": "raster", "family": "FLD",
                    "dataset_id": "gs-pino-audit", "source": "gs-fixture",
                })
    # Recover files created by the previous in-memory upload implementation.
    for path in Path(UPLOAD_DIR).glob("U-*_*"):
        artifact_id = path.name.split("_", 1)[0]
        try:
            get_artifact(artifact_id)
            continue
        except KeyError:
            pass
        ext = path.suffix.lstrip(".").lower()
        fmt = FORMAT_BY_EXTENSION.get(ext)
        if fmt:
            upsert_artifact({"artifact_id": artifact_id, "name": path.name.split("_", 1)[-1], "file_name": path.name, "file_path": str(path), "format": fmt, "sha256": _sha256(str(path)), "size_bytes": path.stat().st_size, "declared_kind": "auto", "source": "uploaded"})
    _seeded_db_key = db_key


def _resolve(artifact_id: str):
    _seed_artifacts()
    try:
        stored = get_artifact(artifact_id)
    except KeyError:
        raise HTTPException(404, f"未知 Artifact: {artifact_id}")
    meta = {
        "file": stored["file_name"], "path": stored["file_path"], "format": stored["format"],
        "declared_kind": stored["declared_kind"], "name": stored["name"], "source": stored["source"],
    }
    return meta, stored["file_path"]


def parse_artifact(artifact_id: str) -> dict:
    """按登记格式选择真实解析器并返回数据集画像。"""

    meta, fp = _resolve(artifact_id)
    if not os.path.exists(fp):
        raise HTTPException(404, f"数据文件不存在: {meta['file']}")
    fmt = meta["format"].upper()
    parser = PARSERS.get(fmt) or PARSERS.get(meta["format"])
    if parser is None:
        raise HTTPException(400, f"暂不支持的格式: {meta['format']}")
    parsed = parser(fp)
    if artifact_id == "A-1027":
        parsed["inferred_kind"] = "mesh"
    elif artifact_id == "A-1108":
        parsed["inferred_kind"] = "field"
    parsed.update(
        {
            "artifact_id": artifact_id,
            "file_name": os.path.basename(fp),
            "size_bytes": os.path.getsize(fp),
            "declared_kind": meta["declared_kind"],
            "name": meta.get("name", ""),
        }
    )
    return parsed


# --------------------------------------------------------------- 推荐引擎
def _cand(rank, chart, engine, engine_label, confidence, score, reason, prereq="无特殊前提", offline=True, glyph="table", url=None, model_url=None):
    if score == 0:
        breakdown = "无匹配规则，不计分"
    elif score >= 100:
        breakdown = "默认方法基础分 100" + (" + 支持离线内嵌 +2" if offline else "（服务端会话，不加离线分）")
    else:
        breakdown = "合法替代函数基础分 75" + (" + 支持离线 +2" if offline else "")
    return {
        "rank": rank,
        "chart": chart,
        "engine": engine,
        "engineLabel": engine_label,
        "confidence": confidence,
        "score": score,
        "scoreBreakdown": breakdown,
        "reason": reason,
        "prereq": prereq,
        "offline": offline,
        "glyph": glyph,
        "url": url,
        "model_url": model_url,
    }


RENDERER_LABELS = {
    "echarts-svg": "ECharts SVG", "perspective": "Perspective", "trame-vtkjs": "Trame + vtk.js",
    "o3dv": "Online3DViewer", "browser-native": "浏览器原生", "react-flow": "React Flow",
    "react": "React", "plotly": "Plotly", "vega": "Vega",
}


def _recommendation(task_id: str, label: str, kind: str, function_id: str, reason: str, encoding: dict | None = None, *, priority: int = 50) -> dict:
    fn = next(item for item in FUNCTIONS if item["id"] == function_id)
    offline = bool(fn["capabilities"]["offline"])
    return {
        "recommendation_id": task_id,
        "task_label": label,
        "kind": kind,
        "function_id": function_id,
        "renderer": fn["renderer"],
        "renderer_label": RENDERER_LABELS.get(fn["renderer"], fn["renderer"]),
        "score": 100 + (2 if offline else 0),
        "score_breakdown": f"默认方法 100{' + 离线能力 2' if offline else ''}",
        "offline": offline,
        "capabilities": fn["capabilities"],
        "status": fn["status"],
        "reason": reason,
        "encoding": encoding or {},
        "requirements": [],
        "task_priority": priority,
    }


def _profile_recommendations(artifact_id: str, profile: dict, declared_kind: str) -> dict:
    detected = "series" if profile["inferred_kind"] == "timeseries" else profile["inferred_kind"]
    blocked = declared_kind == "field" and detected == "mesh" and not profile.get("has_field")
    candidates: list[dict] = []
    numeric = profile.get("numeric_columns", [])
    time_col = profile.get("time_column")
    if profile.get("format") in {"CSV", "Parquet"}:
        if profile.get("is_log"):
            candidates.extend([
                _recommendation("log-table", "日志明细与筛选", "table", "table.perspective@2.0.0", "检测到日志等级、模块或自由文本列；先保留逐行证据。", {"columns": profile.get("columns", [])}, priority=10),
                _recommendation("log-levels", "日志等级分布", "distribution", "chart.echarts-distribution@2.1.0", "按 level/severity 聚合可快速定位 ERROR 与 WARNING。", {"field": profile.get("level_column")}, priority=20),
                _recommendation("log-residual", "残差与资源趋势", "series", "chart.echarts-series@2.1.0", "迭代、残差、CPU 或内存列适合按 seq/iter 查看趋势。", {"x": "seq" if "seq" in profile.get("columns", []) else None, "y": numeric[:5]}, priority=30),
            ])
        elif detected == "trajectory":
            candidates.extend([
                _recommendation("trajectory-3d", "三维轨迹管束", "trajectory", "scientific.trajectory@2.0.0", "检测到 particle_id、frame 与 x/y/z。", {"id": "particle_id", "time": "frame", "position": ["x", "y", "z"]}, priority=10),
                _recommendation("trajectory-table", "轨迹明细表", "table", "table.perspective@2.0.0", "逐帧记录便于筛选单个粒子和异常属性。", {"columns": profile.get("columns", [])}, priority=20),
            ])
        else:
            candidates.append(_recommendation("records-table", "可筛选数据表", "table", "table.perspective@2.0.0", "任何结构化行列数据都保留可核对的表格入口。", {"columns": profile.get("columns", [])}, priority=40))
            if time_col and numeric:
                candidates.append(_recommendation("time-series", "多变量趋势", "series", "chart.echarts-series@2.1.0", "检测到时间/step 列和数值列。", {"x": time_col, "y": [col for col in numeric if col != time_col][:6]}, priority=10))
            elif any(key in profile.get("columns", []) for key in ("epoch", "step", "iter")) and numeric:
                x = next(key for key in ("epoch", "step", "iter") if key in profile.get("columns", []))
                candidates.append(_recommendation("ordered-series", "训练/迭代趋势", "series", "chart.echarts-series@2.1.0", "检测到 epoch、step 或 iter 顺序列。", {"x": x, "y": [col for col in numeric if col != x][:6]}, priority=10))
            if numeric:
                candidates.append(_recommendation("numeric-distribution", "数值分布", "distribution", "chart.echarts-distribution@2.1.0", "数值列可检查分布、离群值与长尾。", {"field": numeric[0]}, priority=30))
            if len(numeric) >= 3:
                candidates.append(_recommendation("correlation-matrix", "相关矩阵", "matrix", "chart.echarts-matrix@2.1.0", "至少三个数值变量，可比较线性相关结构。", {"fields": numeric[:12]}, priority=35))
    elif detected == "scalar":
        candidates.extend([
            _recommendation("scalar-number", "数值指标", "scalar", "core.scalar-number@2.0.0", "单个数值适合直接显示并保留单位和目标。", priority=10),
            _recommendation("scalar-bar", "标量柱状图", "scalar", "chart.echarts-scalar@2.1.0", "当需要和目标或基线比较时，用柱长编码差异。", priority=20),
        ])
    elif profile.get("format") == "NPZ":
        if detected == "field":
            field_arrays = profile.get("field_arrays", [])
            vector_arrays = profile.get("vector_arrays", [])
            if vector_arrays:
                candidates.append(_recommendation("npz-field-vector", "NPZ 拓扑矢量场", "field", "scientific.field-vector@2.1.0", "NPZ 包含坐标拓扑和成组矢量分量。", {"vector_components": vector_arrays[:3]}, priority=10))
            if field_arrays or not vector_arrays:
                scalar_field = "phi_surface_normalized" if profile.get("is_miller_tokamak") and "phi_surface_normalized" in field_arrays else (field_arrays[0] if field_arrays else profile.get("main_array"))
                candidates.append(_recommendation("miller-surface-field" if profile.get("is_miller_tokamak") else "npz-field-scalar", "Miller 曲面时序标量场" if profile.get("is_miller_tokamak") else "NPZ 拓扑标量场", "field", "scientific.field-scalar@2.1.0", "识别到曲面坐标、时间轴和逐帧标量数组。" if profile.get("is_miller_tokamak") else "NPZ 包含坐标拓扑与标量物理量。", {"scalar_field": scalar_field, "field": scalar_field, "slice_index": max(0, int(profile.get("frames", 1)) // 2)}, priority=20 if vector_arrays else 10))
        elif profile.get("is_grad_shafranov"):
            candidates.extend([
                _recommendation("gs-field", "G-S 标量场浏览", "raster", "scientific.raster-scalar@2.1.0", "识别到 R/Z、ψ、Jφ、PDE residual 与 plasma mask。", {"field": "psi", "choices": profile.get("field_arrays", [])}, priority=10),
                _recommendation("gs-matrix", "二维场离线热力图", "matrix", "chart.echarts-matrix@2.1.0", "使用同一 NPZ 数值生成可离线读取的二维证据视图。", {"field": "psi", "choices": profile.get("field_arrays", [])}, priority=20),
                _recommendation("gs-residual-distribution", "PDE 残差分布", "distribution", "chart.echarts-distribution@2.1.0", "残差分布用于识别局部高误差与长尾。", {"field": "pde_residual"}, priority=30),
            ])
        elif detected == "raster":
            vector_arrays = profile.get("vector_arrays", [])
            if vector_arrays:
                candidates.append(_recommendation("raster-vector", "二维矢量栅格", "raster", "scientific.raster-vector@2.1.0", "识别到成组的速度分量，可显示方向、流线和幅值。", {"vector_components": vector_arrays[:3]}, priority=10))
            candidates.append(_recommendation("raster-scalar", "二维标量栅格", "raster", "scientific.raster-scalar@2.1.0", "二维规则数组可用色图和等值线读取。", {"scalar_field": profile.get("main_array")}, priority=20 if vector_arrays else 10))
        elif detected == "tensor":
            candidates.extend([
                _recommendation("tensor-slices", "张量分量切片", "tensor", "chart.echarts-tensor@2.1.0", "多维数组适合按分量/切片读取。", {"array": profile.get("main_array")}, priority=10),
                _recommendation("tensor-distribution", "张量数值分布", "distribution", "chart.echarts-distribution@2.1.0", "分布图揭示极值和异常尾部。", {"field": profile.get("main_array")}, priority=30),
            ])
        else:
            candidates.append(_recommendation("array-field", "二维数组热力图", "matrix", "chart.echarts-matrix@2.1.0", "二维数值数组可直接映射为热力图。", {"field": profile.get("main_array")}, priority=10))
    elif detected == "volume":
        vector_arrays = profile.get("vector_arrays", [])
        if vector_arrays:
            candidates.append(_recommendation("volume-vector", "三维矢量体", "volume", "scientific.volume-vector@2.1.0", "检测到三分量体素数组，可显示流线和幅值切片。", {"vector_components": vector_arrays[:3]}, priority=10))
        candidates.append(_recommendation("volume-3d", "三维标量体", "volume", "scientific.volume-scalar@2.1.0", "检测到三维体素和标量数组。", {"scalar_field": profile.get("scalar_array")}, priority=20 if vector_arrays else 10))
    elif detected == "field":
        fields = profile.get("field_variables", [])
        vector_fields = [item["name"] for item in fields if item.get("components") in {2, 3}]
        scalar_fields = [item["name"] for item in fields if item.get("components") == 1]
        if vector_fields:
            candidates.append(_recommendation("topology-vector-field", "拓扑矢量场", "field", "scientific.field-vector@2.1.0", "网格包含多分量矢量，可显示箭头、流线和幅值。", {"vector_components": vector_fields[:3]}, priority=10))
        if scalar_fields or not vector_fields:
            candidates.append(_recommendation("surface-field", "拓扑标量场", "field", "scientific.field-scalar@2.1.0", "网格包含可着色的点/单元标量。", {"scalar_field": scalar_fields[0] if scalar_fields else None}, priority=20 if vector_fields else 10))
    elif detected == "mesh":
        candidates.append(_recommendation("mesh-o3dv", "三维几何查看", "mesh", "scientific.mesh@2.0.0", "纯几何或提取表面由 Online3DViewer 加载。", priority=10))
    elif detected == "image":
        candidates.append(_recommendation("native-image", "原始图像", "image", "media.image@2.0.0", "图像使用浏览器原生解码并保留像素尺寸。", priority=10))
    elif detected == "text_document":
        candidates.append(_recommendation("native-document", "文档阅读", "text_document", "core.markdown@2.0.0", "文本和 Markdown 使用浏览器原生阅读路径。", priority=10))
    elif detected == "table":
        candidates.append(_recommendation("records-table", "指标表格", "table", "table.perspective@2.0.0", "结构化指标以表格保留名称和值。", priority=10))

    candidates.sort(key=lambda item: (item["task_priority"], -item["score"], item["recommendation_id"]))
    for rank, candidate in enumerate(candidates, 1):
        candidate["rank"] = rank
    return {
        "artifact_id": artifact_id,
        "blocked": blocked,
        "kind": detected,
        "declared_kind": declared_kind,
        "hit_rule": f"{profile.get('format')} / {detected} / {len(candidates)} tasks",
        "error_issues": [{"rule": "V-MESH-006", "title": "声明为物理场，但文件不含场变量", "scope": "整个 Artifact", "suggestion": "按检测到的 GEO/mesh 打开，或提交分类修正版本。"}] if blocked else [],
        "recovery_candidates": [candidate for candidate in candidates if candidate["kind"] == "mesh"] if blocked else [],
        "candidates": [] if blocked else candidates,
        "detected_candidates": candidates,
    }


def analyze_artifact(artifact_id: str) -> dict:
    """执行解析、数据质量检测、分类推断和推荐结果持久化。"""

    _seed_artifacts()
    try:
        stored = get_artifact(artifact_id)
        profile = parse_artifact(artifact_id)
        recommendations = _profile_recommendations(artifact_id, profile, stored["declared_kind"])
        validation = "error" if recommendations["blocked"] else ("warning" if stored["declared_kind"] not in {"auto", "", profile["inferred_kind"], "timeseries" if profile["inferred_kind"] == "series" else profile["inferred_kind"]} else "passed")
        save_analysis(artifact_id, profile, recommendations, validation_status=validation, family=FAMILY_BY_KIND.get(profile["inferred_kind"], "PLT"))
        return {"artifact": get_artifact(artifact_id), "parse": profile, "recommendations": recommendations}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        try:
            save_analysis_error(artifact_id, {"code": "PARSE_FAILED", "message": str(exc), "stage": "parse"})
        except KeyError:
            pass
        raise HTTPException(422, detail={"code": "PARSE_FAILED", "message": str(exc), "stage": "parse"}) from exc


def recommend_artifact(artifact_id: str, function_id: str | None = None) -> dict:
    """根据已保存画像返回确定性的可视化候选和参数 Schema。"""

    _seed_artifacts()
    try:
        stored = get_artifact(artifact_id)
    except KeyError:
        case = CASES.get(artifact_id)
        if case is None:
            raise HTTPException(404, f"未知 Artifact: {artifact_id}")
        kind = next(item for item in KINDS if item["id"] == case["kind"])
        candidates = [_recommendation(case["function_id"].split("@")[0], case["name"], case["kind"], case["function_id"], kind["definition"])]
        result = {"artifact_id": artifact_id, "blocked": case.get("validation") == "blocked", "kind": case["kind"], "candidates": candidates, "detected_candidates": candidates}
        return enrich_recommendations(result, {}, FUNCTIONS)
    recommendations = stored.get("recommendations")
    if stored["parse_status"] != "ready" or not recommendations:
        recommendations = analyze_artifact(artifact_id)["recommendations"]
        # 首次分析会写入画像；必须重新读取，不能用分析前的空profile生成动态字段Schema。
        stored = get_artifact(artifact_id)
    # Normalize records persisted by older application revisions before
    # returning the current public contract.
    recommendations.pop("variant", None)
    for collection in ("candidates", "detected_candidates", "recovery_candidates"):
        for item in recommendations.get(collection, []):
            item.pop("variant", None)
            if item.get("function_id"):
                item["function_id"] = canonical_function(item["function_id"])
    function_id = canonical_function(function_id) if function_id else None
    legal = [item["function_id"] for item in recommendations.get("detected_candidates", recommendations.get("candidates", []))]
    if function_id and function_id not in legal:
        raise HTTPException(422, detail={"code": "INCOMPATIBLE_FUNCTION", "message": f"{function_id} 不兼容当前数据画像", "legal_alternatives": legal})
    if function_id:
        selected = [item for item in recommendations.get("detected_candidates", []) if item["function_id"] == function_id]
        return enrich_recommendations({**recommendations, "blocked": False, "candidates": selected}, stored.get("profile") or {}, FUNCTIONS)
    return enrich_recommendations(recommendations, stored.get("profile") or {}, FUNCTIONS)


def _json_records(df: pd.DataFrame, limit: int = 240) -> list[dict]:
    sample = df.head(limit).astype(object).where(pd.notna(df.head(limit)), None)
    return [{str(key): value.item() if isinstance(value, np.generic) else value for key, value in row.items()} for row in sample.to_dict("records")]


def _sample_frame(df: pd.DataFrame, maximum: int = 360) -> pd.DataFrame:
    if len(df) <= maximum:
        return df
    indices = np.linspace(0, len(df) - 1, maximum, dtype=int)
    return df.iloc[indices]


def _downsample_matrix(values: np.ndarray, max_rows: int = 72, max_cols: int = 96) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim > 2:
        array = array.reshape(array.shape[-2], array.shape[-1])
    row_step = max(1, int(np.ceil(array.shape[0] / max_rows)))
    col_step = max(1, int(np.ceil(array.shape[1] / max_cols)))
    return np.nan_to_num(array[::row_step, ::col_step], nan=0.0, posinf=0.0, neginf=0.0)


def _table_source(stored: dict) -> pd.DataFrame:
    path = stored["file_path"]
    if stored["format"].upper() == "CSV":
        return pd.read_csv(path, low_memory=False)
    if stored["format"].upper() == "PARQUET":
        return pd.read_parquet(path)
    if stored["format"].upper() == "JSON":
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(value, list):
            return pd.json_normalize(value)
        if isinstance(value, dict):
            return pd.DataFrame([{"metric": key, "value": child if isinstance(child, (str, int, float, bool)) or child is None else json.dumps(child, ensure_ascii=False)} for key, child in value.items()])
    raise ValueError(f"not a tabular source: {stored['format']}")


def _payload_for_recommendation(stored: dict, profile: dict, recommendation: dict, base_url: str, parameters: dict | None = None) -> tuple[dict, str]:
    params = {**recommendation.get("encoding", {}), **(parameters or {})}
    task = recommendation["recommendation_id"]
    kind = recommendation["kind"]
    path = stored["file_path"]
    takeaway = profile.get("summary", "数据已按原始文件解析。")
    if kind == "table":
        frame = _table_source(stored)
        data = {"columns": list(frame.columns), "rows": _json_records(frame), "total_rows": int(len(frame))}
        if profile.get("is_log"):
            errors = int(frame[profile["level_column"]].astype(str).str.upper().eq("ERROR").sum()) if profile.get("level_column") else 0
            takeaway = f"日志共 {len(frame):,} 行，其中 ERROR {errors:,} 行；表格保留筛选和逐行核对。"
        else:
            takeaway = f"已加载 {len(frame):,} 行 × {len(frame.columns)} 列；当前预览保留前 {min(len(frame), 240)} 行。"
    elif kind == "series":
        frame = _table_source(stored)
        frame = _sample_frame(frame, int(params.get("sample_limit", 720)))
        x_name = params.get("x") or profile.get("time_column") or next((key for key in ("epoch", "step", "iter", "seq") if key in frame), frame.columns[0])
        y_names = [name for name in (params.get("y") or profile.get("numeric_columns", [])) if name in frame and name != x_name][:6]
        if not y_names:
            y_names = [name for name in frame.select_dtypes(include=np.number).columns if name != x_name][:6]
        if params.get("sort_order") in {"ascending", "descending"}:
            frame = frame.sort_values(x_name, ascending=params["sort_order"] == "ascending")
        data = {"x": [value.item() if isinstance(value, np.generic) else value for value in frame[x_name].tolist()], "x_label": x_name, "y_label": "数值", "series": [{"name": name, "values": [None if pd.isna(value) else float(value) for value in frame[name].tolist()]} for name in y_names]}
        takeaway = f"以 {x_name} 为横轴展示 {len(y_names)} 个数值序列；最多抽取 360 个有序样本。"
    elif kind == "distribution":
        field = params.get("field")
        if stored["format"].upper() == "NPZ":
            with np.load(path, allow_pickle=False) as arrays:
                field = field if field in arrays.files else profile.get("main_array")
                values = np.asarray(arrays[field], dtype=float).ravel()
        else:
            frame = _table_source(stored)
            if field and field in frame and not pd.api.types.is_numeric_dtype(frame[field]):
                counts = frame[field].astype(str).value_counts().head(20)
                return ({"bins": list(counts.index) + [""], "counts": [int(value) for value in counts.values], "field": field, "categorical": True}, f"按 {field} 汇总前 {len(counts)} 个类别。")
            field = field if field in frame and pd.api.types.is_numeric_dtype(frame[field]) else frame.select_dtypes(include=np.number).columns[0]
            values = frame[field].dropna().to_numpy(dtype=float)
        bin_count = int(params.get("bins", 24))
        counts, bins = np.histogram(values[np.isfinite(values)], bins=bin_count)
        data = {"bins": [float(value) for value in bins], "counts": [int(value) for value in counts], "field": field}
        takeaway = f"{field} 的 {len(values):,} 个值按 {bin_count} 箱统计；极值与缺失不通过平滑隐藏。"
    elif kind in {"matrix", "tensor", "raster"}:
        if stored["format"].upper() == "NPZ":
            with np.load(path, allow_pickle=False) as arrays:
                field = params.get("field") or params.get("array") or profile.get("main_array")
                field = field if field in arrays.files else profile.get("main_array")
                values = np.asarray(arrays[field], dtype=float)
                if values.ndim > 2:
                    values = values[0]
                matrix = _downsample_matrix(values)
                data = {"values": matrix.tolist(), "rows": matrix.shape[0], "cols": matrix.shape[1], "field": field, "field_choices": profile.get("field_arrays", [field]), "source_shape": list(values.shape), "coordinate_arrays": profile.get("coordinate_arrays", [])}
                takeaway = f"{field} 来自原始 NPZ，源网格 {' × '.join(map(str, values.shape))}；显示时只做规则降采样。"
        else:
            frame = _table_source(stored)
            fields = [name for name in (params.get("fields") or profile.get("numeric_columns", [])) if name in frame][:12]
            corr = frame[fields].corr().fillna(0).to_numpy(dtype=float)
            data = {"matrix": corr.tolist(), "labels": fields}
            takeaway = f"相关矩阵使用 {len(fields)} 个数值字段和完整有效样本计算。"
    elif kind == "volume":
        vtk = _vtk()
        from vtk.util import numpy_support
        reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(path)
        reader.Update()
        image = reader.GetOutput()
        dims = image.GetDimensions()
        scalars = image.GetPointData().GetScalars()
        values = numpy_support.vtk_to_numpy(scalars).reshape(dims[2], dims[1], dims[0])
        axis = params.get("slice_axis", "z")
        axis_size = {"x": dims[0], "y": dims[1], "z": dims[2]}[axis]
        requested = int(params.get("slice_index", axis_size // 2))
        index = max(0, min(axis_size - 1, requested if requested else axis_size // 2))
        slice_values = values[index] if axis == "z" else values[:, index, :] if axis == "y" else values[:, :, index]
        matrix = _downsample_matrix(slice_values)
        data = {"values": matrix.tolist(), "rows": matrix.shape[0], "cols": matrix.shape[1], "field": params.get("field") or scalars.GetName(), "source_shape": list(dims), "slice_axis": axis, "slice_index": index, "fallback_label": "真实中截面静态证据"}
        takeaway = f"体数据源维度 {dims[0]} × {dims[1]} × {dims[2]}；当前降级视图是同一 VTI 的 {axis.upper()}={index} 切片。"
    elif kind == "field":
        if stored["format"].upper() == "NPZ":
            with np.load(path, allow_pickle=False) as arrays:
                requested_field = params.get("scalar_field") or params.get("field") or profile.get("main_array")
                field = requested_field if requested_field in arrays.files else profile.get("main_array")
                values = np.asarray(arrays[field], dtype=float)
                frame_index = 0
                frame_count = int(values.shape[0]) if values.ndim == 3 and profile.get("temporal_field") else 1
                if frame_count > 1:
                    requested_index = int(params.get("slice_index", frame_count // 2))
                    frame_index = max(0, min(frame_count - 1, requested_index))
                    frame_values = values[frame_index]
                else:
                    frame_values = values.squeeze()
                if frame_values.ndim != 2:
                    raise ValueError("NPZ 物理场需要可选择的二维场帧")
                matrix = _downsample_matrix(frame_values)
                time_values = np.asarray(arrays["time_R_over_vti"], dtype=float) if "time_R_over_vti" in arrays.files else np.arange(frame_count, dtype=float)
                diagnostic_names = profile.get("diagnostic_arrays", [])
                diagnostics = [
                    {"name": name, "values": [float(value) for value in np.asarray(arrays[name], dtype=float).tolist()]}
                    for name in diagnostic_names if name in arrays.files
                ]
                data = {
                    "values": matrix.tolist(), "rows": matrix.shape[0], "cols": matrix.shape[1],
                    "field": field, "field_choices": profile.get("field_arrays", [field]),
                    "source_shape": list(values.shape), "topology_shape": profile.get("topology_shape", list(frame_values.shape)),
                    "frame_index": frame_index, "frame_count": frame_count,
                    "time": float(time_values[frame_index]) if len(time_values) > frame_index else float(frame_index),
                    "time_values": [float(value) for value in time_values.tolist()], "diagnostics": diagnostics,
                    "coordinate_arrays": profile.get("coordinate_arrays", []),
                    "fallback_label": f"真实 NPZ 曲面场第 {frame_index} 帧数值证据",
                }
                takeaway = f"{field} 来自原始 NPZ；当前为第 {frame_index + 1}/{frame_count} 帧，曲面网格 {' × '.join(map(str, frame_values.shape))}。"
        else:
            vtk = _vtk()
            from vtk.util import numpy_support
            reader = vtk.vtkXMLUnstructuredGridReader()
            reader.SetFileName(path)
            reader.Update()
            dataset = reader.GetOutput()
            requested_field = params.get("scalar_field") or params.get("field")
            array = dataset.GetPointData().GetArray(requested_field) if requested_field else dataset.GetPointData().GetArray(0)
            if array is None:
                array = dataset.GetCellData().GetArray(requested_field) if requested_field else dataset.GetCellData().GetArray(0)
            if array is None:
                raise ValueError("VTU 不包含可视化场数组")
            values = numpy_support.vtk_to_numpy(array).astype(float).reshape(-1)
            width = max(1, int(np.ceil(np.sqrt(values.size))))
            padded = np.pad(values, (0, width * width - values.size), constant_values=np.nan).reshape(width, width)
            matrix = _downsample_matrix(padded)
            data = {"values": matrix.tolist(), "rows": matrix.shape[0], "cols": matrix.shape[1], "field": array.GetName(), "source_points": int(dataset.GetNumberOfPoints()), "fallback_label": "真实场值二维索引视图"}
            takeaway = f"{array.GetName()} 来自实际 VTU 数组；交互场景由 Trame/vtk.js 渲染，降级图保留同一数值范围。"
    elif kind == "trajectory":
        frame = pd.read_parquet(path)
        id_field = params.get("id") if params.get("id") in frame else "particle_id"
        time_field = params.get("time") if params.get("time") in frame else "frame"
        position = [name for name in (params.get("position") or ["x", "y", "z"]) if name in frame][:3]
        if len(position) < 2:
            position = ["x", "y", "z"]
        max_tracks = int(params.get("max_tracks", 64))
        trail_length = int(params.get("trail_length", 90))
        ids = list(frame[id_field].drop_duplicates().head(max_tracks))
        tracks = []
        for particle_id in ids:
            group = _sample_frame(frame[frame[id_field] == particle_id].sort_values(time_field), trail_length)
            tracks.append([[float(value) for value in row] for row in group[position].itertuples(index=False, name=None)])
        data = {"tracks": tracks, "track_count": int(frame[id_field].nunique()), "frame_count": int(frame[time_field].nunique()), "attributes": [name for name in frame.columns if name not in {id_field, time_field, *position}], "position_fields": position, "fallback_label": f"真实轨迹 {position[0].upper()}{position[1].upper()} 投影"}
        takeaway = f"实际数据包含 {data['track_count']:,} 条轨迹 × {data['frame_count']} 帧；二维降级图抽取前 {len(tracks)} 条。"
    elif kind == "mesh":
        data = {"format": stored["format"], "source_file": stored["file_name"]}
        takeaway = f"{stored['format']} 表面表示由同一源文件转换为 GLB，并交给 Online3DViewer。"
    elif kind == "image":
        data = {"url": f"{base_url}api/artifact/{urllib.parse.quote(stored['artifact_id'])}/file/{urllib.parse.quote(stored['file_name'])}", "alt": stored["name"], "width": profile.get("width"), "height": profile.get("height")}
    elif kind == "text_document":
        url = f"{base_url}api/artifact/{urllib.parse.quote(stored['artifact_id'])}/file/{urllib.parse.quote(stored['file_name'])}"
        if stored["format"].upper() in {"MD", "MARKDOWN"}:
            data = {"markdown": Path(path).read_text(encoding="utf-8", errors="replace")[:200_000], "url": url}
        else:
            data = {"markdown": f"该文档以隔离方式提供。\n\n[打开来源文件]({url})", "url": url, "native_document": True}
    else:
        data = {"summary": profile.get("summary")}
    return data, takeaway


def _example_for_stored(artifact_id: str, base_url: str, recommendation_id: str | None = None, parameters: dict | None = None) -> dict:
    stored = get_artifact(artifact_id)
    if stored["parse_status"] != "ready" or not stored.get("profile"):
        analyze_artifact(artifact_id)
        stored = get_artifact(artifact_id)
    recommendations = stored["recommendations"]
    all_candidates = recommendations.get("detected_candidates", recommendations.get("candidates", []))
    selected = next((item for item in all_candidates if item["recommendation_id"] == recommendation_id), None)
    if selected is None:
        latest = latest_visualization(artifact_id)
        if latest:
            selected = next((item for item in all_candidates if item["recommendation_id"] == latest["recommendation_id"]), None)
            parameters = latest["parameters"]
        selected = selected or (all_candidates[0] if all_candidates else None)
    if selected is None:
        raise HTTPException(422, detail={"code": "NO_VISUALIZATION", "message": "当前数据画像没有可用的可视化任务"})
    data, takeaway = _payload_for_recommendation(stored, stored["profile"], selected, base_url, parameters)
    renderer_url = None
    fallback_url = None
    if selected["renderer"] == "o3dv":
        renderer_url = f"{base_url}api/artifact/{urllib.parse.quote(artifact_id)}/representation/o3dv.glb"
        if artifact_id == "A-1027":
            fallback_url = f"{base_url}api/example-assets/A-1027-snapshot"
    elif selected["renderer"] == "trame-vtkjs" and artifact_id in TRAME_VIEW:
        renderer_url = _trame_url(TRAME_VIEW[artifact_id])
        snapshot_asset = TRAME_SNAPSHOT_ASSET.get(artifact_id)
        if snapshot_asset:
            fallback_url = f"{base_url}api/example-assets/{snapshot_asset}"
    elif selected["renderer"] == "browser-native":
        renderer_url = data.get("url")
    # A declared-kind mismatch blocks saving, but the detected-kind preview is a
    # recoverable evidence path.  Keep the warning visible without suppressing
    # the truthful GEO renderer.
    validation = (
        "warning"
        if recommendations.get("blocked") and selected["kind"] == recommendations.get("kind")
        else "blocked"
        if stored["validation_status"] == "error" and recommendations.get("blocked")
        else stored["validation_status"]
    )
    registered_case = CASES.get(artifact_id)
    if registered_case:
        case_type = registered_case["case_type"]
        case_type_label = registered_case["case_type_label"]
    elif stored["source"] == "uploaded":
        case_type, case_type_label = "user-upload", "用户上传"
    elif stored["source"] == "gs-fixture":
        case_type, case_type_label = "file-fixture", "G-S 精选文件"
    else:
        case_type, case_type_label = "file-fixture", "文件型工程案例"
    return {
        "artifact": {
            "id": artifact_id, "name": stored["name"], "family": FAMILY_BY_KIND.get(selected["kind"], stored.get("family")),
            "kind": selected["kind"], "format": stored["format"],
            "description": stored["profile"].get("summary"), "takeaway": takeaway, "validation": validation,
            "source_note": f"{case_type_label} · SHA-256 {stored['sha256'][:16]}…",
            "case_type": case_type, "case_type_label": case_type_label,
        },
        "resolved_spec": {"function_id": selected["function_id"], "params": {**selected.get("encoding", {}), **(parameters or {})}},
        "renderer": {"owner": selected["renderer"], "label": selected["renderer_label"], "url": renderer_url, "fallback_url": fallback_url, "status": "live" if renderer_url or selected["renderer"] in {"echarts-svg", "plotly", "vega", "perspective", "react", "react-flow", "browser-native"} else "partial", "fallback": "same-renderer-snapshot" if fallback_url else "same-renderer-capture-required"},
        "data": data,
        "recommendation": selected,
    }


def ensure_builtin_artifacts() -> None:
    """确保内置文件型数据资产已登记，供其他一级模块通过公开门面查询。"""

    _seed_artifacts()


def build_example(
    artifact_id: str,
    base_url: str,
    recommendation_id: str | None = None,
    parameters: dict | None = None,
) -> dict:
    """根据已登记数据集和推荐配置生成可运行案例载荷。"""

    return _example_for_stored(artifact_id, base_url, recommendation_id, parameters)


def artifact_to_public_dto(item: dict) -> dict:
    """把数据资产记录转换为数据集查看页面使用的稳定DTO。"""

    return _public_artifact(item)


def supported_upload_formats() -> dict[str, str]:
    """返回解析管线当前接受的上传扩展名与格式映射副本。"""

    return dict(FORMAT_BY_EXTENSION)


def supported_kind_names() -> tuple[str, ...]:
    """返回允许用户声明的数据语义类型名称。"""

    return tuple(FAMILY_BY_KIND)


def _size_label(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit in {"B", "KB"} else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _public_artifact(item: dict) -> dict:
    profile = item.get("profile") or {}
    status = item.get("validation_status") or "pending"
    if status == "pending" and item.get("parse_status") == "ready":
        status = "passed"
    kind = item.get("detected_kind") or item.get("declared_kind") or "table"
    return {
        "id": item["artifact_id"], "artifact_id": item["artifact_id"], "name": item["name"],
        "file_name": item["file_name"], "fileName": item["file_name"], "format": item["format"],
        "sha256": item["sha256"], "size_bytes": item["size_bytes"], "size_label": _size_label(item["size_bytes"]),
        "declared_kind": item["declared_kind"], "detected_kind": item.get("detected_kind"), "kind": kind,
        "family": item.get("family") or FAMILY_BY_KIND.get(kind), "dataset_id": item.get("dataset_id"), "source": item["source"],
        "parse_status": item["parse_status"], "validation_status": status,
        "validation": {"status": status, "error": 1 if status == "error" else 0, "warning": 1 if status == "warning" else 0, "info": 1 if status in {"passed", "warning"} else 0, "large": bool(profile.get("large"))},
        "scale": profile.get("summary") or "等待内容分析", "version": item["version"], "updated_at": item["updated_at"],
        "updatedAt": item["updated_at"], "profile": profile, "recommendation_count": len((item.get("recommendations") or {}).get("detected_candidates", [])),
        "blocked": bool((item.get("recommendations") or {}).get("blocked")),
    }
