"""两个 SafeDiffCon 原始数据源；官方划分不受网络配置影响。"""

import hashlib
import zipfile
from pathlib import Path

import h5py
import numpy as np
from pyarrow import ipc


def read_burgers(root: str | Path, split: str) -> dict[str, np.ndarray]:
    """读取原 HDF5 状态与控制，不重划分训练/校准/测试。"""
    with h5py.File(Path(root) / f"burgers_{split}.h5", "r") as source:
        return {
            "states": source[split]["pde_11-128"][:],
            "controls": source[split]["pde_11-128_f"][:],
        }


def read_tokamak(root: str | Path, split: str) -> dict[str, np.ndarray]:
    """按原顺序读取四个 Arrow 分片，缺 metadata 时不要求重下载。"""
    from contextlib import ExitStack

    start, end = {"train": (0, 48950), "cal": (48950, 49950), "test": (49950, 50000)}[split]
    fields = {"states": [], "controls": [], "targets": []}
    for index in range(4):
        if index * 12500 >= end or (index + 1) * 12500 <= start:
            continue
        name = f"data-{index:05d}-of-00004.arrow"
        candidates = sorted(Path(root).rglob(name))
        with ExitStack() as stack:
            choices = []
            for candidate in candidates:
                choices.append(stack.enter_context(candidate.open("rb")))
            for path in sorted(Path(root).glob("*.zip")):
                archive = stack.enter_context(zipfile.ZipFile(path))
                choices.extend(
                    stack.enter_context(archive.open(member))
                    for member in archive.namelist()
                    if Path(member).name == name
                )
            if not choices:
                raise FileNotFoundError(name)
            if len(choices) > 1:
                hashes = [hashlib.file_digest(choice, "sha256").hexdigest() for choice in choices]
                if len(set(hashes)) != 1:
                    raise ValueError(f"Tokamak 同名分片副本内容冲突: {name}")
                for choice in choices:
                    choice.seek(0)
            stream = choices[0]
            offset = index * 12500
            for batch in ipc.open_stream(stream):
                local_start, local_end = max(0, start - offset), min(len(batch), end - offset)
                if local_end > local_start:
                    rows = batch.slice(local_start, local_end - local_start).to_pylist()
                    for role, key in (
                        ("states", "outputs"),
                        ("controls", "actions"),
                        ("targets", "targets"),
                    ):
                        fields[role].extend(row[key] for row in rows)
                offset += len(batch)
            if offset != (index + 1) * 12500:
                raise ValueError("Tokamak 分片数量不符")
    return {name: np.asarray(value, dtype=np.float32) for name, value in fields.items()}
