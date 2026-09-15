"""AI4E VizReport 后端 — 样例数据生成器（与前端声明的 Artifact 完全对齐）

每个文件与 mockData.js 中声明的 Artifact 一一对应（名实相符）：
  A-1024  PLT · table       -> cfd_wing_pressure_surface.csv   机翼表面压力分布（大表格）
  A-1025  PLT · series      -> wind_tunnel_ts_pitot.csv        皮托管 9 通道时序
  A-1026  PLT · tensor      -> stress_tensor_cycle118.npz      应力张量切片
  A-1027  GEO · mesh        -> turbine_blade_mesh.vtu          涡轮叶片网格 + 压力场（VTU 非结构网格）
  A-1028  FLD · volume      -> combustor_temp_volume.vti       燃烧室温度体数据（VTI）
  A-1029  ENT · trajectory  -> particle_traj_plume.parquet     羽流粒子轨迹（Parquet）
  A-1030  FLD?->GEO · mesh  -> heater_plate_field.stl          加热板表面（声明为场，实为纯几何 → 校验阻断样例）
  A-1031  GEO · mesh        -> wing_surface_geometry.ply       机翼表面几何（PLY，Online3DViewer）
  A-1032  PLT · table       -> simulation_log_raw.csv          仿真运行日志（列型混杂，未命中规则样例）
  A-1033  GEO · mesh        -> nozzle_geometry.obj             拉瓦尔喷管几何（OBJ，Online3DViewer）

所有文件写入 resources/examples/，由解析服务、Trame/vtk.js 与浏览器端渲染器加载。
"""

from __future__ import annotations

import os

import numpy as np

REPOSITORY_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPOSITORY_ROOT, "resources", "examples")


def ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def path(name: str) -> str:
    return os.path.join(DATA_DIR, name)


def asset_path(name: str) -> str:
    directory = os.path.join(DATA_DIR, "assets")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, name)


# ================================================================ A-1024 表格
def write_wing_pressure_csv(n_rows: int = 150_000, seed: int = 7) -> str:
    """机翼表面压力分布（CFD）：14 列 × 15 万行的大表格，触发流式渲染规则。"""
    import pandas as pd

    rng = np.random.default_rng(seed)
    n_span, n_chord = 60, 125  # 60*125*2*10 = 150000
    span = np.linspace(-1.0, 1.0, n_span)
    chord = np.linspace(0.0, 1.0, n_chord)
    zs, xc = np.meshgrid(span, chord, indexing="ij")
    zs, xc = zs.ravel(), xc.ravel()

    rows_per_surf = len(zs)
    reps = n_rows // (rows_per_surf * 2)
    parts = []
    for r in range(max(1, reps)):
        for side, sgn in (("upper", -1.0), ("lower", 1.0)):
            twist = 1.6 * zs
            peak = -3.1 * np.exp(-xc / 0.07)
            shock = 0.85 / (1.0 + np.exp(-(xc - (0.60 + 0.05 * twist)) / 0.02))
            base = 1.0 - 1.02 * np.sqrt(np.clip(1.0 - xc, 0, None))
            cp = (
                sgn * np.abs(peak) * (0.55 + 0.45 * np.cos(np.pi * xc) ** 2)
                + shock * (1.0 if side == "upper" else 0.32)
                + base * 0.12
                + rng.normal(0.0, 0.03, xc.shape)
            )
            pressure = 101.325 * (1.0 - cp * 0.142)
            mach = np.clip(0.78 + 0.32 * np.sqrt(np.clip(-cp, 0, None)) + rng.normal(0, 0.006, xc.shape), 0.2, 1.42)
            shear = 18.5 * np.exp(-xc / 0.35) + rng.normal(0, 0.8, xc.shape)
            temp = 288.15 * (1.0 + 0.2 * 0.78**2 * (1 - cp * 0.12))
            rho = pressure * 1000.0 / (287.05 * temp)
            vel = mach * np.sqrt(1.4 * 287.05 * temp)
            zone = np.where(zs < -0.33, 1, np.where(zs < 0.33, 2, 3))
            df = pd.DataFrame(
                {
                    "point_id": np.arange(len(xc)) + r * rows_per_surf * 2,
                    "zone_id": zone.astype(np.int32),
                    "x_over_c": np.round(xc, 5),
                    "y_mm": np.round(zs * 610.0, 3),
                    "z_mm": np.round(rng.normal(0, 0.02, xc.shape), 4),
                    "side": side,
                    "cp": np.round(cp, 4),
                    "pressure_kpa": np.round(pressure, 3),
                    "shear_pa": np.round(shear, 3),
                    "mach_local": np.round(mach, 4),
                    "temp_k": np.round(temp, 2),
                    "rho_kg_m3": np.round(rho, 4),
                    "vel_m_s": np.round(vel, 2),
                    "residual_id": rng.integers(0, 999999, xc.shape),
                }
            )
            parts.append(df)
    out = pd.concat(parts, ignore_index=True).head(n_rows)
    fp = path("cfd_wing_pressure_surface.csv")
    out.to_csv(fp, index=False)
    return fp


