"""AI4E VizReport — trame 3D 可视化服务（FLD / ENT）

与前端声明的 Artifact 完全对齐，加载真实样例数据：
  view=raster      FLD · 二维标量栅格     -> 确定性生成场
  view=volume      FLD · 燃烧室温度体数据 -> combustor_temp_volume.vti   （A-1028）
  view=field       FLD · 涡轮叶片压力场   -> turbine_blade_mesh.vtu      （A-1108）
  view=miller_field FLD · Miller 托卡马克时序场 -> miller_tokamak_timeseries_240frames.npz（A-1115）
  view=points      ENT · 空间点集         -> 确定性生成点集
  view=trajectory  ENT · 羽流粒子轨迹     -> particle_traj_plume.parquet （A-1029）

渲染方式：**客户端渲染（VtkLocalView / vtk.js）**。场景在服务端构建并序列化，
由浏览器 WebGL 渲染 —— 规避 macOS 上 trame 服务端 OpenGL 会话的 SIGSEGV 崩溃。

启动：在backend目录执行 ``python -m modules.visPhysField.trameServer --port 8090``
前端以 iframe 嵌入时携带 sessionURL、secret 与 view，以直连 wslink，避免误走 launcher。
"""

from __future__ import annotations

import asyncio
import os

import numpy as np
import pandas as pd
import vtk
from vtk.util import numpy_support  # noqa: F401

from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import html, vuetify2
from trame_client.widgets import trame
from trame_vtk.widgets.vtk import VtkLocalView
from trame_server.utils import asynchronous

from .modules.fieldVisualization.timelineAnimation import MillerFieldAnimation
from infrastructure.config import REPOSITORY_ROOT

DATA_DIR = str(REPOSITORY_ROOT / "resources" / "examples")

VIEW_META = {
    "raster": {
        "title": "FLD · 二维标量栅格",
        "artifact": "CASE-RASTER-SCALAR",
        "engine": "Trame + vtk.js · 标量面",
        "file": "确定性栅格数据",
        "note": "30 × 18 规则网格 · stability index · 连续色标",
    },
    "raster_vector": {
        "title": "FLD · 圆柱绕流二维速度场",
        "artifact": "CASE-RASTER-VECTOR",
        "engine": "Trame + vtk.js · 矢量箭头与幅值",
        "file": "基于 CFDBench u/v 约定的轻量重建",
        "note": "二维规则网格 · u/v 分量 · 箭头方向 + 速度幅值",
    },
    "volume": {
        "title": "FLD · 燃烧室温度体数据",
        "artifact": "A-1028",
        "engine": "vtk.js · 体渲染（客户端）",
        "file": "combustor_temp_volume.vti",
        "note": "144×112×96 体素 · temperature (K) · 等值面 1100 / 1500 K",
    },
    "volume_vector": {
        "title": "FLD · 外流场三维速度体",
        "artifact": "CASE-VOLUME-VECTOR",
        "engine": "Trame + vtk.js · 三维矢量箭头",
        "file": "基于 PhysicsNeMo 外气动示例的轻量重建",
        "note": "三维体素采样 · u/v/w 分量 · 按速度幅值着色",
    },
    "trajectory": {
        "title": "ENT · 羽流粒子轨迹",
        "artifact": "A-1029",
        "engine": "vtk.js · 轨迹管束（客户端）",
        "file": "particle_traj_plume.parquet",
        "note": "900 条轨迹 × 160 帧 · 按速度着色（渲染取 500 条）",
    },
    "field": {
        "title": "FLD · 涡轮叶片压力场",
        "artifact": "A-1108",
        "engine": "Trame + vtk.js · 表面场着色",
        "file": "turbine_blade_mesh.vtu",
        "note": "30,720 点 · 60,800 单元 · pressure 着色",
    },
    "field_vector": {
        "title": "FLD · 机翼近壁速度场",
        "artifact": "CASE-FIELD-VECTOR",
        "engine": "Trame + vtk.js · 表面矢量箭头",
        "file": "turbine_blade_mesh.vtu · 确定性近壁速度重建",
        "note": "非规则表面采样 · 三分量速度 · 方向与幅值同时可读",
    },
    "miller_field": {
        "title": "FLD · Miller 托卡马克静电势场",
        "artifact": "A-1115",
        "engine": "Trame + vtk.js · 曲面标量场",
        "file": "miller_tokamak_timeseries_240frames.npz",
        "note": "240 帧 · 148×176 Miller 曲面网格 · 支持播放、逐帧与时间定位",
    },
    "points": {
        "title": "ENT · 空间点集",
        "artifact": "CASE-POINT-SET-POINTS",
        "engine": "Trame + vtk.js · 三维点集",
        "file": "确定性点集数据",
        "note": "220 个空间采样点 · temperature 着色",
    },
}

