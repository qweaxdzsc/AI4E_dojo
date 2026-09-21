"""规则网格固定物理帧的预测、真值与误差图。"""


def plot_frame(prediction, target, path, *, sample=0, frame=-1, component=0):
    """保存同色标真值/预测及误差图；不调用模型。"""
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    p = prediction[sample, frame, :, :, component]
    t = target[sample, frame, :, :, component]
    fig, axes = plt.subplots(1, 3, figsize=(10, 3), layout="constrained")
    for axis, value, title in zip(axes, (t, p, p - t), ("Truth", "Prediction", "Error")):
        image = axis.imshow(
            value,
            origin="lower",
            vmin=min(t.min(), p.min()) if title != "Error" else None,
            vmax=max(t.max(), p.max()) if title != "Error" else None,
        )
        axis.set_title(title)
        fig.colorbar(image, ax=axis)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_error_curve(frame_components, path):
    """按物理帧绘制各分量相对误差，不能混作生成流时间。"""
    import matplotlib

    matplotlib.use("Agg")
    import numpy as np
    from matplotlib import pyplot as plt

    values = np.asarray(frame_components, dtype=float)
    fig, axis = plt.subplots(figsize=(6, 3), layout="constrained")
    for component in range(values.shape[1]):
        axis.plot(range(values.shape[0]), values[:, component], label=f"component {component}")
    axis.set_xlabel("Physical frame")
    axis.set_ylabel("Relative L2")
    axis.legend()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_named_frames(path, metrics: dict, *, time_unit: str):
    """具名场随显式物理时间的样本平均误差图，单位从调用方提供。"""
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(dict.fromkeys(row["field"] for row in metrics["rows"]))
    fig, axes = plt.subplots(len(names), 1, figsize=(7, 3 * len(names)), squeeze=False)
    for axis, name in zip(axes[:, 0], names, strict=True):
        rows = [row for row in metrics["rows"] if row["field"] == name]
        times = sorted({row["time"] for row in rows})
        values = [np.mean([row["mse"] for row in rows if row["time"] == time]) for time in times]
        axis.plot(times, values, marker="o")
        axis.set(xlabel=f"time [{time_unit}]", ylabel=f"{name} MSE [{rows[0]['unit']}²]")
        axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path)


def plot_named_field(path, prediction, target, coordinates, *, field: str, unit: str):
    """最后一帧同一场的真值/预测/误差散点图，适用于二维或表面坐标。"""
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for axis, values, title in zip(
        axes,
        (target, prediction, prediction - target),
        ("Target", "Prediction", "Error"),
        strict=True,
    ):
        artist = axis.scatter(coordinates[:, 0], coordinates[:, 1], c=np.asarray(values), s=3)
        axis.set_title(f"{title}: {field} [{unit}]")
        axis.set_aspect("equal")
        fig.colorbar(artist, ax=axis)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return str(path)
