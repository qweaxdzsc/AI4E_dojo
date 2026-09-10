"""pytest 夹具：本地 ShapeNet 目录与隔离的 HuggingFace 缓存。"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import huggingface_reachable, shapenet_raw_root


@pytest.fixture
def shapenet_raw() -> Path:
    """有本地原始样本才继续，否则跳过。"""
    root = shapenet_raw_root()
    if not root.is_dir():
        pytest.skip(f"本地 ShapeNet 原始目录不存在: {root}")
    return root


@pytest.fixture
def hf_isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """把 HuggingFace 缓存关进临时目录，测完由 pytest 删除。"""
    if not huggingface_reachable():
        pytest.skip("huggingface.co 不可达")
    home = tmp_path / "hf_home"
    monkeypatch.setenv("HF_HOME", str(home))
    monkeypatch.setenv("HF_HUB_CACHE", str(home / "hub"))
    return tmp_path
