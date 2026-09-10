"""HuggingFace 通用下载：整库快照或单文件。"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Literal

RepoType = Literal["model", "dataset"]

SnapshotFn = Callable[..., str]
FileFn = Callable[..., str]


def _token() -> str | None:
    """读取环境变量中的 HuggingFace 令牌，没有则匿名下载。"""
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")


def download_huggingface_snapshot(
    repo_id: str,
    local_dir: str | Path,
    *,
    repo_type: RepoType = "dataset",
    revision: str = "main",
    snapshot_download_fn: SnapshotFn | None = None,
) -> Path:
    """把 HuggingFace 仓库整库下载到本地目录。

    Args:
        repo_id: 仓库标识，例如 ``EmmiAI/DrivAerML_subsampled_10x``。
        local_dir: 本地目标目录。
        repo_type: ``dataset`` 或 ``model``。
        revision: 分支或标签。
        snapshot_download_fn: 可替换的下载函数，测试用替身。

    Returns:
        本地目标目录。
    """
    dest = Path(local_dir)
    dest.mkdir(parents=True, exist_ok=True)
    fetch = snapshot_download_fn
    if fetch is None:
        from huggingface_hub import snapshot_download

        fetch = snapshot_download
    fetch(
        repo_id=repo_id,
        local_dir=str(dest),
        repo_type=repo_type,
        revision=revision,
        token=_token(),
    )
    return dest


def download_huggingface_file(
    repo_id: str,
    filename: str,
    local_dir: str | Path,
    *,
    repo_type: RepoType = "dataset",
    revision: str = "main",
    hf_hub_download_fn: FileFn | None = None,
) -> Path:
    """从 HuggingFace 仓库下载单个文件到本地目录。

    Args:
        repo_id: 仓库标识。
        filename: 仓库内相对路径。
        local_dir: 本地目标目录。
        repo_type: ``dataset`` 或 ``model``。
        revision: 分支或标签。
        hf_hub_download_fn: 可替换的下载函数，测试用替身。

    Returns:
        下载后的本地文件路径。
    """
    dest = Path(local_dir)
    dest.mkdir(parents=True, exist_ok=True)
    fetch = hf_hub_download_fn
    if fetch is None:
        from huggingface_hub import hf_hub_download

        fetch = hf_hub_download
    saved = fetch(
        repo_id=repo_id,
        filename=filename,
        repo_type=repo_type,
        revision=revision,
        token=_token(),
        local_dir=str(dest),
    )
    return Path(saved)