BG = (0.055, 0.075, 0.105)


def _ensure_data():
    need = [VIEW_META[k]["file"] for k in ("volume", "field", "trajectory")]
    if not all(os.path.exists(os.path.join(DATA_DIR, f)) for f in need):
        from scripts.generate_example_data import generate_all

        generate_all()


def _mk_rw(ren):
    ren.SetBackground(*BG)
    rw = vtk.vtkRenderWindow()
    rw.AddRenderer(ren)
    return rw


# ---------------------------------------------------------------- FLD 二维栅格
def build_raster_scene():
    """构建二维标量栅格Trame场景。"""

    nx, ny = 30, 18
    plane = vtk.vtkPlaneSource()
    plane.SetOrigin(0.0, 0.0, 0.0)
    plane.SetPoint1(1.0, 0.0, 0.0)
    plane.SetPoint2(0.0, 0.62, 0.0)
    plane.SetXResolution(nx - 1)
    plane.SetYResolution(ny - 1)
    plane.Update()

    values = []
    for y in range(ny):
        yn = y / max(1, ny - 1)
        for x in range(nx):
            xn = x / max(1, nx - 1)
            values.append(0.45 + 0.34 * np.sin(5 * xn + 3 * yn) + 0.22 * np.cos(7 * yn - 2 * xn))
    scalars = numpy_support.numpy_to_vtk(np.asarray(values, dtype=np.float32), deep=True)
    scalars.SetName("stability_index")
    plane.GetOutput().GetPointData().SetScalars(scalars)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.66, 0.0)
    lut.SetRange(float(np.min(values)), float(np.max(values)))
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(plane.GetOutput())
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(float(np.min(values)), float(np.max(values)))
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    camera = ren.GetActiveCamera()
    camera.SetPosition(0.5, 0.31, 1.7)
    camera.SetFocalPoint(0.5, 0.31, 0.0)
    camera.SetViewUp(0.0, 1.0, 0.0)
    camera.ParallelProjectionOn()
    return _mk_rw(ren)


def _vector_glyph_actor(points_array, vectors_array, scale_factor: float):
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    for index, point in enumerate(points_array):
        point_id = points.InsertNextPoint(*[float(value) for value in point])
        vertex = vtk.vtkVertex()
        vertex.GetPointIds().SetId(0, point_id)
        vertices.InsertNextCell(vertex)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetVerts(vertices)
    vectors = np.asarray(vectors_array, dtype=np.float32)
    vtk_vectors = numpy_support.numpy_to_vtk(vectors, deep=True)
    vtk_vectors.SetName("velocity")
    poly.GetPointData().SetVectors(vtk_vectors)
    magnitude = numpy_support.numpy_to_vtk(np.linalg.norm(vectors, axis=1).astype(np.float32), deep=True)
    magnitude.SetName("speed")
    poly.GetPointData().SetScalars(magnitude)

    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(8)
    arrow.SetShaftResolution(8)
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(poly)
    glyph.SetSourceConnection(arrow.GetOutputPort())
    glyph.SetVectorModeToUseVector()
    glyph.SetScaleModeToScaleByVector()
    glyph.SetScaleFactor(scale_factor)
    glyph.OrientOn()
    glyph.Update()

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.66, 0.0)
    lut.SetRange(float(np.min(np.linalg.norm(vectors, axis=1))), float(np.max(np.linalg.norm(vectors, axis=1))))
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph.GetOutputPort())
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(lut.GetRange())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    return actor


