"""流式计算资产身份；索引提交仍由运行 writer 独占。"""

import hashlib
import json
from pathlib import Path


def file_inventory(path: str | Path) -> dict[str, str]:
    """按相对位置记录文件摘要，空目录也必须真实存在。"""
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
    result = {}
    for file in files:
        digest = hashlib.sha256()
        with file.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        result[file.name if path.is_file() else file.relative_to(path).as_posix()] = digest.hexdigest()
    return result


def content_digest(path: str | Path) -> str:
    """稳定记录文件集合身份；不读入完整张量。"""
    value = file_inventory(path)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_asset_content(record: dict) -> None:
    """核验资产及全部声明依赖；缺少依赖摘要不视为完整资产。"""
    from ai4e_spec.artifacts.indexes import validate_asset_record

    validate_asset_record(record)
    expected = record.get("dependency_digests", {})
    if not isinstance(expected, dict) or set(expected) != set(record["dependencies"]):
        raise ValueError("asset_dependency_digests_incomplete")
    for path, digest in [(record["path"], record["digest"]), *expected.items()]:
        if content_digest(path) != digest:
            raise ValueError(f"asset_content_changed: {path}")
    if "bundle" in record:
        root = Path(record["bundle"]["root"]).resolve()
        if not root.is_dir() or any(not Path(p).resolve().is_relative_to(root)
                                    for p in [record["path"], *record["dependencies"]]):
            raise ValueError("asset_bundle_members_outside_root")
        if content_digest(root) != record["bundle"]["digest"]:
            raise ValueError("asset_bundle_changed")
