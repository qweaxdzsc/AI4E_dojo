"""训练诊断：规模、参数量、峰值内存与条件预计剩余时间。"""

import sys

import torch

from ai4e_core.base.events import event


def parameter_count(model) -> int:
    """统计全部参数个数。"""
    return int(sum(item.numel() for item in model.parameters()))


def peak_memory(device) -> int | None:
    """返回当前设备能测到的峰值内存字节数。"""
    device = torch.device(device)
    if device.type == "cuda" and torch.cuda.is_available():
        return int(torch.cuda.max_memory_allocated(device))
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux 为 KB，macOS 为字节
        return int(usage if sys.platform == "darwin" else usage * 1024)
    except (ImportError, OSError):
        return None


def report_setup(*, split_counts: dict, parameters: int, device) -> None:
    """写出启动时的数据规模与参数量。"""
    event("训练", "诊断", 规模=split_counts, 参数量=parameters, 设备=str(device))


def report_progress(
    *,
    epoch: int,
    epochs: int,
    updates: int,
    loss: float,
    lr: float,
    seconds: float,
    device,
    interactive: bool | None = None,
    stability: dict | None = None,
) -> None:
    """写出一轮进度；交互终端才附加预计剩余，稳定性仅在调用方打开时写入。"""
    payload = {
        "轮次": epoch,
        "更新": updates,
        "损失": loss,
        "学习率": lr,
        "耗时": seconds,
    }
    memory = peak_memory(device)
    if memory is not None:
        payload["峰值内存"] = memory
    if interactive is None:
        interactive = sys.stderr.isatty()
    if interactive and epoch < epochs and seconds > 0:
        payload["预计剩余"] = seconds * (epochs - epoch)
    if stability:
        payload["稳定性"] = stability
    event("训练", "进度", **payload)