# ================================================================ A-1025 时序
def make_pitot_ts(n_pts: int = 6000, dt: float = 5e-4, seed: int = 11):
    """9 通道皮托管/静压/温度/振动时序，含 0.36–0.39s 采样缺口与 261 个重复时间戳。"""
    rng = np.random.default_rng(seed)
    t = np.arange(n_pts) * dt
    gap = (t > 0.36) & (t < 0.39)
    t = t[~gap]

    def chan(base, amp, f0, noise, phase=0.0):
        s = base + amp * np.sin(2 * np.pi * f0 * t + phase) + 0.35 * amp * np.sin(2 * np.pi * f0 * 3.17 * t)
        return s + rng.normal(0, noise, t.shape)

    p1 = chan(112.4, 6.2, 38.0, 0.42)
    p2 = chan(111.9, 5.8, 38.0, 0.40, 0.6)
    p3 = chan(112.1, 6.0, 37.2, 0.41, 1.1)
    p4 = chan(109.7, 4.1, 36.5, 0.55, 1.9)
    p4[rng.random(t.shape) < 0.34] = np.nan
    ps = chan(98.6, 0.8, 12.0, 0.08)
    t1 = chan(301.4, 0.9, 4.0, 0.05)
    vx = chan(0.0, 2.4, 92.0, 0.9)
    vy = chan(0.0, 1.8, 84.0, 0.8, 0.4)
    vz = chan(0.0, 1.2, 71.0, 0.7, 0.9)

    dup_idx = rng.choice(np.arange(10, len(t) - 1), 261, replace=False)
    t_out = t.copy()
    t_out[dup_idx] = t_out[dup_idx - 1]
    return np.column_stack([t_out, p1, p2, p3, p4, ps, t1, vx, vy, vz])


