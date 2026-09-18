"""独立场准备记录与耦合配对交接。"""

from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.validate.trajectory import validate_pairing

from .contracts import digest, file_digest, read_record


def prepare(descriptions, path, *, dataset, profile="scaled"):
    """冻结已解析来源、字段与选择；不复制物理数组。"""
    coupled = [value for key, value in descriptions.items() if key.endswith("/couple")]
    if coupled:
        validate_pairing(
            [
                {
                    "sample_ids": [
                        (r["id"], r.get("index"), r.get("window")) for r in description["records"]
                    ],
                    "time_indices": description.get("time_indices"),
                }
                for description in coupled
            ]
        )
    sources = {}
    for description in descriptions.values():
        paths = set(description.get("files", {}).values()) | {
            r["path"] for r in description["records"] if "path" in r
        }
        if "statistics_path" in description:
            paths.add(description["statistics_path"])
        for name in sorted(paths):
            if name not in sources:
                p = Path(name)
                sources[name] = {
                    "sha256": file_digest(p),
                    "size": p.stat().st_size,
                    "mtime_ns": p.stat().st_mtime_ns,
                }
    record = {
        "kind": "coupled_preparation_v1",
        "dataset": dataset,
        "profile": profile,
        "descriptions": descriptions,
        "sources": sources,
    }
    record["content_id"] = digest(record)
    path = Path(path)
    if path.exists():
        old = read_record(path, "coupled_preparation_v1")
        if old != record:
            raise FileExistsError("准备记录已存在且声明不同")
    else:
        save_json(path, record)
    return str(path.resolve())


def open_preparation(path):
    """核对来源当前身份；元信息变化时校验内容，不静默重做准备。"""
    record = read_record(path, "coupled_preparation_v1")
    for name, info in record["sources"].items():
        p = Path(name)
        if not p.is_file() or p.stat().st_size != info["size"]:
            raise ValueError(f"准备来源失效: {name}")
        if p.stat().st_mtime_ns != info["mtime_ns"] and file_digest(p) != info["sha256"]:
            raise ValueError(f"准备来源已改变: {name}")
    return record


class FieldSamples:
    """按需缓存已选窗口；模型训练只消费批次，不处理文件循环。"""

    def __init__(self, description, reader):
        self.description, self.reader = description, reader
        self.cache = {}

    def __len__(self):
        return len(self.description["records"])

    def sample(self, index):
        """读取一个冻结身份的样本。"""
        index = int(index)
        if index not in self.cache:
            self.cache[index] = self.reader(self.description["records"][index], self.description)
        return self.cache[index]

    def batch(self, indices, device="cpu"):
        """收集同场样本为 B,T,H,W,C，不跨场补齐网格。"""
        samples = [self.sample(i) for i in indices]
        return {
            key: torch.stack([s[key] for s in samples]).to(device)
            for key in ("input", "target", "physical")
        }
