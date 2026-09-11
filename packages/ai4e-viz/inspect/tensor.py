"""安全读取 NPY 与受限 PT 张量，拒绝自定义对象反序列化。"""

from pathlib import Path


def read_tensors(path: Path) -> dict:
    """按张量键返回数组；只接受张量或张量字典。"""
    import numpy as np

    if path.suffix.lower() == ".npy":
        return {"array": np.load(path, mmap_mode="r", allow_pickle=False)}
    if path.suffix.lower() == ".zarr" or path.is_dir():
        import zarr

        root = zarr.open(str(path), mode="r")
        if hasattr(root, "shape"):
            return {"array": root}
        arrays = {}

        def visit(group, prefix=""):
            for name, value in group.members():
                key = prefix + name
                if hasattr(value, "shape"):
                    arrays[key] = value
                else:
                    visit(value, key + "/")

        visit(root)
        if not arrays:
            raise ValueError("empty_tensor_store")
        return arrays
    import torch

    value = torch.load(path, map_location="cpu", weights_only=True)
    values = value if isinstance(value, dict) else {"array": value}
    if any(not isinstance(v, torch.Tensor) for v in values.values()):
        raise ValueError("unsupported_tensor_payload")
    return {str(k): v.detach().numpy() for k, v in values.items()}


def inspect_tensor(path: Path) -> dict:
    """读取形状与类型，不将整个数组传给浏览器。"""
    return {
        "kind": "tensor",
        "fields": [
            {
                "id": k,
                "name": k,
                "association": "array",
                "shape": list(v.shape),
                "dtype": str(v.dtype),
            }
            for k, v in read_tensors(path).items()
        ],
    }