def build_raster_vector_scene():
    """构建二维矢量栅格与幅值着色场景。"""

    points, vectors = [], []
    for y in np.linspace(-0.55, 0.55, 11):
        for x in np.linspace(-1.0, 1.6, 18):
            radius_sq = x * x + y * y
            damping = np.exp(-radius_sq / 0.18)
            points.append((x, y, 0.0))
            vectors.append((1.0 - 0.86 * damping, 0.7 * y * np.exp(-((x - 0.15) ** 2) / 0.42), 0.0))
    ren = vtk.vtkRenderer()
    ren.AddActor(_vector_glyph_actor(points, vectors, 0.105))
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(0.16)
    cylinder.SetHeight(0.035)
    cylinder.SetResolution(48)
    cylinder_mapper = vtk.vtkPolyDataMapper()
    cylinder_mapper.SetInputConnection(cylinder.GetOutputPort())
    cylinder_actor = vtk.vtkActor()
    cylinder_actor.SetMapper(cylinder_mapper)
    cylinder_actor.RotateX(90)
    cylinder_actor.GetProperty().SetColor(0.75, 0.78, 0.83)
    ren.AddActor(cylinder_actor)
    camera = ren.GetActiveCamera()
    camera.SetPosition(0.3, 0.0, 4.2)
    camera.SetFocalPoint(0.3, 0.0, 0.0)
    camera.SetViewUp(0.0, 1.0, 0.0)
    camera.ParallelProjectionOn()
    return _mk_rw(ren)


# ---------------------------------------------------------------- ENT 空间点集
def build_points_scene():
    """构建三维空间点集场景。"""

    rng = np.random.default_rng(1109)
    points = vtk.vtkPoints()
    vertices = vtk.vtkCellArray()
    temperatures = []
    for index in range(220):
        x = float(rng.random() * 2.2)
        spread = 0.08 + 0.18 * x
        point_id = points.InsertNextPoint(x, float(rng.normal(0, spread)), float(rng.normal(0, spread)))
        vertex = vtk.vtkVertex()
        vertex.GetPointIds().SetId(0, point_id)
        vertices.InsertNextCell(vertex)
        temperatures.append(1200 - 280 * x + float(rng.normal(0, 35)))

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetVerts(vertices)
    scalars = numpy_support.numpy_to_vtk(np.asarray(temperatures, dtype=np.float32), deep=True)
    scalars.SetName("temperature")
    poly.GetPointData().SetScalars(scalars)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.66, 0.0)
    lut.SetRange(float(np.min(temperatures)), float(np.max(temperatures)))
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(float(np.min(temperatures)), float(np.max(temperatures)))
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(6)

    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    camera = ren.GetActiveCamera()
    camera.SetPosition(1.1, -3.5, 1.8)
    camera.SetFocalPoint(1.1, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)
    return _mk_rw(ren)


