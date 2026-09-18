"""冻结原工作树、切片身份和单侧三小时协议；兼容参考 Python 3.8。"""

import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path


def digest(path):
    """流式读取完整文件摘要。"""
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    """同目录原子发布轻量证据。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    temporary.replace(path)


def validate_indices(partitions):
    """核对代表索引、轨迹分片隔离和预期独立样本数量。"""
    for name, count, upper in (
        ("train", 18000, 20000),
        ("validation", 2000, 20000),
        ("test", 4000, 4000),
    ):
        values = partitions[name]
        if len(values) != count or len(set(values)) != count:
            raise ValueError("切片数量或唯一身份不符: " + name)
        if any(type(i) is not int or not 0 <= i < upper for i in values):
            raise ValueError("不是原重复组的代表索引: " + name)
    if set(partitions["train"]) & set(partitions["validation"]):
        raise ValueError("训练和验证泄漏")


def freeze(source, split, output):
    """保留完整跟踪源码及补丁；测试子集在训练之前固定。"""
    source, split, output = Path(source).resolve(), Path(split).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError("协议目录已存在，不能覆盖冻结记录")
    manifest = json.loads(split.read_text())
    partitions = {
        name: json.loads(Path(record["index_file"]).read_text())["representative_indices"]
        for name, record in manifest["partitions"].items()
    }
    validate_indices(partitions)
    for item in manifest["sources"].values():
        if digest(item["file"]) != item["sha256"]:
            raise ValueError("数据摘要与已批准切片不符")
    output.mkdir(parents=True)
    snapshot = output / "source"
    snapshot.mkdir()
    files = (
        subprocess.check_output(["git", "-C", str(source), "ls-files", "-z"]).decode().split("\0")
    )
    hashes = {}
    for name in filter(None, files):
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
        hashes[name] = digest(target)
    patch = subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--binary"])
    (output / "source.patch").write_bytes(patch)
    write_json(
        output / "source.json",
        {
            "head": subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"])
            .decode()
            .strip(),
            "files": hashes,
            "patch_sha256": digest(output / "source.patch"),
        },
    )
    write_json(
        output / "indices.json",
        {
            "train": partitions["train"],
            "validation": random.Random(43).sample(partitions["validation"], 64),
            "test": random.Random(44).sample(partitions["test"], 128),
        },
    )
    protocol = {
        "scope": "source_burgers_base_local_slice_not_paper_reproduction",
        "sources": manifest["sources"],
        "split_manifest": str(split),
        "split_sha256": digest(split),
        "indices_sha256": digest(output / "indices.json"),
        "max_updates": 2000,
        "batch_size": 16,
        "seed": 0,
        "dim": 128,
        "groups": 1,
        "dim_mults": [1, 2, 4, 8],
        "device": "mps",
        "dtype": "float32",
        "learning_rate": 1e-4,
        "adam_betas": [0.9, 0.99],
        "scheduler_T_max": 10000,
        "ema_decay": 0.995,
        "ema_update_every": 10,
        "gradient_clip": 1.0,
        "sampling_steps": 50,
        "eta": 1.0,
        "weights": "model",
        "train_cutoff": 8100,
        "evaluation_cutoff": 9900,
        "total_seconds": 10800,
        "differences": [
            "User-approved representative trajectory split and fixed 64/128 evaluation subset",
            "Source-script groups=1, not paper groups=8; at most 2000 updates",
            "CPU chunked wavelet preparation; original functions, unchanged formulas",
            "Original Trainer; DataLoader workers=0, checkpoint retention and safe-boundary deadline observer",
            "Original ordinary model and sampling functions; local base truth replaces absent high-resolution test",
            "No control solver or high-resolution evaluation in this prediction slice",
        ],
    }
    write_json(output / "protocol.json", protocol)
    return protocol


def verify(frozen):
    """运行前检查冻结源码和名单没有漂移。"""
    frozen = Path(frozen)
    source = json.loads((frozen / "source.json").read_text())
    for name, expected in source["files"].items():
        if digest(frozen / "source" / name) != expected:
            raise ValueError("冻结原源码变化: " + name)
    protocol = json.loads((frozen / "protocol.json").read_text())
    if digest(frozen / "indices.json") != protocol["indices_sha256"]:
        raise ValueError("固定评价名单变化")
    return protocol