def write_pitot_ts() -> str:
    cols = make_pitot_ts()
    fp = path("wind_tunnel_ts_pitot.csv")
    header = "time,pitot_p1,pitot_p2,pitot_p3,pitot_p4,static_p,temp_t1,vib_acc_x,vib_acc_y,vib_acc_z"
    with open(fp, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for r in cols:
            f.write(",".join("nan" if np.isnan(v) else f"{v:.6g}" for v in r) + "\n")
    return fp


# ================================================================ A-1026 张量
def make_stress_tensor(h: int = 512, w: int = 512, seed: int = 23):
    """3 × 512 × 512 应力张量（σxx, σxy, σyy），带孔边应力集中（Kirsch 解）。"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = xx / w - 0.5
    yy = yy / h - 0.5
    r = np.sqrt(xx**2 + yy**2) + 1e-6
    theta = np.arctan2(yy, xx)
    far, a = 240.0, 0.08
    k = (a / np.clip(r, a, None)) ** 2
    sxx = far * (1 - k * (1.5 * np.cos(2 * theta) - np.cos(4 * theta)) + 0.5 * k**2 * np.cos(4 * theta))
    syy = far * (-k * (0.5 * np.cos(2 * theta) + np.cos(4 * theta)) + 0.5 * k**2 * np.cos(4 * theta)) + far * 0.32
    sxy = far * (-0.5 * k * np.sin(2 * theta) + 0.5 * k**2 * np.sin(4 * theta))
    noise = rng.normal(0, 2.2, (3, h, w)).astype(np.float32)
    return np.stack([sxx, sxy, syy]).astype(np.float32) + noise


def write_stress_tensor() -> str:
    tens = make_stress_tensor()
    fp = path("stress_tensor_cycle118.npz")
    np.savez_compressed(fp, stress=tens, channels=np.array(["sigma_xx", "sigma_xy", "sigma_yy"]), units="MPa", cycle=118)
    return fp


# ================================================================ A-1027 网格（VTU）
def naca4(cx, camber: float = 0.035, thick: float = 0.055):
    xt = 0.6 * thick * (0.2969 * np.sqrt(cx) - 0.126 * cx - 0.3516 * cx**2 + 0.2843 * cx**3 - 0.1036 * cx**4)
    yc = camber * (2 * cx - cx**2)
    return yc, xt


def make_blade_rings(n_chord: int = 160, n_span: int = 96):
    """涡轮叶片：NACA 剖面沿展向带扭转/收缩。"""
    rings = []
    for j in range(n_span):
        s = j / (n_span - 1)
        z = (s - 0.5) * 1.1
        twist = np.deg2rad(-28.0 * s + 10.0)
        scale = 0.72 + 0.28 * np.cos(np.pi * (s - 0.5))
        ring = []
        for i in range(n_chord):
            cx = i / (n_chord - 1)
            yc, xt = naca4(cx)
            for half in (1.0, -1.0):
                px = cx - 0.35
                py = yc + half * xt
                rx = px * np.cos(twist) - py * np.sin(twist)
                ry = px * np.sin(twist) + py * np.cos(twist)
                ring.append((rx * scale, ry * scale, z))
        rings.append(ring)
    return np.array(rings, dtype=np.float32), n_chord


def write_blade_vtu() -> str:
    """涡轮叶片网格 + 压力场，写出为 .vtu（vtkUnstructuredGrid，三角单元）。"""
    import vtk
    from vtk.util import numpy_support

    rings, n_chord = make_blade_rings()
    n_span = rings.shape[0]
    m = 2 * n_chord
    n_pts = n_span * m

    pts_arr = rings.reshape(n_pts, 3)
    # 伪压力标量：前缘高压、上表面吸力
    scalars = np.zeros(n_pts, dtype=np.float32)
    idx = 0
    for j in range(n_span):
        for i in range(n_chord):
            cx = i / (n_chord - 1)
            stag = 1.4 * np.exp(-(((cx - 0.02) ** 2) / 0.004))
            for half in (1.0, -1.0):
                suct = -1.9 * np.exp(-(((cx - 0.22) ** 2) / 0.02)) if half > 0 else 0.35 * np.exp(-(((cx - 0.3) ** 2) / 0.05))
                scalars[idx] = 0.2 + stag + suct + 0.15 * np.sin(np.pi * rings[j, 0, 2] + cx * 3)
                idx += 1

    # 三角单元连接关系
    conn = []
    for j in range(n_span - 1):
        for i in range(m):
            i2 = (i + 1) % m
            a, b = j * m + i, j * m + i2
            c, d = (j + 1) * m + i2, (j + 1) * m + i
            conn.append((a, b, c))
            conn.append((a, c, d))
    conn = np.array(conn, dtype=np.int64)
    n_cells = len(conn)

    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(np.ascontiguousarray(pts_arr), deep=True, array_type=vtk.VTK_FLOAT))

    cells = vtk.vtkCellArray()
    offsets = numpy_support.numpy_to_vtk(np.arange(0, (n_cells + 1) * 3, 3, dtype=np.int64), deep=True)
    conn_arr = numpy_support.numpy_to_vtk(conn.ravel().astype(np.int64), deep=True)
    cells.SetData(offsets, conn_arr)

    ug = vtk.vtkUnstructuredGrid()
    ug.SetPoints(points)
    ug.SetCells(vtk.VTK_TRIANGLE, cells)
    sa = numpy_support.numpy_to_vtk(scalars, deep=True)
    sa.SetName("pressure")
    ug.GetPointData().SetScalars(sa)
    ug.GetPointData().AddArray(numpy_support.numpy_to_vtk((scalars * 101.325).astype(np.float32), deep=True))
    ug.GetPointData().GetArray(1).SetName("pressure_kpa")

    fp = path("turbine_blade_mesh.vtu")
    w = vtk.vtkXMLUnstructuredGridWriter()
    w.SetFileName(fp)
    w.SetInputData(ug)
    w.SetDataModeToBinary()
    w.Write()
    return fp


# ================================================================ A-1028 体数据（燃烧室温度）
def make_combustor_volume(nx: int = 144, ny: int = 112, nz: int = 96, seed: int = 31):
    """燃烧室温度场（K）：中心燃烧核高温、向壁面递减、带火焰锋面皱褶。"""
    rng = np.random.default_rng(seed)
    z, y, x = np.mgrid[0:nz, 0:ny, 0:nx].astype(np.float32)
    x = x / nx
    y = y / ny - 0.5
    z = z / nz - 0.5

    # 轴向（x）燃烧：入口低温 → 中部燃烧核 → 出口高温掺混
    axial = 300.0 + 1500.0 / (1.0 + np.exp(-(x - 0.32) / 0.09))
    # 径向：中心热、壁面冷
    rr = np.sqrt((y / 0.5) ** 2 + (z / 0.5) ** 2)
    radial = np.exp(-(rr**2) * 1.4)
    # 火焰锋面皱褶（湍流）
    wrinkle = 0.16 * np.sin(9 * x + 5 * y) * np.cos(7 * z + 4 * x) + 0.1 * np.sin(15 * x + 11 * z)
    core = axial * (0.35 + 0.65 * radial) * (1.0 + wrinkle * radial)
    # 壁面冷却层
    wall = 320.0 * (1.0 - np.exp(-((rr - 0.95) ** 2) / 0.01))
    temp = np.clip(core + wall * (1 - radial), 300.0, 1900.0)
    temp += rng.normal(0, 8.0, temp.shape).astype(np.float32)
    return temp.astype(np.float32)


def write_combustor_vti() -> str:
    """燃烧室温度体数据写出为 .vti（vtkImageData，标量名 temperature，单位 K）。"""
    import vtk
    from vtk.util import numpy_support

    vol = make_combustor_volume()
    nz, ny, nx = vol.shape
    img = vtk.vtkImageData()
    img.SetDimensions(nx, ny, nz)
    img.SetSpacing(0.6 / nx * 4.0, 0.4 / ny * 4.0, 0.4 / nz * 4.0)  # ~燃烧室尺寸 400×400×400 mm 缩放
    img.SetOrigin(-0.0, -0.8, -0.8)
    arr = numpy_support.numpy_to_vtk(np.ascontiguousarray(vol.ravel()), deep=True, array_type=vtk.VTK_FLOAT)
    arr.SetName("temperature")
    img.GetPointData().SetScalars(arr)

    fp = path("combustor_temp_volume.vti")
    w = vtk.vtkXMLImageDataWriter()
    w.SetFileName(fp)
    w.SetInputData(img)
    w.SetDataModeToBinary()
    w.Write()
    return fp


# ================================================================ A-1029 轨迹（Parquet 羽流）
def make_plume_trajectories(n_particles: int = 900, n_steps: int = 160, seed: int = 41):
    """羽流：从喷口（原点）沿 +x 膨胀扩散，速度衰减、温度冷却、湍流抖动。"""
    rng = np.random.default_rng(seed)
    rec = []
    for pid in range(n_particles):
        # 喷口出射角（锥形）
        theta = rng.uniform(0, 2 * np.pi)
        spread0 = rng.rayleigh(0.12)
        v0 = rng.uniform(280.0, 620.0)  # m/s
        T0 = rng.uniform(900.0, 1500.0)
        x = y = z = 0.0
        vy = np.sin(theta) * spread0
        vz = np.cos(theta) * spread0
        for s in range(n_steps):
            frac = s / n_steps
            vel = v0 * (1.0 - 0.55 * frac) + rng.normal(0, 2.0)
            temp = T0 * (1.0 - 0.6 * frac) + 300.0 * (0.6 * frac)
            rec.append((pid, s, x, y, z, max(vel, 5.0), temp))
            dx = vel * 0.0016
            y += vy * dx * 1.9 + rng.normal(0, 0.0018)
            z += vz * dx * 1.9 + rng.normal(0, 0.0018)
            x += dx
    return np.array(rec, dtype=np.float32)


def write_plume_parquet() -> str:
    """羽流轨迹写出为 Parquet（particle_id / frame / x / y / z / velocity / temperature）。"""
    import pandas as pd

    arr = make_plume_trajectories()
    df = pd.DataFrame(
        {
            "particle_id": arr[:, 0].astype(np.int32),
            "frame": arr[:, 1].astype(np.int32),
            "x": np.round(arr[:, 2], 5),
            "y": np.round(arr[:, 3], 5),
            "z": np.round(arr[:, 4], 5),
            "velocity": np.round(arr[:, 5], 2),
            "temperature": np.round(arr[:, 6], 1),
        }
    )
    fp = path("particle_traj_plume.parquet")
    df.to_parquet(fp, index=False)
    return fp


# ================================================================ A-1030 STL（纯几何，声明为场 → 阻断样例）
def write_heater_plate_stl() -> str:
    """加热板表面（带肋）纯几何 STL —— 无任何场数据，用于名实不符校验演示。"""
    import vtk

    plate = vtk.vtkCubeSource()
    plate.SetXLength(2.0)
    plate.SetYLength(0.06)
    plate.SetZLength(1.2)
    plate.SetCenter(0.0, 0.0, 0.0)

    app = vtk.vtkAppendPolyData()
    app.AddInputConnection(plate.GetOutputPort())
    # 加热肋
    for i in range(6):
        rib = vtk.vtkCubeSource()
        rib.SetXLength(0.06)
        rib.SetYLength(0.05)
        rib.SetZLength(1.1)
        rib.SetCenter(-0.8 + i * 0.32, 0.055, 0.0)
        app.AddInputConnection(rib.GetOutputPort())
    app.Update()

    tri = vtk.vtkTriangleFilter()
    tri.SetInputConnection(app.GetOutputPort())
    tri.Update()

    fp = path("heater_plate_field.stl")
    w = vtk.vtkSTLWriter()
    w.SetFileName(fp)
    w.SetInputConnection(tri.GetOutputPort())
    w.SetFileTypeToBinary()
    w.Write()
    return fp


# ================================================================ A-1032 日志（列型混杂，未命中规则样例）
def write_sim_log_csv(n_rows: int = 41_207, seed: int = 53) -> str:
    """仿真运行日志：23 列，字符串/整数/浮点混杂，无合法时间列与明确分类+数值结构。"""
    import pandas as pd

    rng = np.random.default_rng(seed)
    levels = ["INFO", "WARN", "DEBUG", "ERROR", "TRACE"]
    modules = ["solver", "mesh", "io", "turb", "chem", "bc", "post", "alloc"]
    df = pd.DataFrame(
        {
            "seq": np.arange(n_rows, dtype=np.int64),
            "session": rng.choice(["sess-A", "sess-B", "sess-C", "sess-D"], n_rows),
            "level": rng.choice(levels, n_rows, p=[0.5, 0.18, 0.2, 0.07, 0.05]),
            "module": rng.choice(modules, n_rows),
            "msg_code": rng.integers(1000, 9999, n_rows),
            "iter": rng.integers(0, 5000, n_rows),
            "elapsed_raw": rng.exponential(12.0, n_rows).round(3),
            "resid_cont": rng.exponential(1e-3, n_rows),
            "resid_mom": rng.exponential(1e-3, n_rows),
            "resid_energy": rng.exponential(1e-4, n_rows),
            "cells_k": rng.integers(800, 4200, n_rows),
            "mem_mb": rng.integers(512, 32768, n_rows),
            "cpu_pct": rng.uniform(12, 99, n_rows).round(1),
            "gpu_util": rng.uniform(0, 100, n_rows).round(1),
            "node_id": rng.integers(1, 48, n_rows),
            "rank": rng.integers(0, 256, n_rows),
            "thread": rng.integers(0, 64, n_rows),
            "queue_depth": rng.integers(0, 64, n_rows),
            "retry": rng.integers(0, 4, n_rows),
            "flag": rng.integers(0, 2, n_rows),
            "checksum": [f"{rng.integers(0, 16**8):08x}" for _ in range(n_rows)],
            "note": rng.choice(["ok", "stall", "retry", "skip", "clamp", ""], n_rows),
            "free_text": [f"step {i} {rng.choice(['conv','div','hold','flux'])}" for i in range(n_rows)],
        }
    )
    fp = path("simulation_log_raw.csv")
    df.to_csv(fp, index=False)
    return fp


# ================================================================ A-1031 机翼几何（PLY，供 Online3DViewer）
def make_wing_surface(n_chord: int = 60, n_span: int = 24):
    """机翼表面：NACA 剖面沿展向带后掠/扭转/收缩，纯几何（无场变量）。"""
    rings = []
    for j in range(n_span):
        s = j / (n_span - 1)
        y = s * 8.0                       # 展向 0–8 m
        chord = 1.6 * (1.0 - 0.6 * s)     # 梢根比 0.4
        x_off = 0.45 * s * 1.6            # 前缘后掠
        twist = np.deg2rad(-3.0 * s)      # 梢部洗出 -3°
        ring = []
        for i in range(n_chord):
            cx = i / (n_chord - 1)
            yc, xt = naca4(cx, camber=0.02, thick=0.55)
            for half in (1.0, -1.0):
                xi = (cx - 0.25) * chord
                eta = (yc + half * xt) * chord
                px = xi * np.cos(twist) - eta * np.sin(twist)
                pz = xi * np.sin(twist) + eta * np.cos(twist)
                ring.append((px + x_off, pz, y))  # x 流向 · y 上 · z 展向（匹配查看器 Y-up）
        rings.append(ring)
    return np.array(rings, dtype=np.float32), n_chord


def write_wing_ply() -> str:
    """机翼表面几何 → ASCII PLY（vtkPLYReader 兼容，供 Online3DViewer 加载）。"""
    rings, n_chord = make_wing_surface()
    n_span = rings.shape[0]
    m = 2 * n_chord
    n_pts = n_span * m

    # 三角单元连接关系（同 blade_rings 的环形拓扑）
    conn = []
    for j in range(n_span - 1):
        for i in range(m):
            i2 = (i + 1) % m
            a, b = j * m + i, j * m + i2
            c, d = (j + 1) * m + i2, (j + 1) * m + i
            conn.append((a, b, c))
            conn.append((a, c, d))
    n_faces = len(conn)

    fp = path("wing_surface_geometry.ply")
    with open(fp, "w") as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write("comment AI4E VizReport sample: wing surface geometry (GEO · mesh, pure geometry)\n")
        f.write(f"element vertex {n_pts}\n")
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write(f"element face {n_faces}\n")
        f.write("property list uchar int vertex_indices\n")
        f.write("end_header\n")
        for j in range(n_span):
            for i in range(m):
                x, y, z = rings[j, i]
                f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
        for a, b, c in conn:
            f.write(f"3 {a} {b} {c}\n")
    return fp


# ================================================================ A-1033 喷管几何（OBJ，供 Online3DViewer）
def make_nozzle(n_ax: int = 40, n_circ: int = 48):
    """拉瓦尔喷管：收敛-扩张型面（轴对称），纯几何。返回 (rings, r_in, r_th, r_out)。"""
    rings = []
    for j in range(n_ax):
        x = j / (n_ax - 1) * 2.4          # 轴向 0–2.4 m
        if x < 0.84:                       # 收敛段：0.62 → 0.22
            t = x / 0.84
            r = 0.62 - 0.40 * (3 * t**2 - 2 * t**3)
        else:                              # 扩张段：0.22 → 0.86（Bell 型）
            t = (x - 0.84) / (2.4 - 0.84)
            r = 0.22 + 0.64 * (1 - np.exp(-t * 2.6))
        ring = []
        for k in range(n_circ):
            th = 2 * np.pi * k / n_circ
            ring.append((r * np.cos(th), r * np.sin(th), x))
        rings.append(ring)
    return np.array(rings, dtype=np.float32), n_circ


def write_nozzle_obj() -> str:
    """拉瓦尔喷管 → Wavefront OBJ（四边形管壁 + 两端三角封盖）。"""
    rings, m = make_nozzle()
    n_ax = rings.shape[0]
    n_pts = n_ax * m
    v_in = n_pts        # 入口中心点
    v_out = n_pts + 1   # 出口中心点

    fp = path("nozzle_geometry.obj")
    with open(fp, "w") as f:
        f.write("# AI4E VizReport sample: CD nozzle geometry (GEO · mesh, pure geometry)\n")
        for j in range(n_ax):
            for k in range(m):
                x, y, z = rings[j, k]
                f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        f.write(f"v 0.000000 0.000000 {rings[0, 0, 2]:.6f}\n")   # 入口中心
        f.write(f"v 0.000000 0.000000 {rings[-1, 0, 2]:.6f}\n")  # 出口中心
        for j in range(n_ax - 1):
            for k in range(m):
                k2 = (k + 1) % m
                a = j * m + k + 1
                b = j * m + k2 + 1
                c = (j + 1) * m + k2 + 1
                d = (j + 1) * m + k + 1
                f.write(f"f {a} {b} {c} {d}\n")
        for k in range(m):  # 入口封盖（三角扇）
            k2 = (k + 1) % m
            f.write(f"f {v_in + 1} {k2 + 1} {k + 1}\n")
        for k in range(m):  # 出口封盖（三角扇，反向）
            k2 = (k + 1) % m
            f.write(f"f {v_out + 1} {(n_ax - 1) * m + k + 1} {(n_ax - 1) * m + k2 + 1}\n")
    return fp


# ================================================================ A-1112 / A-1113 报告媒体资产
def _temperature_frame(width: int, height: int, phase: float = 0.0):
    """Create an evidence-bearing synthetic temperature field frame."""
    from PIL import Image, ImageDraw

    yy, xx = np.mgrid[0:height, 0:width]
    xn = xx / width
    yn = yy / height
    center = 0.48 + 0.03 * np.sin(phase)
    core = np.exp(-((xn - 0.42 - 0.08 * np.sin(phase * 0.6)) ** 2 / 0.075 + (yn - center) ** 2 / 0.035))
    wake = np.exp(-((xn - 0.72) ** 2 / 0.16 + (yn - center) ** 2 / (0.055 + 0.025 * xn)))
    field = np.clip(0.12 + 0.72 * core + 0.34 * wake, 0, 1)
    stops = np.array([[20, 38, 92], [28, 112, 171], [20, 157, 137], [239, 187, 63], [225, 74, 43]], dtype=float)
    scaled = field * (len(stops) - 1)
    low = np.floor(scaled).astype(int)
    high = np.clip(low + 1, 0, len(stops) - 1)
    mix = (scaled - low)[..., None]
    rgb = (stops[low] * (1 - mix) + stops[high] * mix).astype(np.uint8)
    image = Image.fromarray(rgb, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((18, 18, 290, 68), fill=(10, 18, 34, 186), outline=(255, 255, 255, 45))
    draw.text((32, 29), "COMBUSTOR TEMPERATURE  |  K", fill=(245, 248, 252, 235))
    draw.text((32, 48), "Fixed camera · section z=0.50", fill=(210, 220, 232, 190))
    for index, label in enumerate(("720", "980", "1240", "1500", "1760")):
        x0 = 32 + index * 55
        draw.rectangle((x0, height - 42, x0 + 52, height - 29), fill=tuple(stops[index].astype(int)) + (255,))
        draw.text((x0, height - 25), label, fill=(250, 250, 250, 220))
    return image


def write_report_assets() -> list[str]:
    import imageio.v2 as imageio

    poster = asset_path("temperature_fixed_camera.png")
    _temperature_frame(960, 540).save(poster, format="PNG", optimize=True)

    video = asset_path("plume_evolution_silent.mp4")
    writer = imageio.get_writer(video, fps=12, codec="libx264", pixelformat="yuv420p", macro_block_size=16)
    try:
        for index in range(48):
            writer.append_data(np.asarray(_temperature_frame(640, 368, index / 8), dtype=np.uint8))
    finally:
        writer.close()
    return [poster, video]


# ================================================================ 汇总
def generate_all() -> dict:
    ensure_dir()
    results = {}
    results["A-1024 plt_table"] = write_wing_pressure_csv()
    results["A-1025 plt_series"] = write_pitot_ts()
    results["A-1026 plt_tensor"] = write_stress_tensor()
    results["A-1027 geo_mesh_vtu"] = write_blade_vtu()
    results["A-1028 fld_volume_vti"] = write_combustor_vti()
    results["A-1029 ent_traj_parquet"] = write_plume_parquet()
    results["A-1030 geo_stl"] = write_heater_plate_stl()
    results["A-1031 geo_ply"] = write_wing_ply()
    results["A-1032 plt_log"] = write_sim_log_csv()
    results["A-1033 geo_obj"] = write_nozzle_obj()
    for index, media_path in enumerate(write_report_assets(), 1):
        results[f"A-111{index + 1} asset"] = media_path
    return results


if __name__ == "__main__":
    for kind, fp in generate_all().items():
        size = os.path.getsize(fp)
        print(f"[ok] {kind:<24} -> {os.path.basename(fp):<34} {size/1024:>10.1f} KB")