# ---------------------------------------------------------------- FLD 体数据
def build_volume_scene():
    """构建三维标量体渲染场景。"""

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(os.path.join(DATA_DIR, VIEW_META["volume"]["file"]))
    reader.Update()
    img = reader.GetOutput()
    lo, hi = img.GetScalarRange()

    ren = vtk.vtkRenderer()

    # 体渲染：温度色图（冷蓝 → 橙红 → 亮黄）
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(img)
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(lo, 0.10, 0.15, 0.45)
    ctf.AddRGBPoint(lo + (hi - lo) * 0.35, 0.15, 0.35, 0.75)
    ctf.AddRGBPoint(lo + (hi - lo) * 0.60, 0.90, 0.45, 0.12)
    ctf.AddRGBPoint(lo + (hi - lo) * 0.82, 0.98, 0.75, 0.15)
    ctf.AddRGBPoint(hi, 1.0, 0.95, 0.55)
    ofun = vtk.vtkPiecewiseFunction()
    ofun.AddPoint(lo, 0.0)
    ofun.AddPoint(lo + (hi - lo) * 0.30, 0.004)
    ofun.AddPoint(lo + (hi - lo) * 0.60, 0.030)
    ofun.AddPoint(lo + (hi - lo) * 0.85, 0.10)
    ofun.AddPoint(hi, 0.16)
    prop = vtk.vtkVolumeProperty()
    prop.SetColor(ctf)
    prop.SetScalarOpacity(ofun)
    prop.ShadeOn()
    prop.SetInterpolationTypeToLinear()
    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(prop)
    ren.AddVolume(volume)

    # 等值面：火焰锋面 1100 K（橙）与高温核 1500 K（亮黄）
    for iso, color, op in ((1100.0, (0.95, 0.55, 0.15), 0.55), (1500.0, (1.0, 0.9, 0.35), 0.65)):
        cf = vtk.vtkContourFilter()
        cf.SetInputData(img)
        cf.SetValue(0, iso)
        cm = vtk.vtkPolyDataMapper()
        cm.SetInputConnection(cf.GetOutputPort())
        cm.ScalarVisibilityOff()
        ca = vtk.vtkActor()
        ca.SetMapper(cm)
        ca.GetProperty().SetColor(*color)
        ca.GetProperty().SetOpacity(op)
        ren.AddActor(ca)

    ren.GetActiveCamera().SetPosition(2.6, -2.3, 1.5)
    ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
    return _mk_rw(ren)


def build_volume_vector_scene():
    """构建三维矢量体采样场景。"""

    points, vectors = [], []
    for z in np.linspace(-0.7, 0.7, 5):
        for y in np.linspace(-0.8, 0.8, 6):
            for x in np.linspace(-1.1, 1.1, 8):
                points.append((x, y, z))
                vectors.append((0.9 + 0.15 * np.cos(np.pi * z), -0.42 * z, 0.42 * y))
    ren = vtk.vtkRenderer()
    ren.AddActor(_vector_glyph_actor(points, vectors, 0.11))
    camera = ren.GetActiveCamera()
    camera.SetPosition(3.2, -3.0, 2.2)
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)
    return _mk_rw(ren)


# ---------------------------------------------------------------- ENT 轨迹
def build_trajectory_scene():
    """构建羽流粒子三维轨迹场景。"""

    df = pd.read_parquet(os.path.join(DATA_DIR, VIEW_META["trajectory"]["file"]))
    # 渲染取 500 条、步长 2，兼顾观感与客户端负载
    keep = np.sort(np.random.default_rng(3).choice(df["particle_id"].unique(), 500, replace=False))
    df = df[df["particle_id"].isin(keep)]

    ren = vtk.vtkRenderer()
    pts = vtk.vtkPoints()
    cells = vtk.vtkCellArray()
    vel_vals = []
    off = 0
    for pid, grp in df.groupby("particle_id"):
        grp = grp.sort_values("frame")
        n = len(grp)
        for _, row in grp.iterrows():
            pts.InsertNextPoint(float(row["x"]), float(row["y"]), float(row["z"]))
            vel_vals.append(float(row["velocity"]))
        cell = vtk.vtkPolyLine()
        cell.GetPointIds().SetNumberOfIds(n)
        for k in range(n):
            cell.GetPointIds().SetId(k, off + k)
        cells.InsertNextCell(cell)
        off += n

    poly = vtk.vtkPolyData()
    poly.SetPoints(pts)
    poly.SetLines(cells)
    va = numpy_support.numpy_to_vtk(np.array(vel_vals, dtype=np.float32), deep=True)
    va.SetName("velocity")
    poly.GetPointData().SetScalars(va)

    vmax = float(df["velocity"].max())
    tube = vtk.vtkTubeFilter()
    tube.SetInputData(poly)
    # The plume spans roughly 115 engineering units.  The old 0.0035 radius
    # collapsed below one device pixel once the full dataset was fitted,
    # making the truthful fallback look empty.  Keep a thin but legible tube
    # at about 0.07% of the longitudinal range.
    tube.SetRadius(0.08)
    tube.SetNumberOfSides(5)

    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.62, 0.02)
    lut.SetRange(0.0, vmax)
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(0.0, vmax)
    mapper.SelectColorArray("velocity")
    mapper.SetScalarModeToUsePointFieldData()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren.AddActor(actor)

    # 喷口参考锥
    nozzle = vtk.vtkConeSource()
    nozzle.SetCenter(-0.05, 0.0, 0.0)
    nozzle.SetRadius(0.06)
    nozzle.SetHeight(0.16)
    nozzle.SetDirection(1.0, 0.0, 0.0)
    nozzle.SetResolution(24)
    nm = vtk.vtkPolyDataMapper()
    nm.SetInputConnection(nozzle.GetOutputPort())
    na = vtk.vtkActor()
    na.SetMapper(nm)
    na.GetProperty().SetColor(0.72, 0.76, 0.82)
    na.GetProperty().SetOpacity(0.85)
    ren.AddActor(na)

    camera = ren.GetActiveCamera()
    camera.SetPosition(55.0, -260.0, 120.0)
    camera.SetFocalPoint(55.0, 0.0, 0.0)
    camera.SetViewUp(0.0, 0.0, 1.0)
    ren.ResetCameraClippingRange()
    return _mk_rw(ren)


