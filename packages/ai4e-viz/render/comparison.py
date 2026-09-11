"""已计算物理图形的共色标渲染，不计算模型或切面。"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv


def render(visual: dict, field: str, path: str | Path) -> dict:
    """真值及预测共色标，两个绝对误差使用另一共同色标。"""
    models = visual["models"]
    field_title = visual.get("field_labels", {}).get(field, field)
    mesh = pv.read(visual["path"])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if visual["kind"] == "curve":
        figure, ax = plt.subplots(figsize=(11, 4), layout="constrained")
        lines = mesh.lines
        start = 0
        segments = []
        while start < len(lines):
            count = lines[start]
            segments.append(lines[start + 1 : start + 1 + count])
            start += count + 1
        for label, color in [("truth", "black"), (models[0], "#2675be"), (models[1], "#e76f25")]:
            from matplotlib.collections import LineCollection

            values = mesh[field + "." + label]
            vertices = [np.column_stack((mesh.points[ids, 0], values[ids])) for ids in segments]
            ax.add_collection(LineCollection(vertices, colors=color, linewidths=1.0, label=label))
        ax.autoscale()
        ax.set_xlabel("Physical X")
        ax.set_ylabel(field_title)
        ax.set_title(
            f"{visual['sample']} | {field_title} | span {visual.get('span_fraction') or visual['fraction']:.0%}"
        )
        ax.grid(alpha=0.2)
        ax.legend()
        figure.savefig(path, dpi=160)
        plt.close(figure)
        return {"path": str(path), "kind": "curve", "field": field}
    labels = ["truth", *models, *(name + "_error" for name in models)]
    values = [np.asarray(mesh[field + "." + label]) for label in labels]
    if not all(np.isfinite(value).all() for value in values):
        raise ValueError("渲染产物含非有限值")
    lo = min(float(v.min()) for v in values[:3])
    hi = max(float(v.max()) for v in values[:3])
    error = max(float(v.max()) for v in values[3:])
    if hi == lo:
        hi = lo + 1e-12
    if error == 0:
        error = 1e-12
    plot = pv.Plotter(shape=(1, 5), off_screen=True, window_size=(2000, 650))
    try:
        for i, label in enumerate(labels):
            plot.subplot(0, i)
            plot.set_background("white")
            plot.add_text(label, font_size=12, color="black")
            plot.add_mesh(
                mesh,
                scalars=field + "." + label,
                clim=(lo, hi) if i < 3 else (0, error),
                cmap="viridis" if i < 3 else "magma",
                show_edges=False,
                scalar_bar_args={
                    "title": field_title if i < 3 else "absolute error",
                    "color": "black",
                    "title_font_size": 11,
                    "label_font_size": 10,
                },
            )
            if visual["kind"] == "slice":
                plot.view_xz() if visual["axis"] == 1 else plot.view_xy()
            else:
                plot.view_isometric()
                plot.camera.up = visual.get("view_up", [0, 0, 1])
            plot.reset_camera()
        plot.link_views()
        plot.screenshot(str(path))
    finally:
        plot.close()
    return {
        "path": str(path),
        "kind": visual["kind"],
        "field": field,
        "prediction_limits": [lo, hi],
        "error_limits": [0, error],
    }
