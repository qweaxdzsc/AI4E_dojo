"""通用计算设备发现；不读取任务、模型或领域配置。"""


def available_devices() -> list[str]:
    """返回实际可用设备，分配与占用由管理调用方决定。"""
    import torch

    devices = ["cpu"]
    if torch.backends.mps.is_available():
        devices.append("mps")
    if torch.cuda.is_available():
        devices.extend(f"cuda:{index}" for index in range(torch.cuda.device_count()))
    return devices


def inspect_resources(request: dict) -> list[str]:
    """为独立资源检查进程提供可序列化入口。"""
    if request.get("operation") != "devices":
        raise ValueError("unknown_resource_operation")
    return available_devices()