# ---------------------------------------------------------------- FLD 表面物理场
def build_field_scene():
    """构建非规则网格标量物理场场景。"""

    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(os.path.join(DATA_DIR, VIEW_META["field"]["file"]))
    reader.Update()

    surf = vtk.vtkDataSetSurfaceFilter()
    surf.SetInputConnection(reader.GetOutputPort())
    surf.Update()
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(surf.GetOutputPort())
    normals.SplittingOff()
    normals.Update()

    lo, hi = reader.GetOutput().GetScalarRange()
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetHueRange(0.66, 0.0)
    lut.SetRange(lo, hi)
    lut.Build()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(lo, hi)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetSpecular(0.25)
    actor.GetProperty().SetInterpolationToPhong()

    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    light = vtk.vtkLight()
    light.SetPosition(1.5, -2.0, 2.5)
    ren.AddLight(light)
    ren.GetActiveCamera().SetPosition(1.9, -1.8, 0.9)
    ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
    return _mk_rw(ren)


def build_field_vector_scene():
    """构建非规则网格矢量物理场场景。"""

    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(os.path.join(DATA_DIR, VIEW_META["field"]["file"]))
    reader.Update()
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputConnection(reader.GetOutputPort())
    surface.Update()
    poly = surface.GetOutput()

    base_mapper = vtk.vtkPolyDataMapper()
    base_mapper.SetInputData(poly)
    base_mapper.ScalarVisibilityOff()
    base_actor = vtk.vtkActor()
    base_actor.SetMapper(base_mapper)
    base_actor.GetProperty().SetColor(0.28, 0.32, 0.38)
    base_actor.GetProperty().SetOpacity(0.78)

    points, vectors = [], []
    step = max(1, poly.GetNumberOfPoints() // 220)
    for index in range(0, poly.GetNumberOfPoints(), step):
        x, y, z = poly.GetPoint(index)
        points.append((x, y, z))
        vectors.append((1.0, -0.32 * z, 0.18 * y))
    ren = vtk.vtkRenderer()
    ren.AddActor(base_actor)
    ren.AddActor(_vector_glyph_actor(points, vectors, 0.055))
    camera = ren.GetActiveCamera()
    camera.SetPosition(1.9, -1.8, 0.9)
    camera.SetFocalPoint(0.0, 0.0, 0.0)
    return _mk_rw(ren)


def build_miller_field_scene():
    """构建Miller曲面时序标量场场景。"""

    """Build the temporal Miller field and retain all frames for animation."""

    return MillerFieldAnimation(os.path.join(DATA_DIR, VIEW_META["miller_field"]["file"]))


