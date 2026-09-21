"""按来源轨迹生成模型准备，不改变物理参考真值。"""

from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays, save_arrays


def prepare_inputs(
    physical: dict, output: str, transform, *, declaration: dict, chunk_size=256
) -> dict:
    """只为训练物化系数；评价继续读取原始物理条件。"""
    record, arrays = read_arrays(physical["train"], kind="spatiotemporal-physical-v1")
    chunks = []
    for offset in range(0, len(arrays["u"]), chunk_size):
        with torch.no_grad():
            values = transform(
                torch.from_numpy(arrays["u"][offset : offset + chunk_size].copy()),
                torch.from_numpy(arrays["f"][offset : offset + chunk_size].copy()),
            )
        chunks.append(values.cpu().numpy())
    manifest = save_arrays(
        Path(output) / "train",
        {"values": np.concatenate(chunks), "ids": arrays["ids"]},
        kind="spatiotemporal-prepared-v1",
        metadata={
            "physical": str(Path(physical["train"]).resolve()),
            "physical_sha256": digest(physical["train"]),
            "declaration": declaration,
            "source": record["metadata"],
        },
    )
    return {"train": manifest, "validation": physical["validation"], "test": physical["test"]}


def prepare_trajectory_inputs(
    physical, output, *, extract, statistics, transform, declaration, caches=None
):
    """具名轨迹准备入口，抽取时间与通道绑定由调用方声明。"""
    from ai4e_core.applications.parametric_pde.trainprep import prepare_field_inputs

    return prepare_field_inputs(
        physical,
        output,
        extract=extract,
        statistics=statistics,
        transform=transform,
        declaration=declaration,
        caches=caches,
    )
