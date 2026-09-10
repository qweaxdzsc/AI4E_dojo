"""归一化方法记录：版本目录内原子提交，不覆盖不同变换。"""

from pathlib import Path

from ai4e_core.abilities.data.stats.load import load_statistics, write_statistics


def save_record(root: str | Path, digest: str, record: dict, *, dry_run: bool = False) -> Path:
    """保存冻结参数；已有记录必须完全一致，检查模式无写入。"""
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("非法归一化版本摘要")
    target = Path(root) / digest / "normalization.yaml"
    if target.exists():
        if load_statistics(target) != record:
            raise ValueError("冻结归一化记录冲突")
    elif not dry_run:
        write_statistics(target, record)
    return target


def materialize(
    index, normalization, output: dict, prepare_sample, *, dry_run: bool = False
) -> Path:
    """在独立版本目录保存全分辨率场，全部成功后才发布归一化清单。"""
    import json
    import shutil
    from uuid import uuid4

    import torch

    version = normalization.digest
    root = Path(output["root"]) / version
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"归一化数据版本已存在: {manifest_path}")
    manifest = {
        "version": 1,
        "state": "normalized",
        "normalization": normalization.record,
        "normalization_digest": version,
        "partitions": index.partitions,
        "samples": [],
    }
    created = []
    temporary = []
    try:
        for partition, samples in index.partitions.items():
            for i, sample in enumerate(samples):
                destination = (Path(output[partition]) / version / sample).resolve()
                split_root = (Path(output[partition]) / version).resolve()
                if not destination.is_relative_to(split_root) or destination == split_root:
                    raise ValueError("样本路径逃离归一化分片根")
                if destination.exists():
                    raise FileExistsError(destination)
                fields = normalization.apply(prepare_sample(index.read(partition, i)))
                record = {
                    "partition": partition,
                    "sample": sample,
                    "written": True,
                    "path": str(destination),
                    "filemap": {},
                    "fields": {},
                }
                stage = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
                if not dry_run:
                    stage.mkdir(parents=True)
                    temporary.append(stage)
                for n, (name, value) in enumerate(fields.items()):
                    filename = f"field_{n}.pt"
                    record["filemap"][name] = filename
                    record["fields"][name] = {
                        "shape": list(value.shape),
                        "dtype": str(value.dtype),
                        "state": "normalized",
                    }
                    if not dry_run:
                        torch.save(value, stage / filename)
                if not dry_run:
                    stage.rename(destination)
                    created.append(destination)
                manifest["samples"].append(record)
        if not dry_run:
            save_record(output["root"], version, normalization.record)
            root.mkdir(parents=True, exist_ok=True)
            target = root / f".manifest.{uuid4().hex}.tmp"
            try:
                target.write_text(json.dumps(manifest, indent=2))
                target.replace(manifest_path)
            finally:
                target.unlink(missing_ok=True)
        return manifest_path
    except Exception:
        for path in created + temporary:
            if path.exists():
                shutil.rmtree(path)
        raise
