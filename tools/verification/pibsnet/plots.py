"""从已保存的物理数组与正式历史生成误差图，不执行新训练。"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch


def render(root, *, prediction_directory="predictions", figure_directory="figures"):
    """绘制已有完整结果；不为尚未完成案例生成成功报告。"""
    output = root / figure_directory
    output.mkdir(parents=True, exist_ok=True)
    for case in (
        "convection_diffusion",
        "neumann_diffusion",
        "advection",
        "burgers",
        "diffusion_trapezoid",
    ):
        manifest = root / case / prediction_directory / "predictions.json"
        if not manifest.exists():
            continue
        record = json.loads(manifest.read_text())
        if record["status"] != "complete":
            continue
        sample = torch.load(manifest.parent / f"{record['samples'][0]['id']}.pt", weights_only=True)
        truth, prediction = sample["target"].numpy(), sample["prediction"].numpy()
        if truth.ndim == 3:
            truth, prediction = truth[-1], prediction[-1]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
        low, high = min(truth.min(), prediction.min()), max(truth.max(), prediction.max())
        for ax, array, name in zip(
            axes,
            (truth, prediction, np.abs(prediction - truth)),
            ("Truth", "Prediction", "Absolute error"),
            strict=True,
        ):
            image = ax.imshow(
                array,
                origin="lower",
                aspect="auto",
                **({"vmin": low, "vmax": high} if name != "Absolute error" else {}),
            )
            ax.set_title(name)
            ax.set_xlabel("Spatial grid index")
            ax.set_ylabel("Time index" if sample["target"].ndim == 2 else "Spatial grid index")
            fig.colorbar(image, ax=ax)
        fig.suptitle(case)
        fig.savefig(output / f"{case}-fields.png", dpi=160)
        plt.close(fig)
        state = torch.load(record["checkpoint"], map_location="cpu", weights_only=False)
        fig, ax = plt.subplots(figsize=(7, 4), constrained_layout=True)
        history = state["history"]
        ax.semilogy(
            [r["epoch"] for r in history], [r["loss"] for r in history], label="Total weighted loss"
        )
        for name in ("pde", "data", "initial"):
            rows = [r for r in history if name in r.get("online", {})]
            if rows:
                ax.semilogy(
                    [r["epoch"] for r in rows], [r["online"][name] for r in rows], label=name
                )
        ax.set(xlabel="Epoch", ylabel="Mean per-instance loss", title=case)
        ax.legend()
        fig.savefig(output / f"{case}-loss.png", dpi=160)
        plt.close(fig)
    data = np.load(root / "derivatives/fields.npz")
    for i, name in enumerate(("field", "dt", "dx", "dtt", "dxx", "dtx")):
        exact = data["truth"][i]
        fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
        arrays = (
            exact,
            np.abs(data["spline"][i] - exact),
            np.abs(data["finite_difference"][i] - exact),
        )
        for ax, array, title in zip(
            axes, arrays, ("Analytic", "Spline error", "Finite difference error"), strict=True
        ):
            image = ax.imshow(array, origin="lower", aspect="auto", extent=[-1, 1, 0, 1])
            ax.set(title=title, xlabel="x", ylabel="t")
            fig.colorbar(image, ax=ax)
        fig.suptitle(name)
        fig.savefig(output / f"derivatives-{name}.png", dpi=160)
        plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--prediction-directory", default="predictions")
    parser.add_argument("--figure-directory", default="figures")
    args = parser.parse_args()
    render(
        args.root,
        prediction_directory=args.prediction_directory,
        figure_directory=args.figure_directory,
    )
