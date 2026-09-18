"""明确的相机与显示设置，不持有 Web 会话或全局主题。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


def configure_camera(
    plotter: Any,
    camera: Any = "isometric",
    *,
    normal: Any = None,
    projection: str = "parallel",
    zoom: float = 1.0,
) -> dict:
    """设置标准或自定义视角，返回实际相机及投影以便复现。"""
    if projection not in {"parallel", "perspective"} or not np.isfinite(zoom) or zoom <= 0:
        raise ValueError("非法投影或缩放")
    if isinstance(camera, Mapping):
        values = [camera[k] for k in ("position", "focal_point", "view_up")]
        if np.asarray(values).shape != (3, 3) or not np.isfinite(values).all():
            raise ValueError("相机参数必须为有限三维坐标")
        if not np.linalg.norm(np.subtract(values[0], values[1])) or not np.linalg.norm(values[2]):
            raise ValueError("相机位置和焦点不能重合，朝上方向不能为零")
        if not np.linalg.norm(np.cross(np.subtract(values[0], values[1]), values[2])):
            raise ValueError("相机朝上方向不能平行于观察方向")
        plotter.camera_position = values
    elif camera == "normal":
        if normal is None:
            raise ValueError("法向视角需要切面法向")
        plotter.view_vector(normal)
    else:
        methods = {
            "isometric": plotter.view_isometric,
            "xy": plotter.view_xy,
            "xz": plotter.view_xz,
            "yz": plotter.view_yz,
            "yx": plotter.view_yx,
            "zx": plotter.view_zx,
            "zy": plotter.view_zy,
        }
        if camera not in methods:
            raise ValueError("未知标准视角")
        methods[camera]()
    plotter.enable_parallel_projection() if projection == "parallel" else plotter.disable_parallel_projection()
    plotter.camera.zoom(zoom)
    return {
        "position": list(plotter.camera.position),
        "focal_point": list(plotter.camera.focal_point),
        "view_up": list(plotter.camera.up),
        "projection": projection,
        "parallel_scale": float(plotter.camera.parallel_scale),
        "view_angle": float(plotter.camera.view_angle),
        "zoom": zoom,
    }
