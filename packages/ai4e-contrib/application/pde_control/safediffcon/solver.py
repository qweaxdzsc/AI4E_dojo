"""物理响应连接，KSTAR 子进程不污染 Dojo 的 Python/NumPy 环境。"""

import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import torch


def solve(states: np.ndarray, controls: np.ndarray, *, case: str, settings: dict) -> np.ndarray:
    """消费物理初态与控制，返回可直接评价的真实响应。"""
    if case == "burgers":
        from ai4e_contrib.ability.postproc.safediffcon.burgers import burgers_numeric_solve_free

        result = burgers_numeric_solve_free(
            torch.tensor(states[:, 0], dtype=torch.float32),
            torch.tensor(controls, dtype=torch.float32),
            visc=0.01,
            T=1.0,
            dt=1e-4,
            num_t=10,
        )
        return result.numpy()
    from ai4e_contrib.ability.postproc.safediffcon import burgers as location

    worker = Path(location.__file__).with_name("kstar_worker.py")
    with tempfile.TemporaryDirectory(prefix="safediffcon-kstar-") as directory:
        directory = Path(directory)
        np.savez(directory / "controls.npz", controls=controls)
        env = {
            **os.environ,
            "SAFEDIFFCON_KSTAR_ASSETS": str(settings["assets"]),
            "MPLBACKEND": "Agg",
            "TF_NUM_INTRAOP_THREADS": "4",
            "TF_NUM_INTEROP_THREADS": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--python",
                settings["python"],
                "python",
                str(worker),
                "--input",
                str(directory / "controls.npz"),
                "--output",
                str(directory / "response.npy"),
            ],
            env=env,
            check=True,
            timeout=settings["timeout_seconds"],
        )
        values = np.load(directory / "response.npy", allow_pickle=False)
    if values.shape != (len(controls), 122, 8) or not np.isfinite(values).all():
        raise ValueError("KSTAR 响应形状或数值不符")
    return values[:, :, [1, 4, 6]].transpose(0, 2, 1)
