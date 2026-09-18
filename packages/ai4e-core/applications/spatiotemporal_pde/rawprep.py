"""物理时空场的分片交接；数据身份由来源适配器提供。"""

from pathlib import Path

from ai4e_core.abilities.data.save.array_manifest import save_arrays


def prepare_physical(reader, options: dict, output: str) -> dict:
    """冻结所选轨迹和来源，物理数组与模型输入分开保存。"""
    splits, metadata = reader(options)
    return {
        name: save_arrays(
            Path(output) / name,
            arrays,
            kind="spatiotemporal-physical-v1",
            metadata={**metadata, "split": name},
        )
        for name, arrays in splits.items()
    }
