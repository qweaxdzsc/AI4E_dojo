"""DeepMind CylinderFlow 官方轨迹子集获取，保留原始记录与分片身份。"""

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

from ai4e_core.abilities.data.source.record_download import download_record_prefix

BASE = "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/"


def download_subset(directory, *, train=8, valid=2, test=2):
    """获取官方完整轨迹子集；不生成或修改来源字段。"""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    with urlopen(BASE + "meta.json", timeout=60) as response:
        metadata = response.read()
    parsed = json.loads(metadata)
    if parsed["trajectory_length"] != 600:
        raise ValueError("官方元数据的轨迹长度已经变化")
    path = root / "meta.json"
    if path.exists() and path.read_bytes() != metadata:
        raise ValueError("本地与官方元数据不一致")
    path.write_bytes(metadata)
    result = {"meta_sha256": hashlib.sha256(metadata).hexdigest(), "splits": {}}
    for split, count in (("train", train), ("valid", valid), ("test", test)):
        result["splits"][split] = download_record_prefix(
            BASE + split + ".tfrecord", root / split, count
        )
    return result
