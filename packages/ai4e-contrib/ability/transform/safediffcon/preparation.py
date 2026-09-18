"""SafeDiffCon 原版通道、补齐和常数缩放，保留独立的物理目标。"""

import numpy as np

TOKAMAK_SCALE = np.array([2, 7, 2, 1, 2, 2, 2, 2, 1, 1, 2, 3], dtype=np.float32)


def prepare_arrays(arrays: dict[str, np.ndarray], *, case: str) -> dict[str, np.ndarray]:
    """返回原版网络张量、参考状态及论文原 targets；所有轴显式声明。"""
    state = np.asarray(arrays["states"], dtype=np.float32)
    control = np.asarray(arrays["controls"], dtype=np.float32)
    if case == "burgers":
        if state.shape[1:] != (11, 128) or control.shape[1:] != (10, 128):
            raise ValueError("Burgers 状态/控制时间或空间轴不符")
        model = np.zeros((len(state), 3, 16, 128), dtype=np.float32)
        model[:, 0, :11] = state
        model[:, 1, :10] = control
        model[:, 2, :11] = np.square(state).max(axis=(1, 2))[:, None, None]
        return {
            "model": model / np.float32(10),
            "target": state,
            "paper_target": state,
            "controls": control,
        }
    if case != "tokamak" or state.shape[1:] != (122, 8) or control.shape[1:] != (121, 9):
        raise ValueError("Tokamak 状态/控制时间或通道轴不符")
    model = np.zeros((len(state), 12, 128), dtype=np.float32)
    target = state[:, :, [1, 4, 6]].transpose(0, 2, 1)
    model[:, :3, :122] = target
    model[:, 3:, :121] = control.transpose(0, 2, 1)
    return {
        "model": model / TOKAMAK_SCALE[None, :, None],
        "target": target,
        "paper_target": np.asarray(arrays["targets"], dtype=np.float32).transpose(0, 2, 1),
        "controls": control,
    }


def physical(values, *, case):
    """恢复物理单位；输入和输出均保留原生维度。"""
    import torch

    if case == "burgers":
        return values * 10
    return values * torch.as_tensor(TOKAMAK_SCALE, device=values.device)[:, None]
