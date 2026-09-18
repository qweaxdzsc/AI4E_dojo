"""控制模型显式重建，权重种类不通过文件名猜测。"""

import torch


def restore_model(
    checkpoint: str,
    *,
    construct,
    settings: dict,
    case: str,
    device: str,
    weight_kind: str = "model",
) -> tuple[torch.nn.Module, dict]:
    """严格加载局部训练契约；不把别的网络宽度当作继续训练。"""
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if (
        state.get("version") != 2
        or state["contract"]["case"] != case
        or state["contract"]["model"] != settings
    ):
        raise ValueError("控制检查点的模型或案例不兼容")
    if state.get("status") != "complete":
        raise ValueError("控制阶段输入须为已完成检查点；中断状态仅用于训练恢复")
    model = construct(case=case, device=device, **settings)
    if weight_kind == "model":
        weights = state["model"]
    elif weight_kind == "ema" and state.get("ema"):
        weights = {
            k.removeprefix("ema_model."): v
            for k, v in state["ema"].items()
            if k.startswith("ema_model.")
        }
    else:
        raise ValueError("检查点缺少所选权重")
    model.load_state_dict(weights, strict=True)
    return model, state
