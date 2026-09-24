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
    return _restore_state(
        state, model, optimizer, contract=contract, ema=ema, scaler=scaler, scheduler=scheduler
    )


def _restore_state(state, model, optimizer, *, contract, ema=None, scaler=None, scheduler=None):
    """应用已读取的可信快照，供迭代恢复及失败回滚共用。"""
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


def capture_iteration(
    model,
    optimizer,
    *,
    updates,
    stream,
    contract,
    history,
    ema=None,
    scheduler=None,
    scaler=None,
    state_bindings=None,
):
    """在既有检查点容器中补充迭代状态，不改变旧轮次恢复语义。"""
    state = capture(
        model,
        optimizer,
        epoch=0,
        updates=updates,
        best=float("inf"),
        contract=contract,
        ema=ema,
        scheduler=scheduler,
        scaler=scaler,
    )
    state.update(
        loop_kind="iterations", stream=deepcopy(stream.state_dict()), history=list(history)
    )
    if state_bindings:
        state["user_state"] = capture_user_state(state_bindings)
    return state


def restore_iteration(
    path,
    model,
    optimizer,
    *,
    stream,
    contract,
    ema=None,
    scheduler=None,
    scaler=None,
    state_bindings=None,
):
    """先核对合同和游标副本，再恢复模型与真实数据流，拒绝时不消耗输入。"""
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state.get("loop_kind") != "iterations" or "stream" not in state:
        raise ValueError("检查点缺少精确迭代恢复状态")
    if state.get("version") != 2 or state.get("contract") != contract:
        raise ValueError("检查点配置、模型或数据语义冲突")
    if len(state.get("history", [])) != state.get("updates"):
        raise ValueError("恢复历史与有效更新次数不匹配")
    candidate = deepcopy(stream)
    candidate.load_state_dict(state["stream"])
    bindings = validate_state_bindings(state_bindings)
    _validate_user_state(state.get("user_state"), bindings)
    # 验证函数不得修改对象；加载函数只支持可回滚的内存状态。
    before = capture_iteration(
        model,
        optimizer,
        updates=0,
        stream=stream,
        contract=contract,
        history=[],
        ema=ema,
        scheduler=scheduler,
        scaler=scaler,
        state_bindings=bindings,
    )
    try:
        restored = _restore_state(
            state, model, optimizer, contract=contract, ema=ema, scheduler=scheduler, scaler=scaler
        )
        stream.load_state_dict(deepcopy(state["stream"]))
        _load_user_state(state.get("user_state"), bindings)
    except Exception as error:
        failures = []
        for rollback in (
            lambda: _restore_state(
                before,
                model,
                optimizer,
                contract=contract,
                ema=ema,
                scheduler=scheduler,
                scaler=scaler,
            ),
            lambda: stream.load_state_dict(deepcopy(before["stream"])),
            *(
                lambda name=name, hooks=hooks: hooks["load"](
                    deepcopy(before["user_state"]["values"][name])
                )
                for name, hooks in bindings.items()
            ),
        ):
            try:
                rollback()
            except Exception as failure:  # noqa: BLE001 - 回滚须尽力恢复其余对象并汇总失败
                failures.append(str(failure))
        if failures:
            raise RuntimeError(f"恢复失败且部分内存状态无法回滚: {failures}") from error
        raise
    return restored


def validate_state_bindings(bindings: dict | None) -> dict:
    """核对具名save/validate/load函数，不调用用户代码；返回连接表副本。

    validate必须无副作用，load只修改由save完整描述的内存状态。
    不要求组件继承基类；此约定只适用于显式启用的检查点连接。
    """
    if bindings is None:
        return {}
    if not isinstance(bindings, dict):
        raise TypeError("用户状态连接须为具名映射")
    result = {}
    for name, hooks in bindings.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(hooks, dict):
            raise ValueError("用户状态名称或连接非法")
        if set(hooks) != {"save", "validate", "load"} or not all(
            callable(v) for v in hooks.values()
        ):
            raise ValueError("用户状态需要save/validate/load三个函数")
        result[name] = dict(hooks)
    return result


def capture_user_state(bindings: dict) -> dict:
    """冻结具名用户状态，与固定algorithm_state兼容声明分离。"""
    bindings = validate_state_bindings(bindings)
    values = {name: deepcopy(hooks["save"]()) for name, hooks in bindings.items()}
    payload = {"version": 1, "values": values}
    _validate_user_state(payload, bindings)
    return payload


def _validate_user_state(payload, bindings):
    """先核对完整状态集合，再执行用户只读预检。"""
    if payload is None:
        if bindings:
            raise ValueError("检查点缺少要求的用户状态")
        return
    if (
        not isinstance(payload, dict)
        or type(payload.get("version")) is not int
        or payload.get("version") != 1
        or not isinstance(payload.get("values"), dict)
    ):
        raise ValueError("用户状态版本或结构非法")
    if set(payload["values"]) != set(bindings):
        raise ValueError("用户状态名称不相容，不能丢弃或补造状态")
    for name, hooks in bindings.items():
        hooks["validate"](deepcopy(payload["values"][name]))


def _load_user_state(payload, bindings):
    """预检通过后读回独立副本，避免用户函数改写冻结状态。"""
    if payload is not None:
        for name, hooks in bindings.items():
            hooks["load"](deepcopy(payload["values"][name]))
