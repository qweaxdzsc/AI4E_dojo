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
