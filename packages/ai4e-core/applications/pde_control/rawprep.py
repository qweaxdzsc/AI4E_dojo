"""控制领域原始数组处理：来源解释注入，物理清单独立交付。"""

from .contracts import save_arrays


def materialize(root: str, output: str, *, reader, case: str) -> dict[str, str]:
    """读取官方三个分片，保存物理状态、控制与目标，不训练模型。"""
    from pathlib import Path

    result = {}
    for split in ("train", "cal", "test"):
        arrays = reader(root, split)
        count = len(arrays["states"])
        if any(len(value) != count for value in arrays.values()):
            raise ValueError("同分片字段样本身份不对齐")
        result[split] = save_arrays(
            Path(output) / split,
            arrays,
            kind="control_physical_v1",
            metadata={"case": case, "split": split, "source": str(root), "count": count},
        )
    return result
