"""测试辅助：相对仓库根解析本地数据，运行时探测外网与设备。"""

from __future__ import annotations

import os
import socket
from pathlib import Path

import torch

from ai4e_core.abilities.training.optimization import resolve_device

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHAPENET_RAW = (
    Path("..") / ".." / "datasets" / "shapenet_car_cfd" / "mlcfd_data" / "training_data"
)
DEFAULT_SHAPENET_PROCESSED = Path("..") / ".." / "datasets" / "shapenet_car_cfd"
SHAPENET_SAMPLES = (
    Path("param0/1687b77b048d1aaf635b88185c42637a"),
    Path("param2/86c8a3137a716d70e742b0b5e87bec54"),
)


def shapenet_raw_root() -> Path:
    """解析 ShapeNet-Car 原始 ``training_data`` 目录。

    优先环境变量 ``AI4E_SHAPENET_RAW``（相对路径相对仓库根），
    否则使用仓库根下的 ``../../datasets/shapenet_car_cfd/mlcfd_data/training_data``。
    """
    override = os.environ.get("AI4E_SHAPENET_RAW")
    if override:
        path = Path(override)
        return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()
    return (REPO_ROOT / DEFAULT_SHAPENET_RAW).resolve()


def shapenet_processed_root() -> Path:
    """解析 ShapeNet-Car 预处理写出根。

    优先环境变量 ``AI4E_SHAPENET_PROCESSED``（相对路径相对仓库根），
    否则使用仓库根下的 ``../../datasets/shapenet_car_cfd``。
    """
    override = os.environ.get("AI4E_SHAPENET_PROCESSED")
    if override:
        path = Path(override)
        return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()
    return (REPO_ROOT / DEFAULT_SHAPENET_PROCESSED).resolve()


def resolve_test_device() -> torch.device:
    """复用训练设备解析：``auto`` 优先加速器，没有则警告并回退 CPU。"""
    return resolve_device("auto")


def to_device(value, device: torch.device):
    """把张量或张量字典放到解析后的设备上。"""
    if isinstance(value, dict):
        return {key: to_device(item, device) for key, item in value.items()}
    if isinstance(value, torch.Tensor):
        return value.to(device)
    return value


def huggingface_reachable(*, timeout: float = 3.0) -> bool:
    """探测 HuggingFace Hub 是否可达。"""
    try:
        socket.create_connection(("huggingface.co", 443), timeout=timeout).close()
    except OSError:
        return False
    return True
