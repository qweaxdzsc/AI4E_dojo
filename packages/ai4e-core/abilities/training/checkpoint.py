"""轮次边界状态打包与严格兼容恢复。"""

import random
from copy import deepcopy

import numpy as np
import torch


def capture(
    model,
    optimizer,
    *,
    epoch,
    updates,
    best,
    contract,
    ema=None,
    scaler=None,
    scheduler=None,
):
    """冻结模型、优化器和所有已启用随机/数值状态。"""
    return deepcopy(
        {
            "version": 2,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "epoch": epoch,
            "updates": updates,
            "best": best,
            "contract": contract,
            "python_rng": random.getstate(),
            "numpy_rng": np.random.get_state(),
            "torch_rng": torch.get_rng_state(),
            "cuda_rng": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            "mps_rng": torch.mps.get_rng_state() if torch.backends.mps.is_available() else None,
            "ema": ema.state if ema else None,
            "scaler": scaler.state_dict() if scaler else None,
            "scheduler": scheduler.state_dict() if scheduler else None,
        }
    )


def restore(path, model, optimizer, *, contract, ema=None, scaler=None, scheduler=None):
    """加载用户指定可信本地检查点，语义不一致即拒绝恢复。"""
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state.get("version") != 2:
        raise ValueError("检查点版本不兼容：需要 version=2，旧格式不支持迁移（语义冲突）")
    if state["contract"] != contract:
        raise ValueError("检查点配置、模型或数据语义冲突")
    if state.get("ema") is not None and ema is None:
        raise ValueError("EMA 或精度恢复设置不一致")
    if (state.get("scaler") is None) != (scaler is None):
        raise ValueError("EMA 或精度恢复设置不一致")
    if (state.get("scheduler") is None) != (scheduler is None):
        raise ValueError("调度恢复设置不一致")
    model.load_state_dict(state["model"], strict=True)
    optimizer.load_state_dict(state["optimizer"])
    if ema:
        if state.get("ema") is None:
            ema.state = {key: value.detach().clone() for key, value in model.state_dict().items()}
        else:
            device = next(model.parameters()).device
            ema.state = {key: value.to(device) for key, value in state["ema"].items()}
    if scaler:
        scaler.load_state_dict(state["scaler"])
    if scheduler:
        scheduler.load_state_dict(state["scheduler"])
    random.setstate(state["python_rng"])
    np.random.set_state(state["numpy_rng"])
    torch.set_rng_state(state["torch_rng"])
    if state["cuda_rng"] is not None and torch.cuda.is_available():
        torch.cuda.set_rng_state_all(state["cuda_rng"])
    if state.get("mps_rng") is not None and torch.backends.mps.is_available():
        torch.mps.set_rng_state(state["mps_rng"])
    return state


def restore_selection(state, path, *, best_on_equal=False):
    """恢复此前选优产物；缺失时拒绝把最新模型伪装成最佳模型。"""
    import math
    from pathlib import Path

    if not math.isfinite(state["best"]):
        return None
    selected = state.get("selection")
    if selected is None:
        history = state.get("history", [])
        last = history[-1].get("evaluation") if history else None
        earlier_best = any(
            entry.get("evaluation") is not None and entry["evaluation"]["loss"] == state["best"]
            for entry in history[:-1]
        )
        if (
            last is not None
            and last["loss"] == state["best"]
            and (best_on_equal or not earlier_best)
        ):
            selected = {key: value for key, value in state.items() if key != "selection"}
        else:
            candidate = Path(path).with_name("best.pt")
            if not candidate.is_file():
                raise ValueError("恢复缺少此前最佳检查点，不能以最新模型替代")
            selected = torch.load(candidate, map_location="cpu", weights_only=False)
    if (
        selected.get("contract") != state["contract"]
        or selected.get("best") != state["best"]
        or selected.get("epoch", state["epoch"] + 1) > state["epoch"]
    ):
        raise ValueError("此前最佳检查点与恢复状态不一致")
    return deepcopy({key: value for key, value in selected.items() if key != "selection"})
