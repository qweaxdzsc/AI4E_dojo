"""离屏物理场与曲线绘制，返回像素且不写文件。"""

from __future__ import annotations

from typing import Any

import numpy as np

from .display import configure_camera
from .fields import pyvista, scalar_mesh


def render_field(
    mesh: Any,
    *,
    field: str,
    association: str = "point",
    component: str | int = "scalar",
    camera: Any = "isometric",
    normal: Any = None,
    cmap: Any = "viridis",
    clim: Any = None,
    n_colors: int = 256,
    size: Any = (1600, 1000),
    opacity: float = 1.0,
    style: Any = "surface",
    show_edges: bool = False,
    axes: bool = True,
    background: Any = "white",
    title: str | None = None,
    unit: str | None = None,
    projection: str = "parallel",
    zoom: float = 1.0,
    plotter: Any = None,
    metadata: dict | None = None,
) -> Any:
    """生成 RGB 图片；传入 Plotter 时仅添加对象，由调用者负责窗口释放。"""
    if len(size) != 2 or any(
        isinstance(x, bool) or int(x) != x or not 64 <= x <= 8192 for x in size
    ):
        raise ValueError("图片尺寸须为 64 到 8192 的整数")
    if (
        style not in {"surface", "wireframe", "points"}
        or not 0 <= opacity <= 1
        or not 2 <= n_colors <= 4096
    ):
        raise ValueError("非法显示参数")
    source = scalar_mesh(mesh, field, association=association, component=component)
    attrs = source.point_data if association == "point" else source.cell_data
    values = attrs["__post_scalar"]
    limits = [float(values.min()), float(values.max())] if clim is None else list(clim)
    if len(limits) != 2 or not np.isfinite(limits).all() or limits[0] > limits[1]:
        raise ValueError("颜色范围必须有限且递增")
    if limits[0] == limits[1]:
        limits[1] += max(abs(limits[0]) * 1e-9, 1e-12)
    owned = plotter is None
    plot = pyvista().Plotter(off_screen=True, window_size=size) if owned else plotter
    try:
        plot.set_background(background)
        label = title or field
        if unit:
            label += f" [{unit}]"
        actor = plot.add_mesh(
            source,
            scalars="__post_scalar",
            preference=association,
            cmap=cmap,
            clim=limits,
            n_colors=n_colors,
            opacity=opacity,
            style=style,
            show_edges=show_edges,
            scalar_bar_args={"title": label, "color": "black"},
        )
        if axes:
            plot.add_axes()
        actual_camera = configure_camera(
            plot, camera, normal=normal, projection=projection, zoom=zoom
        )
        if metadata is not None:
            metadata.update(
                field=field,
                association=association,
                component=component,
                clim=limits,
                cmap=cmap,
                n_colors=n_colors,
                camera=actual_camera,
                size=list(size),
                unit=unit,
                opacity=opacity,
                style=style,
                show_edges=show_edges,
                axes=axes,
                background=background,
                title=label,
            )
        if not owned:
            return actor
        pixels = plot.screenshot(return_img=True)
        if pixels is None or pixels.shape[:2] != (size[1], size[0]):
            raise RuntimeError("离屏渲染未生成有效图片")
        return np.array(pixels, copy=True)
    finally:
        if owned:
            plot.close()


def render_profile(
    profile: dict,
    *,
    field: str,
    component: str | int = "scalar",
    size: Any = (1600, 1000),
    title: str | None = None,
    unit: str | None = None,
) -> np.ndarray:
    """沿线曲线绘图；无效采样置 NaN 使线条断开。"""
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
    except ImportError as exc:
        raise ImportError("曲线图片需要安装 ai4e-core[post]") from exc

    values = np.array(profile["fields"][field], dtype=float, copy=True)
    if values.ndim == 2:
        if component == "scalar" and values.shape[1] != 1:
            raise ValueError("向量曲线须显式选择分量或模长")
        if component not in {"scalar", "magnitude", 0, 1, 2, "0", "1", "2"}:
            raise ValueError("非法曲线分量")
        values = (
            np.linalg.norm(values, axis=1)
            if component == "magnitude"
            else values[:, int(component) if component != "scalar" else 0]
        )
    if values.ndim != 1:
        raise ValueError("曲线需要指定标量分量")
    values[~np.asarray(profile["valid"], dtype=bool)] = np.nan
    figure = Figure(figsize=(size[0] / 100, size[1] / 100), dpi=100, layout="constrained")
    canvas = FigureCanvasAgg(figure)
    axis = figure.subplots()
    axis.plot(profile["distance"], values)
    axis.set(xlabel="Distance", ylabel=f"{field} [{unit}]" if unit else field, title=title or field)
    axis.grid(alpha=0.25)
    canvas.draw()
    return np.asarray(canvas.buffer_rgba()).copy()
