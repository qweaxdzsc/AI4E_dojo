"""AI4E VizReport — 可视化后端统一启动编排

一条命令同时拉起：
  trame  3D 服务   -> http://127.0.0.1:8090   （FLD 栅格/体/场 / ENT 点集/轨迹）
  API    解析/推荐 -> http://127.0.0.1:8091   （格式解析 / 可视化推荐 / 文件上传）

用法：
  backend/.venv/bin/python backend/run.py          # 先按需生成样例数据，再启动服务
  backend/.venv/bin/python backend/run.py --regen  # 强制重新生成样例数据

Ctrl+C 同时停止全部子进程。
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRAME_PORT = 8090
API_PORT = 8091


def banner(msg: str):
    print(f"\n\033[36m[run]\033[0m {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="AI4E VizReport 可视化后端编排")
    parser.add_argument("--regen", action="store_true", help="强制重新生成样例数据")
    parser.add_argument("--trame-port", type=int, default=TRAME_PORT)
    parser.add_argument("--api-port", type=int, default=API_PORT)
    args = parser.parse_args()

    sys.path.insert(0, HERE)
    from scripts.generate_example_data import DATA_DIR, generate_all
    from modules.reportManage.quarto import quarto_health

    need = [
        "cfd_wing_pressure_surface.csv",   # A-1024 PLT · table
        "wind_tunnel_ts_pitot.csv",        # A-1025 PLT · series
        "stress_tensor_cycle118.npz",      # A-1026 PLT · tensor
        "turbine_blade_mesh.vtu",          # A-1027 GEO · mesh
        "combustor_temp_volume.vti",       # A-1028 FLD · volume
        "particle_traj_plume.parquet",     # A-1029 ENT · trajectory
        "heater_plate_field.stl",          # A-1030 GEO（声明为场 → 阻断示例）
        "wing_surface_geometry.ply",       # A-1031 GEO · mesh（Online3DViewer）
        "simulation_log_raw.csv",          # A-1032 未整理表格（兜底示例）
        "nozzle_geometry.obj",             # A-1033 GEO · mesh（Online3DViewer）
    ]
    if args.regen or not all(os.path.exists(os.path.join(DATA_DIR, f)) for f in need):
        banner("生成样例数据（与前端声明一一对应 × 10）…")
        for kind, fp in generate_all().items():
            banner(f"  {kind:<22} -> {os.path.basename(fp)}  ({os.path.getsize(fp)/1024:.1f} KB)")
    else:
        banner(f"样例数据已存在（{DATA_DIR}），跳过生成；如需重建请加 --regen")

    py = sys.executable
    services = [
        {
            "name": "trame",
            "required": False,
            "process": subprocess.Popen(
                [py, "-m", "modules.visPhysField.trameServer", "--port", str(args.trame_port)], cwd=HERE
            ),
        },
        {
            "name": "api",
            "required": True,
            "process": subprocess.Popen(
                [py, "-m", "server.api", "--port", str(args.api_port)], cwd=HERE
            ),
        },
    ]

    banner(
        f"trame  -> http://127.0.0.1:{args.trame_port}/"
        "?view=raster|raster_vector|volume|volume_vector|field|field_vector|miller_field|points|trajectory"
    )
    banner(f"API    -> http://127.0.0.1:{args.api_port}/api/health | /api/upload")
    export_health = quarto_health()
    banner(f"Quarto -> {export_health['state']} · required {export_health['required_version']} · {export_health['message']}")
    banner("Ctrl+C 停止全部服务")

    def shutdown(*_):
        banner("正在停止子进程…")
        for service in services:
            p = service["process"]
            if p.poll() is None:
                p.terminate()
        time.sleep(1.0)
        for service in services:
            p = service["process"]
            if p.poll() is None:
                p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # API 是核心服务；Trame 是可降级 renderer。Trame 异常时保留 API，
    # 让前端仍可读取冻结 Spec、同源静态证据并显示明确的 offline 状态。
    reported_exits: set[str] = set()
    while True:
        for service in services:
            name = service["name"]
            p = service["process"]
            code = p.poll()
            if code is None or name in reported_exits:
                continue
            reported_exits.add(name)
            if service["required"]:
                banner(f"核心服务 {name} 退出（code={code}），停止其余服务")
                shutdown()
            banner(f"可选服务 {name} 退出（code={code}）；API 保持运行，前端将使用同源静态降级")
        time.sleep(1.0)


if __name__ == "__main__":
    main()
