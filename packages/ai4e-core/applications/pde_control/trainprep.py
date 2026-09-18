"""控制领域模型准备；变换实现由贡献能力注入。"""

from pathlib import Path

from .contracts import read_arrays, save_arrays


def prepare(
    physical: dict[str, str], output: str | Path, *, transform, case: str
) -> dict[str, str]:
    """独立生成模型准备，保存来源和物理/模型空间交接。"""
    result = {}
    for split, path in physical.items():
        record, arrays = read_arrays(path, kind="control_physical_v1")
        if record["metadata"]["case"] != case:
            raise ValueError("物理数据案例不匹配")
        prepared = transform(arrays, case=case)
        result[split] = save_arrays(
            Path(output) / split,
            prepared,
            kind="control_prepared_v1",
            metadata={
                **record["metadata"],
                "physical": str(path),
                "target_source": "outputs",
                "paper_target_separate": True,
            },
        )
    return result
