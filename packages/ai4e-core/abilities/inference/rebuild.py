"""推理检查点重建：只迁移模型权重，不恢复训练进度。"""

from pathlib import Path
from typing import Any

import torch

SEMANTIC_KEYS = ("model", "trainprep", "normalization")


def rebuild(path: str | Path, model, *, contract: dict[str, Any]) -> dict[str, Any]:
    """从检查点只加载模型权重，并核对版本与语义契约。

    不加载优化器、调度、EMA、缩放器或随机流，因此不会推进或回退训练进度。

    Args:
        path: 可信本地检查点路径。
        model: 已按当前配置构造、尚未或即将用于推理的模型。
        contract: 当前运行的语义契约，至少含 ``model_version``、``model``、
            ``trainprep`` 与 ``normalization``。

    Returns:
        含 ``model`` 权重和检查点内 ``contract`` 的字典，便于调用方再核对接线。

    Raises:
        ValueError: 版本不是 2，或模型、准备、归一化语义不一致。
    """
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state.get("version") != 2:
        raise ValueError("检查点版本不兼容：需要 version=2，旧格式不支持迁移（语义冲突）")
    saved = state.get("contract") or {}
    if saved.get("model_version") != contract.get("model_version"):
        raise ValueError("检查点配置、模型或数据语义冲突")
    for key in SEMANTIC_KEYS:
        if saved.get(key) != contract.get(key):
            raise ValueError("检查点配置、模型或数据语义冲突")
    model.load_state_dict(state["model"], strict=True)
    return {"model": state["model"], "contract": saved}
