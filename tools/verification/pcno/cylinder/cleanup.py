"""仅按明确生成清单清理实验产物；不推测路径或删除原始来源。"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def inventory(path: Path) -> tuple[int, str]:
    """冻结目录文件名、内容及符号链接本身，不跟随链接删除或遍历。"""
    size = 0
    digest = hashlib.sha256()
    paths = sorted(path.rglob("*")) if path.is_dir() else [path]
    for item in paths:
        relative = str(item.relative_to(path)) if item != path else item.name
        if item.is_symlink():
            digest.update((relative + "->" + str(item.readlink())).encode())
        elif item.is_file():
            digest.update(relative.encode())
            with item.open("rb") as f:
                digest.update(hashlib.file_digest(f, "sha256").digest())
            size += item.stat().st_size
    return size, digest.hexdigest()


def plan(root: str, generated: list[str], protected: list[str]) -> dict:
    """显式路径集合形成可复核账本，拒绝越界、源目录及保护资产。"""
    root = Path(root).resolve()
    protection = [Path(p).resolve() for p in protected]
    entries = []
    for name in generated:
        path = Path(name).absolute()
        if path.is_symlink() or not path.exists():
            raise ValueError("候选必须是存在的普通路径")
        actual = path.resolve()
        if actual == root or not actual.is_relative_to(root):
            raise ValueError("清理候选越界")
        if any(
            actual == p or actual.is_relative_to(p) or p.is_relative_to(actual) for p in protection
        ):
            raise ValueError("清理候选包含受保护来源或结果")
        if any(
            actual.is_relative_to(Path(e["path"])) or Path(e["path"]).is_relative_to(actual)
            for e in entries
        ):
            raise ValueError("清理候选重叠")
        size, sha = inventory(actual)
        entries.append({"path": str(actual), "bytes": size, "sha256": sha})
    return {"root": str(root), "protected": [str(p) for p in protection], "generated": entries}


def apply(ledger: dict) -> dict:
    """全部候选重新校验通过才执行；仅删除账本逐项路径。"""
    checked = plan(ledger["root"], [e["path"] for e in ledger["generated"]], ledger["protected"])
    if checked != ledger:
        raise ValueError("候选内容自计划后改变，拒绝清理")
    removed = []
    for entry in ledger["generated"]:
        path = Path(entry["path"])
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed.append(entry)
    return {"removed": removed, "reclaimed_bytes": sum(x["bytes"] for x in removed)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    path = Path(args.ledger)
    ledger = json.loads(path.read_text())
    if args.apply:
        report = apply(ledger)
        path.with_name("cleanup-result.json").write_text(json.dumps(report, indent=2) + "\n")
        print(report["reclaimed_bytes"])
    else:
        print(json.dumps(ledger, indent=2))
